from flask import Flask, render_template, jsonify, request
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

        @self.flask_app.route("/get_filter_options", methods=["GET"])
        def get_filter_options():
            """
            Belirtilen sütuna göre filtreleme seçeneklerini döner.
            """
            column = request.args.get("column")
            allowed_columns = [
                "center_name", "visa_category", "visa_subcategory",
                "source_country", "mission_country"
            ]

            if column not in allowed_columns:
                return jsonify({"error": "Invalid column name"}), 400

            query = f"SELECT DISTINCT {column} FROM unique_appointments ORDER BY {column}"

            try:
                conn = self.db.postgreDb.connect()
                cursor = conn.cursor()
                cursor.execute(query)
                rows = cursor.fetchall()
                options = [row[0] for row in rows if row[0]]
                return jsonify(options)
            except Exception as e:
                print(f"Error fetching filter options: {e}")
                return jsonify({"error":
                                "Failed to fetch filter options"}), 500
            finally:
                cursor.close()
                conn.close()

        @self.flask_app.route("/get_filtered_appointments", methods=["GET"])
        def get_filtered_appointments():
            """
            Filtrelere göre randevu verilerini döner.
            """
            center_name = request.args.get("center_name", default=None)
            visa_category = request.args.get("visa_category", default=None)
            visa_subcategory = request.args.get("visa_subcategory",
                                                default=None)
            source_country = request.args.get("source_country", default=None)
            mission_country = request.args.get("mission_country", default=None)

            query = """
            SELECT ua.id AS unique_appointment_id, ua.center_name, ua.visa_category, ua.visa_subcategory,
                   ua.source_country, ua.mission_country, MAX(al.appointment_date), MAX(al.last_checked), 
                   MAX(al.people_looking), ua.book_now_link
            FROM unique_appointments ua
            LEFT JOIN appointment_logs al ON ua.id = al.unique_appointment_id
            WHERE 1=1
            """
            params = []

            # Dinamik filtreleme
            if center_name:
                query += " AND ua.center_name ILIKE %s"
                params.append(f"%{center_name}%")
            if visa_category:
                query += " AND ua.visa_category ILIKE %s"
                params.append(f"%{visa_category}%")
            if visa_subcategory:
                query += " AND ua.visa_subcategory ILIKE %s"
                params.append(f"%{visa_subcategory}%")
            if source_country:
                query += " AND ua.source_country ILIKE %s"
                params.append(f"%{source_country}%")
            if mission_country:
                query += " AND ua.mission_country ILIKE %s"
                params.append(f"%{mission_country}%")

            query += " GROUP BY ua.id, ua.center_name, ua.visa_category, ua.visa_subcategory, ua.source_country, ua.mission_country"

            try:
                conn = self.db.postgreDb.connect()
                cursor = conn.cursor()
                cursor.execute(query, params)
                rows = cursor.fetchall()

                data = [{
                    "unique_appointment_id": row[0],
                    "center_name": row[1],
                    "visa_category": row[2],
                    "visa_subcategory": row[3],
                    "source_country": row[4],
                    "mission_country": row[5],
                    "appointment_date": row[6],
                    "last_checked": row[7],
                    "people_looking": row[8],
                     "book_now_link": row[9],
                } for row in rows]
                return jsonify(data)
            except Exception as e:
                print(f"Error fetching appointments: {e}")
                return jsonify({"error": "Failed to fetch appointments"}), 500
            finally:
                cursor.close()
                conn.close()

        @self.flask_app.route("/get_appointment_logs", methods=["GET"])
        def get_appointment_logs():
            """
            Bir randevuya ait logların en güncel verilerini döner.
            """
            appointment_id = request.args.get("appointment_id")

            query = """
            SELECT appointment_date, people_looking, last_checked
            FROM appointment_logs
            WHERE unique_appointment_id = %s
            ORDER BY last_checked DESC
            LIMIT 1
            """

            try:
                conn = self.db.postgreDb.connect()
                cursor = conn.cursor()
                cursor.execute(query, (appointment_id, ))
                row = cursor.fetchone()

                if row:
                    data = {
                        "appointment_date": row[0],
                        "people_looking": row[1],
                        "last_checked": row[2],
                    }
                else:
                    data = {
                        "message": "No logs available for this appointment."
                    }

                return jsonify(data)
            except Exception as e:
                print(f"Error fetching logs: {e}")
                return jsonify({"error": "Failed to fetch logs"}), 500
            finally:
                cursor.close()
                conn.close()

        @self.flask_app.route("/get_logs_for_appointment", methods=["GET"])
        def get_logs_for_appointment():
            """
            Belirtilen randevu için son 100 log kaydını döner.
            """
            appointment_id = request.args.get("appointment_id")

            query = """
            SELECT DISTINCT ON (al.appointment_date) al.appointment_date, ua.center_name, al.people_looking, al.last_checked
            FROM appointment_logs al
            JOIN unique_appointments ua ON al.unique_appointment_id = ua.id
            WHERE al.unique_appointment_id = %s and al.appointment_date is not null
            ORDER BY al.appointment_date 
            """

            try:
                conn = self.db.postgreDb.connect()
                cursor = conn.cursor()
                cursor.execute(query, (appointment_id,))
                rows = cursor.fetchall()

                data = [{
                    "appointment_date": row[0],
                    "center_name": row[1],
                    "people_looking": row[2],
                    "last_checked": row[3],
                } for row in rows]

                return jsonify(data)
            except Exception as e:
                print(f"Error fetching logs for appointment: {e}")
                return jsonify({"error": "Failed to fetch logs"}), 500
            finally:
                cursor.close()
                conn.close()


        @self.flask_app.route("/logs_modal", methods=["GET"])
        def logs_modal():
            """
            Belirtilen randevu için logları render eden modal içeriğini döner.
            """
            appointment_id = request.args.get("appointment_id")

            query = """
            SELECT DISTINCT ON (al.appointment_date) al.appointment_date, ua.center_name, al.people_looking, al.last_checked
            FROM appointment_logs al
            JOIN unique_appointments ua ON al.unique_appointment_id = ua.id
            WHERE al.unique_appointment_id = %s AND al.appointment_date IS NOT NULL
            ORDER BY al.appointment_date desc
            """

            try:
                conn = self.db.postgreDb.connect()
                cursor = conn.cursor()
                cursor.execute(query, (appointment_id,))
                rows = cursor.fetchall()

                # Log verilerini listeye dönüştür
                logs = [{
                    "appointment_date": row[0].strftime("%d.%m.%Y, %a"),
                    "center_name": row[1],
                    "people_looking": row[2],
                    "last_checked": row[3].strftime("%d.%m.%Y %H:%M:%S")
                } for row in rows]

                return render_template("logs_modal.html", logs=logs)

            except Exception as e:
                print(f"Error fetching logs for appointment: {e}")
                return "<p>Error fetching logs</p>", 500
            finally:
                cursor.close()
                conn.close()

    def run_flask_app(self):
        self.flask_app.run(host="0.0.0.0", port=8080, debug=False)


app_manager = SchengenCheckerApp()
flask_app = app_manager.flask_app
