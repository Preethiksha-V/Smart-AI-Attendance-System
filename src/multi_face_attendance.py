import os
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3'

import cv2
import time
import pandas as pd
from datetime import datetime
from ultralytics import YOLO
from deepface import DeepFace

# --------------------------------
# PATHS
# --------------------------------

dataset_path = "dataset/student_faces"
attendance_dir = "attendance_logs/face_attendance"

os.makedirs(attendance_dir, exist_ok=True)

today = datetime.now().strftime("%Y-%m-%d")
attendance_file = os.path.join(attendance_dir, f"{today}.csv")

# --------------------------------
# LOAD YOLO MODEL
# --------------------------------

model = YOLO("yolov8n.pt")

# --------------------------------
# CAMERA
# --------------------------------

camera = cv2.VideoCapture(0)

# --------------------------------
# CONTROL VARIABLES
# --------------------------------

marked_students = set()

last_scan = 0
scan_interval = 4

start_time = time.time()
session_duration = 20

# --------------------------------
# CREATE ATTENDANCE FILE
# --------------------------------

if not os.path.exists(attendance_file):

    df = pd.DataFrame(
        columns=["RegNo","Date","Time","Method","Confidence"]
    )

    df.to_csv(attendance_file, index=False)

else:

    df = pd.read_csv(attendance_file)

    if "RegNo" in df.columns:
        marked_students = set(df["RegNo"].values)

print("\nAI Face Attendance Started")
print("Session Duration:", session_duration, "seconds\n")

# --------------------------------
# MAIN LOOP
# --------------------------------

while True:

    ret, frame = camera.read()

    if not ret:
        break

    # --------------------------------
    # YOLO FACE DETECTION
    # --------------------------------

    results = model(frame, conf=0.4)

    faces_detected = 0

    for r in results:

        boxes = r.boxes.xyxy.cpu().numpy()

        for box in boxes:

            faces_detected += 1

            x1, y1, x2, y2 = map(int, box)

            cv2.rectangle(frame,(x1,y1),(x2,y2),(255,255,0),2)

    # --------------------------------
    # FACE RECOGNITION
    # --------------------------------

    if time.time() - last_scan > scan_interval:

        last_scan = time.time()

        for r in results:

            boxes = r.boxes.xyxy.cpu().numpy()

            for box in boxes:

                x1, y1, x2, y2 = map(int, box)

                # Safe crop
                x1 = max(0, x1)
                y1 = max(0, y1)
                x2 = max(0, x2)
                y2 = max(0, y2)

                face = frame[y1:y2, x1:x2]

                if face.size == 0:
                    continue

                try:

                    dfs = DeepFace.find(
                        img_path = face,
                        db_path = dataset_path,
                        model_name = "Facenet",
                        enforce_detection = False,
                        silent = True
                    )

                    if len(dfs) > 0 and len(dfs[0]) > 0:

                        identity = dfs[0].iloc[0]["identity"]

                        reg_no = os.path.basename(os.path.dirname(identity))

                        confidence = (1 - dfs[0].iloc[0]["distance"]) * 100
                        confidence = round(confidence,2)

                        if reg_no not in marked_students:

                            now = datetime.now()

                            date = now.strftime("%Y-%m-%d")
                            time_str = now.strftime("%H:%M:%S")

                            new_row = pd.DataFrame(
                                [[reg_no,date,time_str,"FACE",confidence]],
                                columns=["RegNo","Date","Time","Method","Confidence"]
                            )

                            df = pd.concat([df,new_row],ignore_index=True)

                            df.to_csv(attendance_file,index=False)

                            marked_students.add(reg_no)

                            print("Attendance marked:", reg_no)

                        label = f"{reg_no} {confidence}%"

                        cv2.putText(
                            frame,
                            label,
                            (x1,y1-10),
                            cv2.FONT_HERSHEY_SIMPLEX,
                            0.7,
                            (0,255,0),
                            2
                        )

                except:
                    pass

    # --------------------------------
    # DISPLAY INFO
    # --------------------------------

    cv2.putText(
        frame,
        f"Faces Detected: {faces_detected}",
        (10,30),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.8,
        (0,255,255),
        2
    )

    cv2.imshow("AI Smart Classroom Attendance", frame)

    # --------------------------------
    # AUTO STOP
    # --------------------------------

    if time.time() - start_time > session_duration:

        print("\nAttendance session finished")
        break

    if cv2.waitKey(1) == 27:
        break

# --------------------------------
# CLEANUP
# --------------------------------

camera.release()
cv2.destroyAllWindows()

print("Camera closed")