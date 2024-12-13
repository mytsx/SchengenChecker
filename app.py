from flask import Flask, render_template, jsonify
from database import Database


class SchengenCheckerApp:

    def __init__(self):

        # Database nesnesi
        self.db = Database()

        # Flask uygulaması
        self.flask_app = Flask(__name__)
        self.add_flask_routes()

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


app_manager = SchengenCheckerApp()
flask_app = app_manager.flask_app
