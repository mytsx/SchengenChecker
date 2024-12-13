
from flask import Flask, render_template, jsonify
import threading
import time
from replit import db

# Flask app setup
app = Flask(__name__)

@app.route("/")
def home():
    return render_template("home.html")

@app.route("/get_logs")
def get_logs():
    logs = db.get("logs", [])
    logs_formatted = [(log["timestamp"], log["message"]) for log in logs]
    return jsonify({"logs": logs_formatted, "recent_appointments": []})

if __name__ == "__main__":
    def flask_app():
        app.run(host="0.0.0.0", port=8080, debug=False)

    threading.Thread(target=flask_app).start()

    while True:
        time.sleep(1)
