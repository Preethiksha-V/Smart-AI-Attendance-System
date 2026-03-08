import qrcode
import time
import random
import os

os.makedirs("src/static", exist_ok=True)

while True:

    token = str(random.randint(100000,999999))

    # save token for verification
    with open("src/static/token.txt","w") as f:
        f.write(token)

    qr = qrcode.make("http://192.168.73.104:5000/scan?token="+token)

    qr.save("src/static/attendance_qr.png")

    print("New QR Token:", token)

    time.sleep(10)   # QR changes every 10 seconds