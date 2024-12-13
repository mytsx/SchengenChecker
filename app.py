# app.py - Flask Application
from flask import Flask, render_template_string
import sqlite3

# Flask app setup
app = Flask(__name__)

# Database connection
DB_FILE = "logs.db"
conn = sqlite3.connect(DB_FILE, check_same_thread=False)
cursor = conn.cursor()


@app.route("/")
def home():
    # Fetch logs from database
    cursor.execute(
        "SELECT timestamp, message FROM logs ORDER BY id DESC LIMIT 100")
    logs = cursor.fetchall()

    # Separate important messages (e.g., appointments found)
    appointments = [log for log in logs if "Randevu" in log[1]]
    other_logs = [log for log in logs if "Randevu" not in log[1]]

    # HTML template
    html_template = """
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Schengen Visa Logs</title>
        <style>
            body { font-family: Arial, sans-serif; margin: 20px; }
            h1 { color: #333; }
            .appointments { background-color: #e7f4e4; padding: 10px; margin-bottom: 20px; border: 1px solid #a4d4a2; }
            .logs { background-color: #f9f9f9; padding: 10px; border: 1px solid #ddd; }
            .log { margin-bottom: 5px; }
            .timestamp { color: #888; font-size: 0.9em; }
        </style>
    </head>
    <body>
        <h1>Schengen Visa Appointment Logs</h1>

        <div class="appointments">
            <h2>Found Appointments</h2>
            {% if appointments %}
                {% for log in appointments %}
                    <div class="log">
                        <span class="timestamp">{{ log[0] }}</span>: {{ log[1] }}
                    </div>
                {% endfor %}
            {% else %}
                <p>No appointments found.</p>
            {% endif %}
        </div>

        <div class="logs">
            <h2>All Logs</h2>
            {% for log in other_logs %}
                <div class="log">
                    <span class="timestamp">{{ log[0] }}</span>: {{ log[1] }}
                </div>
            {% endfor %}
        </div>
    </body>
    </html>
    """
    return render_template_string(html_template,
                                  appointments=appointments,
                                  other_logs=other_logs)


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080, debug=False)
