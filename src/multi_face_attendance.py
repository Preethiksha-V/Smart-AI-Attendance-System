import os
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3'

import cv2
import time
import pandas as pd
from datetime import datetime
from ultralytics import YOLO
from deepface import DeepFace

# Paths
dataset_path = "dataset/student_faces"
attendance_file = "attendance_logs/attendance.csv"

# Load YOLO model
model = YOLO("yolov8n.pt")

# Camera
camera = cv2.VideoCapture(0)

# Attendance control
marked_students = []

# Recognition control
last_scan = 0
scan_interval = 3

# Auto stop timer
start_time = time.time()
session_duration = 30

# Ensure attendance file exists
os.makedirs("attendance_logs", exist_ok=True)

if not os.path.exists(attendance_file):
    df = pd.DataFrame(columns=["Name","Date","Time"])
    df.to_csv(attendance_file,index=False)

print("Smart AI Attendance System Started")

while True:

    ret, frame = camera.read()
    if not ret:
        break

    # YOLO detection
    results = model(frame, conf=0.4)

    # Draw boxes for detected faces
    for r in results:
        boxes = r.boxes.xyxy.cpu().numpy()

        for box in boxes:

            x1, y1, x2, y2 = map(int, box)

            cv2.rectangle(frame,(x1,y1),(x2,y2),(255,255,0),2)

    # Run recognition every few seconds
    if time.time() - last_scan > scan_interval:

        last_scan = time.time()

        for r in results:
            boxes = r.boxes.xyxy.cpu().numpy()

            for box in boxes:

                x1, y1, x2, y2 = map(int, box)

                face = frame[y1:y2, x1:x2]

                try:

                    dfs = DeepFace.find(
                        img_path=face,
                        db_path=dataset_path,
                        model_name="Facenet",
                        enforce_detection=False
                    )

                    if len(dfs) > 0 and len(dfs[0]) > 0:

                        identity = dfs[0].iloc[0]["identity"]
                        name = identity.split("\\")[-2]

                        # Mark attendance once
                        if name not in marked_students:

                            now = datetime.now()
                            date = now.strftime("%Y-%m-%d")
                            time_str = now.strftime("%H:%M:%S")

                            df = pd.read_csv(attendance_file)

                            new_row = pd.DataFrame(
                                [[name,date,time_str]],
                                columns=["Name","Date","Time"]
                            )

                            df = pd.concat([df,new_row])
                            df.to_csv(attendance_file,index=False)

                            marked_students.append(name)

                            print("Attendance marked:", name)

                        cv2.putText(frame,name,(x1,y1-10),
                                    cv2.FONT_HERSHEY_SIMPLEX,
                                    0.7,(0,255,0),2)

                except:
                    pass

    cv2.imshow("Smart Classroom AI Attendance",frame)

    # Auto stop after session time
    if time.time() - start_time > session_duration:
        print("Attendance session finished")
        break

    if cv2.waitKey(1) == 27:
        break

camera.release()
cv2.destroyAllWindows()