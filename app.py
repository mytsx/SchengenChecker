from flask import Flask, render_template, jsonify
from threading import Thread
from database import Database
from schengen_checker import SchengenChecker
import logging
import json
import time


class ApplicationManager:

    def __init__(self, config_file="config.json"):
        # Config dosyasını yükle
        self.config = self.load_config(config_file)

        # Database nesnesi
        self.db = Database()

        # Logger ayarları
        self.setup_logger()

        # SchengenChecker nesnesi
        self.schengen_checker = SchengenChecker(self.config,
                                                self.control_logger, self.db)

        # Flask uygulaması
        self.flask_app = Flask(__name__)
        self.add_flask_routes()

    def load_config(self, config_file):
        try:
            with open(config_file, "r", encoding="utf-8") as file:
                return json.load(file)
        except FileNotFoundError:
            print(f"{config_file} bulunamadı. Lütfen oluşturun.")
            exit(1)
        except json.JSONDecodeError:
            print(
                f"{config_file} dosyasında bir hata var. Lütfen kontrol edin.")
            exit(1)

    def setup_logger(self):
        logging.basicConfig(
            filename="appointment_logs.txt",
            level=logging.INFO,
            format="%(asctime)s - %(levelname)s - %(message)s",
            encoding="utf-8",
            datefmt="%Y-%m-%d %H:%M:%S",
        )
        self.control_logger = logging.getLogger("control_logger")
        control_handler = logging.FileHandler("control_times.txt",
                                              encoding="utf-8")
        control_handler.setFormatter(
            logging.Formatter("%(asctime)s - %(message)s"))
        self.control_logger.addHandler(control_handler)
        self.control_logger.setLevel(logging.INFO)

    def add_flask_routes(self):

        @self.flask_app.route("/")
        def home():
            return render_template("home.html")

        @self.flask_app.route("/get_recent_appointments")
        def get_recent_appointments():
            data = self.db.fetch_table_data("appointments", 10)
            return jsonify(data)

        @self.flask_app.route("/get_responses")
        def get_responses():
            data = self.db.fetch_table_data("responses", 10, json_column=True)
            return jsonify(data)

        @self.flask_app.route("/get_logs")
        def get_logs():
            data = self.db.fetch_table_data("logs", 100)
            return jsonify(data)

    def run_flask_app(self):
        self.flask_app.run(host="0.0.0.0", port=8080, debug=False)

    def run_schengen_checker(self):
        while True:
            self.schengen_checker.check_appointments()
            time.sleep(self.config.get("check_interval", 600))


if __name__ == "__main__":
    app_manager = ApplicationManager()

    # Flask'i ayrı bir thread'de çalıştır
    flask_thread = Thread(target=app_manager.run_flask_app)
    flask_thread.start()

    # SchengenChecker'ı çalıştır
    app_manager.run_schengen_checker()
