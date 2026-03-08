from flask import Flask, request, render_template
import pandas as pd
from datetime import datetime
import socket

app = Flask(__name__)

attendance_file = "attendance_logs/attendance.csv"

# allowed wifi network
ALLOWED_WIFI = "VIT_WIFI"

@app.route("/")
def home():
    return render_template("scan.html")

@app.route("/scan", methods=["GET","POST"])
def scan():

    token = request.args.get("token")

    with open("src/static/token.txt") as f:
        valid_token = f.read()

    if token != valid_token:
        return "QR expired. Scan again."

    if request.method == "POST":

        student = request.form.get("student")

        ip = request.remote_addr

        # wifi verification (basic)
        hostname = socket.gethostname()

        now = datetime.now()
        date = now.strftime("%Y-%m-%d")
        time = now.strftime("%H:%M:%S")

        df = pd.read_csv(attendance_file)

        # prevent duplicate
        if student in df["Name"].values:
            return "Attendance already marked"

        new_row = pd.DataFrame([[student,date,time]],
                               columns=["Name","Date","Time"])

        df = pd.concat([df,new_row])
        df.to_csv(attendance_file,index=False)

        return "Attendance marked for "+student

    return render_template("submit.html")
    

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)