from flask import Flask, render_template, jsonify, g
import json
import psycopg2

# Flask app setup
app = Flask(__name__)

# PostgreSQL bağlantı ayarlarını dosyadan yükleyin
try:
    with open("postgreconfig.json", "r") as config_file:
        DATABASE_CONFIG = json.load(config_file)
except FileNotFoundError:
    print(
        "postgreconfig.json dosyası bulunamadı. Lütfen oluşturun ve gerekli bilgileri ekleyin."
    )
    exit(1)
except json.JSONDecodeError:
    print("postgreconfig.json dosyasında bir hata var. Lütfen kontrol edin.")
    exit(1)


def get_db_connection():
    """Her istekte yeni bir veritabanı bağlantısı oluştur."""
    if "db" not in g:
        g.db = psycopg2.connect(**DATABASE_CONFIG)
        g.cursor = g.db.cursor()
    return g.cursor


@app.teardown_appcontext
def close_db_connection(exception=None):
    """İstek tamamlandığında veritabanı bağlantısını kapat."""
    db = g.pop("db", None)
    if db is not None:
        db.close()


@app.route("/")
def home():
    return render_template("home.html")


@app.route("/get_recent_appointments")
def get_recent_appointments():
    cursor = get_db_connection()
    cursor.execute(
        "SELECT timestamp, message FROM appointments ORDER BY timestamp DESC LIMIT 10"
    )
    appointments = cursor.fetchall()
    appointments_formatted = [{
        "timestamp": app[0],
        "message": app[1]
    } for app in appointments]
    return jsonify(appointments_formatted)


@app.route("/get_responses")
def get_responses():
    cursor = get_db_connection()
    cursor.execute(
        "SELECT timestamp, response FROM responses ORDER BY timestamp DESC LIMIT 10"
    )
    responses = cursor.fetchall()
    responses_formatted = [{
        "timestamp": res[0],
        "response": res[1]
    } for res in responses]
    return jsonify(responses_formatted)


@app.route("/get_logs")
def get_logs():
    cursor = get_db_connection()
    cursor.execute(
        "SELECT timestamp, message FROM logs ORDER BY timestamp DESC LIMIT 100"
    )
    logs = cursor.fetchall()
    logs_formatted = [{"timestamp": log[0], "message": log[1]} for log in logs]
    return jsonify(logs_formatted)


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080, debug=False)
