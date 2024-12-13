from flask import Flask, render_template, jsonify
import sqlite3
import threading
import time

# Flask app setup
app = Flask(__name__)

# Database connection
DB_FILE = "logs.db"
conn = sqlite3.connect(DB_FILE, check_same_thread=False)
cursor = conn.cursor()


@app.route("/")
def home():
    return render_template("home.html")


@app.route("/get_logs")
def get_logs():
    # Fetch logs from database
    cursor.execute(
        "SELECT timestamp, message FROM logs ORDER BY id DESC LIMIT 100")
    logs = cursor.fetchall()

    # Fetch the last 5 appointments from a separate table
    cursor.execute(
        "SELECT timestamp, message FROM appointments ORDER BY id DESC LIMIT 5")
    recent_appointments = cursor.fetchall()

    return jsonify({"logs": logs, "recent_appointments": recent_appointments})


if __name__ == "__main__":

    def flask_app():
        app.run(host="0.0.0.0", port=8080, debug=False)

    threading.Thread(target=flask_app).start()

    # Keep the main thread alive
    while True:
        time.sleep(1)
