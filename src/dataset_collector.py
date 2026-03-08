import cv2
import os

student_name = input("Enter Student Name: ")
student_id = input("Enter Student ID: ")

path = f"dataset/student_faces/{student_name}_{student_id}"

os.makedirs(path, exist_ok=True)

camera = cv2.VideoCapture(0)

count = 0

while True:

    ret, frame = camera.read()
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

    face_cascade = cv2.CascadeClassifier(
        cv2.data.haarcascades + "haarcascade_frontalface_default.xml"
    )

    faces = face_cascade.detectMultiScale(gray, 1.3, 5)

    for (x, y, w, h) in faces:

        face = frame[y:y+h, x:x+w]

        file_name = f"{path}/img_{count}.jpg"

        cv2.imwrite(file_name, face)

        count += 1

        cv2.rectangle(frame, (x,y),(x+w,y+h),(0,255,0),2)

    cv2.imshow("Capturing Faces", frame)

    if count >= 30:
        break

    if cv2.waitKey(1) == 27:
        break

camera.release()
cv2.destroyAllWindows()

print("Dataset collection completed")