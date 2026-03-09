from flask import Flask, request, render_template
import pandas as pd
from datetime import datetime
import os

app = Flask(__name__)

# ---------------------------
# Paths
# ---------------------------

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

TOKEN_PATH = os.path.join(BASE_DIR, "static", "token.txt")

ATTENDANCE_DIR = os.path.join(BASE_DIR, "attendance_logs", "qr_attendance")

STUDENT_FILE = os.path.join(BASE_DIR, "students.csv")

# Create attendance folder
os.makedirs(ATTENDANCE_DIR, exist_ok=True)

# ---------------------------
# WIFI restriction
# ---------------------------

ALLOWED_NETWORK = "192.168"

# ---------------------------
# Load students list
# ---------------------------

students_df = pd.read_csv(STUDENT_FILE)

# ---------------------------
# HOME PAGE
# ---------------------------

@app.route("/")
def home():
    return render_template("scan.html")


# ---------------------------
# QR SCAN
# ---------------------------

@app.route("/scan", methods=["GET","POST"])
def scan():

    if not os.path.exists(TOKEN_PATH):
        return "QR generator not running."

    with open(TOKEN_PATH) as f:
        valid_token = f.read().strip()

    token = request.args.get("token")

    if token != valid_token:
        return "QR expired. Scan again."

    if request.method == "POST":

        student = request.form.get("student").strip()

        now = datetime.now()

        date = now.strftime("%Y-%m-%d")

        time = now.strftime("%H:%M:%S")

        client_ip = request.remote_addr

        # ---------------------------
        # WIFI check
        # ---------------------------

        if not client_ip.startswith(ALLOWED_NETWORK):
            return "Connect to seminar hall WiFi."

        # ---------------------------
        # student validation
        # ---------------------------

        if student not in students_df["ID"].values:
             return "Invalid registration number"

        # ---------------------------
        # today's attendance file
        # ---------------------------

        ATTENDANCE_FILE = os.path.join(
            ATTENDANCE_DIR,
            f"{date}.csv"
        )

        if not os.path.exists(ATTENDANCE_FILE):

            df = pd.DataFrame(
                columns=["Name","Date","Time","IP"]
            )

            df.to_csv(ATTENDANCE_FILE,index=False)

        df = pd.read_csv(ATTENDANCE_FILE)

        # ---------------------------
        # prevent duplicate student
        # ---------------------------

        if student in df["Name"].values:
            return "Attendance already marked today"

        # ---------------------------
        # prevent same device multiple
        # ---------------------------

        if client_ip in df["IP"].values:
            return "This device already submitted today"

        # ---------------------------
        # store attendance
        # ---------------------------

        new_row = pd.DataFrame(
            [[student,date,time,client_ip]],
            columns=["Name","Date","Time","IP"]
        )

        df = pd.concat([df,new_row], ignore_index=True)

        df.to_csv(ATTENDANCE_FILE,index=False)

        return f"Attendance marked for {student}"

    return render_template("submit.html")


# ---------------------------
# FACULTY DASHBOARD
# ---------------------------

@app.route("/dashboard")
def dashboard():

    today = datetime.now().strftime("%Y-%m-%d")

    ATTENDANCE_FILE = os.path.join(
        ATTENDANCE_DIR,
        f"{today}.csv"
    )

    if os.path.exists(ATTENDANCE_FILE):

        df = pd.read_csv(ATTENDANCE_FILE)

    else:

        df = pd.DataFrame(
            columns=["Name","Date","Time","IP"]
        )

    total_students = len(students_df)

    present = len(df)

    absent = total_students - present

    attendance_percent = round(
        (present/total_students)*100,2
    )

    records = df.to_dict(orient="records")

    return render_template(
        "dashboard.html",
        total_students=total_students,
        present=present,
        absent=absent,
        percent=attendance_percent,
        records=records
    )


# ---------------------------
# RUN SERVER
# ---------------------------

if __name__ == "__main__":

    app.run(host="0.0.0.0", port=5000)