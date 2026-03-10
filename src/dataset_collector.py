import cv2
import os

# -----------------------------
# INPUT
# -----------------------------

reg_no = input("Enter Student RegNo (example 23MIS0001): ").strip().upper()

dataset_dir = "dataset/student_faces"
student_path = os.path.join(dataset_dir, reg_no)

os.makedirs(student_path, exist_ok=True)

print("\nCollecting dataset for:", reg_no)
print("Press ESC to stop early\n")

# -----------------------------
# CAMERA
# -----------------------------

camera = cv2.VideoCapture(0)

# -----------------------------
# FACE DETECTOR
# -----------------------------

face_cascade = cv2.CascadeClassifier(
    cv2.data.haarcascades + "haarcascade_frontalface_default.xml"
)

count = 0
max_images = 30

# -----------------------------
# CAPTURE LOOP
# -----------------------------

while True:

    ret, frame = camera.read()

    if not ret:
        break

    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

    faces = face_cascade.detectMultiScale(gray, 1.3, 5)

    for (x, y, w, h) in faces:

        face = frame[y:y+h, x:x+w]

        # resize for consistency
        face = cv2.resize(face, (160,160))

        file_name = os.path.join(student_path, f"img_{count}.jpg")

        cv2.imwrite(file_name, face)

        count += 1

        cv2.rectangle(frame, (x,y),(x+w,y+h),(0,255,0),2)

        cv2.putText(
            frame,
            f"Images: {count}/{max_images}",
            (10,30),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.8,
            (0,255,0),
            2
        )

    cv2.imshow("Dataset Collection - Smart AI Attendance", frame)

    if count >= max_images:
        break

    if cv2.waitKey(1) == 27:
        break

# -----------------------------
# CLEANUP
# -----------------------------

camera.release()
cv2.destroyAllWindows()

print("\nDataset collection completed")
print("Saved to:", student_path)