import cv2
from deepface import DeepFace
import pandas as pd
from datetime import datetime
import os

dataset_path = "dataset/student_faces"
attendance_file = "attendance_logs/attendance.csv"

os.makedirs("attendance_logs", exist_ok=True)

if not os.path.exists(attendance_file):
    df = pd.DataFrame(columns=["Name","Date","Time"])
    df.to_csv(attendance_file,index=False)

marked_students = []

camera = cv2.VideoCapture(0)

while True:

    ret, frame = camera.read()
    if not ret:
        break

    try:

        dfs = DeepFace.find(
            img_path=frame,
            db_path=dataset_path,
            model_name="Facenet",
            enforce_detection=False
        )

        if len(dfs) > 0 and len(dfs[0]) > 0:

            identity = dfs[0].iloc[0]["identity"]

            name = identity.split("\\")[-2]

            if name not in marked_students:

                now = datetime.now()
                date = now.strftime("%Y-%m-%d")
                time = now.strftime("%H:%M:%S")

                df = pd.read_csv(attendance_file)

                new_row = pd.DataFrame([[name,date,time]],
                                       columns=["Name","Date","Time"])

                df = pd.concat([df,new_row])

                df.to_csv(attendance_file,index=False)

                marked_students.append(name)

                print("Attendance marked for:",name)

    except:
        pass

    cv2.imshow("Smart AI Attendance System",frame)

    if cv2.waitKey(1) == 27:
        break

camera.release()
cv2.destroyAllWindows()