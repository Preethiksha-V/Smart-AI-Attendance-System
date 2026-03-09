import os
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3'

import cv2
import time
import pandas as pd
from datetime import datetime
from ultralytics import YOLO
from deepface import DeepFace

# ------------------------------
# PATHS
# ------------------------------

dataset_path = "dataset/student_faces"
attendance_dir = "attendance_logs/face_attendance"

os.makedirs(attendance_dir, exist_ok=True)

# today's attendance file
today = datetime.now().strftime("%Y-%m-%d")
attendance_file = os.path.join(attendance_dir, f"{today}.csv")

# ------------------------------
# LOAD YOLO MODEL
# ------------------------------

model = YOLO("yolov8n.pt")

# ------------------------------
# CAMERA
# ------------------------------

camera = cv2.VideoCapture(0)

# ------------------------------
# CONTROL VARIABLES
# ------------------------------

marked_students = set()

last_scan = 0
scan_interval = 4   # seconds between AI scans

# session timer
start_time = time.time()
session_duration = 20   # seconds camera stays open

# ------------------------------
# CREATE ATTENDANCE FILE
# ------------------------------

if not os.path.exists(attendance_file):

    df = pd.DataFrame(columns=["Name","Date","Time"])
    df.to_csv(attendance_file, index=False)

else:
    df = pd.read_csv(attendance_file)
    marked_students = set(df["Name"].values)

print("\nAI Smart Attendance Started")
print("Session Duration:", session_duration, "seconds\n")

# ------------------------------
# MAIN LOOP
# ------------------------------

while True:

    ret, frame = camera.read()

    if not ret:
        break

    # ------------------------------
    # YOLO FACE DETECTION
    # ------------------------------

    results = model(frame, conf=0.4)

    for r in results:

        boxes = r.boxes.xyxy.cpu().numpy()

        for box in boxes:

            x1, y1, x2, y2 = map(int, box)

            cv2.rectangle(frame,(x1,y1),(x2,y2),(255,255,0),2)

    # ------------------------------
    # RUN FACE RECOGNITION
    # ------------------------------

    if time.time() - last_scan > scan_interval:

        last_scan = time.time()

        for r in results:

            boxes = r.boxes.xyxy.cpu().numpy()

            for box in boxes:

                x1, y1, x2, y2 = map(int, box)

                # safe crop
                face = frame[max(0,y1):max(0,y2), max(0,x1):max(0,x2)]

                if face.size == 0:
                    continue

                try:

                    dfs = DeepFace.find(
                        img_path=face,
                        db_path=dataset_path,
                        model_name="Facenet",
                        enforce_detection=False,
                        silent=True
                    )

                    if len(dfs) > 0 and len(dfs[0]) > 0:

                        identity = dfs[0].iloc[0]["identity"]

                        name = os.path.basename(os.path.dirname(identity))

                        # ------------------------------
                        # MARK ATTENDANCE
                        # ------------------------------

                        if name not in marked_students:

                            now = datetime.now()

                            date = now.strftime("%Y-%m-%d")
                            time_str = now.strftime("%H:%M:%S")

                            df = pd.read_csv(attendance_file)

                            new_row = pd.DataFrame(
                                [[name,date,time_str]],
                                columns=["Name","Date","Time"]
                            )

                            df = pd.concat([df,new_row], ignore_index=True)

                            df.to_csv(attendance_file, index=False)

                            marked_students.add(name)

                            print("Attendance marked:", name)

                        cv2.putText(
                            frame,
                            name,
                            (x1,y1-10),
                            cv2.FONT_HERSHEY_SIMPLEX,
                            0.7,
                            (0,255,0),
                            2
                        )

                except Exception as e:
                    pass

    # ------------------------------
    # DISPLAY WINDOW
    # ------------------------------

    cv2.imshow("AI Smart Classroom Attendance", frame)

    # ------------------------------
    # AUTO STOP SESSION
    # ------------------------------

    if time.time() - start_time > session_duration:

        print("\nAttendance session completed")
        break

    if cv2.waitKey(1) == 27:
        break


# ------------------------------
# CLEANUP
# ------------------------------

camera.release()
cv2.destroyAllWindows()

print("Camera closed")