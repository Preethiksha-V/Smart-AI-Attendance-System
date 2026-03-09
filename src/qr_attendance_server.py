from flask import Flask, request, render_template
import pandas as pd
from datetime import datetime
import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
TOKEN_PATH = os.path.join(BASE_DIR, "static", "token.txt")


app = Flask(__name__)

attendance_file = "attendance_logs/attendance.csv"

ALLOWED_NETWORK = "192.168"

if not os.path.exists(attendance_file):
    df = pd.DataFrame(columns=["Name","Date","Time","IP"])
    df.to_csv(attendance_file,index=False)


@app.route("/")
def home():
    return render_template("scan.html")


@app.route("/scan", methods=["GET","POST"])
def scan():

    import os

    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
    TOKEN_PATH = os.path.join(BASE_DIR, "static", "token.txt")

    if not os.path.exists(TOKEN_PATH):
        return "QR generator not started yet. Please wait."

    with open(TOKEN_PATH) as f:
        valid_token = f.read().strip()

    token = request.args.get("token")

    if token != valid_token:
        return "QR expired. Please scan again."

    if request.method == "POST":

        student = request.form.get("student")

        now = datetime.now()
        date = now.strftime("%Y-%m-%d")
        time = now.strftime("%H:%M:%S")

        df = pd.read_csv(attendance_file)

        if student in df["Name"].values:
            return "Attendance already marked"

        new_row = pd.DataFrame([[student,date,time]],
                               columns=["Name","Date","Time"])

        df = pd.concat([df,new_row])

        df.to_csv(attendance_file,index=False)

        return f"Attendance marked for {student}"

    return render_template("submit.html")

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)