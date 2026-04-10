from flask import Flask, request
from twilio.rest import Client
import pandas as pd
import time
import threading
import csv
from datetime import datetime

app = Flask(__name__)

# 🔐 IMPORTANT: replace with NEW credentials after rotating token
ACCOUNT_SID = ""
AUTH_TOKEN = ""
TWILIO_NUMBER = ""

client = Client(ACCOUNT_SID, AUTH_TOKEN)


# ---------- DIALER ----------
import threading
import time

def make_call(number):
    try:
        print("Calling:", number)

        call = client.calls.create(
            to=str(number),
            from_=TWILIO_NUMBER,
            timeout=15,  # ⏱️ stops ringing after 15s
            twiml="""
            <Response>
                <Say voice="Polly.Matthew">
                    <prosody rate="1">
                            Hi, this is Eddy from Greenopia outreach. We are connecting you to a representative now
                    </prosody>
                </Say>
                <Pause length="0.5"/>
                <Dial>+13107173687</Dial>
            </Response>
            """
        )

        print("Queued:", call.sid)

    except Exception as e:
        print("ERROR:", e)


def dial_numbers():
    df = pd.read_csv("leads.csv")
    df.columns = df.columns.str.strip().str.lower()

    for number in df["phone"]:
        threading.Thread(target=make_call, args=(number,)).start()
        time.sleep(1)  # small delay to avoid rate limits


# ---------- OPTIONAL CALLBACK TRACKING ----------
@app.route("/callback", methods=["POST"])
def callback():
    number = request.form.get("From")
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    print("CALLBACK:", number, timestamp)

    # file name
    file_name = "callbacks.csv"

    # check if file exists
    file_exists = False
    try:
        with open(file_name, "r"):
            file_exists = True
    except FileNotFoundError:
        file_exists = False

    # write to CSV
    with open(file_name, "a", newline="") as file:
        writer = csv.writer(file)

        # write header if file is new
        if not file_exists:
            writer.writerow(["phone", "timestamp", "status"])

        # write row
        writer.writerow([number, timestamp, "callback"])

    return "OK"


# ---------- MAIN ----------
if __name__ == "__main__":
    dial_numbers()
