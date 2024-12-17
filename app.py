from flask import Flask, render_template, jsonify,request
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

        @self.flask_app.route("/log")
        def log():
            return render_template("log.html")


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

        @self.flask_app.route("/get_filtered_appointments", methods=["GET"])
        def get_filtered_appointments():
            """
            unique_appointments ve appointment_logs tablolarından filtrelenmiş verileri döner.
            """
            center_name = request.args.get("center_name", default=None)
            visa_category = request.args.get("visa_category", default=None)
            appointment_date = request.args.get("appointment_date", default=None)

            query = """
            SELECT ua.center_name, ua.visa_category, ua.visa_subcategory, 
                ua.source_country, ua.mission_country, al.appointment_date, 
                al.people_looking, al.last_checked
            FROM unique_appointments ua
            LEFT JOIN appointment_logs al ON ua.id = al.unique_appointment_id
            WHERE 1=1
            """
            params = []

            if center_name:
                query += " AND ua.center_name ILIKE %s"
                params.append(f"%{center_name}%")
            if visa_category:
                query += " AND ua.visa_category ILIKE %s"
                params.append(f"%{visa_category}%")
            if appointment_date:
                query += " AND al.appointment_date = %s"
                params.append(appointment_date)

            query += " ORDER BY al.last_checked DESC LIMIT 100"

            try:
                conn = self.db.postgreDb.connect()
                cursor = conn.cursor()
                cursor.execute(query, params)
                rows = cursor.fetchall()

                data = [
                    {
                        "center_name": row[0],
                        "visa_category": row[1],
                        "visa_subcategory": row[2],
                        "source_country": row[3],
                        "mission_country": row[4],
                        "appointment_date": row[5],
                        "people_looking": row[6],
                        "last_checked": row[7],
                    }
                    for row in rows
                ]
                return jsonify(data)
            except Exception as e:
                print(f"Error fetching filtered appointments: {e}")
                return jsonify({"error": "Veriler getirilirken hata oluştu."})
            finally:
                cursor.close()
                conn.close()





    def run_flask_app(self):
        self.flask_app.run(host="0.0.0.0", port=8080, debug=False)


app_manager = SchengenCheckerApp()
flask_app = app_manager.flask_app
