import qrcode
import time
import os
import secrets

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
STATIC_DIR = os.path.join(BASE_DIR, "static")

token_path = os.path.join(STATIC_DIR, "token.txt")
qr_path = os.path.join(STATIC_DIR, "attendance_qr.png")
# ensure folder exists
os.makedirs(STATIC_DIR, exist_ok=True)

SERVER_IP = "192.168.73.104"
PORT = "5000"

while True:

    token = secrets.token_hex(4)

    token_path = os.path.join(STATIC_DIR, "token.txt")
    qr_path = os.path.join(STATIC_DIR, "attendance_qr.png")

    with open(token_path, "w") as f:
        f.write(token)

    url = f"http://{SERVER_IP}:{PORT}/scan?token={token}"

    qr = qrcode.make(url)
    qr.save(qr_path)

    print("New QR Token:", token)

    time.sleep(20)