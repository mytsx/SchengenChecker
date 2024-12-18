import psycopg2
import json
import pytz
from datetime import datetime
from config_loader import ConfigLoader, ConfigWrapper
from telegram_bot import TelegramBot


class PostgresDatabase:

    def __init__(self):
        database_config_data = ConfigLoader.load_config("postgres.json")
        self.config = ConfigWrapper(database_config_data).config_data
        self.telegramBot = TelegramBot()

    def connect(self):
        try:
            return psycopg2.connect(**self.config)
        except psycopg2.OperationalError as e:
            print(f"PostgreSQL bağlantısı başarısız: {e}")
            raise

    def get_table_schema(self, table_name):
        """PostgreSQL'den tablo şemasını alır."""
        query = f"""
        SELECT column_name, data_type
        FROM information_schema.columns
        WHERE table_name = '{table_name}' AND table_schema = 'public';
        """
        try:
            conn = self.connect()
            cursor = conn.cursor()
            cursor.execute(query)
            schema = cursor.fetchall()
            cursor.close()
            conn.close()
            return schema
        except Exception as e:
            print(f"PostgreSQL'den şema alınırken hata: {e}")
            return []

    def get_all_table_names(self):
        """PostgreSQL'den tüm tablo isimlerini alır."""
        query = """
        SELECT table_name
        FROM information_schema.tables
        WHERE table_schema = 'public' AND table_type = 'BASE TABLE';
        """
        try:
            conn = self.connect()
            cursor = conn.cursor()
            cursor.execute(query)
            tables = [row[0] for row in cursor.fetchall()]
            cursor.close()
            conn.close()
            return tables
        except Exception as e:
            print(f"PostgreSQL'den tablo isimleri alınırken hata: {e}")
            return []

    def log_to_table(self, table_name, data):
        """Logs data into a PostgreSQL table and triggers additional actions for `responses`."""
        tz = pytz.timezone("Europe/Istanbul")
        timestamp = datetime.now(tz).strftime("%Y-%m-%d %H:%M:%S")
        try:
            conn = self.connect()
            cursor = conn.cursor()

            # Insert data into the specified table
            if table_name == "responses":
                cursor.execute(
                    f"INSERT INTO {table_name} (timestamp, response) VALUES (%s, %s)",
                    (timestamp, json.dumps(data)))
                conn.commit()

                # Process the inserted response for unique appointments and logs
                self._process_response_for_appointments(data)

            elif table_name in ["logs", "appointments"]:
                cursor.execute(
                    f"INSERT INTO {table_name} (timestamp, message) VALUES (%s, %s)",
                    (timestamp, data))
                conn.commit()

        except Exception as e:
            print(f"PostgreSQL'e kayıt sırasında hata: {e}")
        finally:
            cursor.close()
            conn.close()

    def fetch_responses_from_postgres(self, limit=500):
        """
        Fetch JSON responses from the 'responses' table in PostgreSQL.
        """
        query = "SELECT timestamp, response FROM responses ORDER BY id DESC LIMIT %s"
        try:
            conn = self.connect()
            cursor = conn.cursor()
            cursor.execute(query, (limit, ))
            rows = cursor.fetchall()
            response_list = []

            for row in rows:
                timestamp, response_data = row
                if isinstance(response_data, str):  # Parse JSON string
                    response_data = json.loads(response_data)

                if isinstance(response_data, list):
                    for record in response_data:
                        response_list.append({
                            "timestamp": timestamp,
                            **record
                        })
                else:
                    response_list.append({
                        "timestamp": timestamp,
                        "data": response_data
                    })

            return response_list
        except Exception as e:
            print(f"Error fetching responses from PostgreSQL: {e}")
            return []
        finally:
            cursor.close()
            conn.close()

    def fetch_or_create_unique_appointment(self,
                                        visa_type_id,
                                        center_name,
                                        book_now_link,
                                        visa_category,
                                        visa_subcategory,
                                        source_country,
                                        mission_country,
                                        appointment_date=None):
        """
        Check or create a unique appointment in PostgreSQL using UPSERT.
        """
        try:
            conn = self.connect()
            cursor = conn.cursor()

            # UPSERT sorgusu
            query_upsert = """
            INSERT INTO unique_appointments (
                visa_type_id, center_name, visa_category, visa_subcategory,
                source_country, mission_country, book_now_link
            ) VALUES (%s, %s, %s, %s, %s, %s, %s)
            ON CONFLICT ON CONSTRAINT unique_visa_appointment DO NOTHING
            RETURNING id;
            """
            cursor.execute(
                query_upsert,
                (visa_type_id, center_name, visa_category, visa_subcategory,
                source_country, mission_country, book_now_link)
            )

            # Eğer yeni bir kayıt oluşturulmadıysa, mevcut ID'yi sorgula
            row = cursor.fetchone()
            if not row:
                query_select = """
                SELECT id FROM unique_appointments
                WHERE visa_type_id = %s 
                AND center_name = %s 
                AND book_now_link = %s
                AND visa_category = %s
                AND visa_subcategory = %s
                AND source_country = %s
                AND mission_country = %s
                """
                cursor.execute(query_select, (visa_type_id, center_name, book_now_link,
                                            visa_category, visa_subcategory,
                                            source_country, mission_country))
                row = cursor.fetchone()

            # Telegram mesajını oluştur
            if row:
                appointment_id = row[0]
                appointment_date_text = f"\n- Appointment Date: {appointment_date}" if appointment_date else ""
                message = (
                    f"🆕 Appointment Processed:\n- Center: {center_name}\n- Category: {visa_category}\n"
                    f"- Subcategory: {visa_subcategory}\n- Source: {source_country}\n"
                    f"- Destination: {mission_country}{appointment_date_text}")
                self.telegramBot.send_message(message)
                return appointment_id

        except Exception as e:
            print(f"Error creating or fetching unique appointment in PostgreSQL: {e}")
            return None
        finally:
            cursor.close()
            conn.close()


    def insert_appointment_log(self, data):
        """
        Appointment log kaydını appointment_logs tablosuna ekler ve Telegram mesajı gönderir.

        Args:
            data (dict): Log verisi.
        """
        try:
            with self.connect() as conn:
                with conn.cursor() as cursor:
                    # Tek sorguda kontrol ve ekleme (UPSERT)
                    query_upsert = """
                    INSERT INTO appointment_logs (
                        unique_appointment_id, timestamp, appointment_date, people_looking, last_checked
                    ) VALUES (%s, %s, %s, %s, %s)
                    ON CONFLICT ON CONSTRAINT unique_appointment_log DO NOTHING
                    RETURNING id;
                    """
                    timestamp = data.get("timestamp", datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
                    cursor.execute(query_upsert, (
                        data.get("unique_appointment_id"),
                        timestamp,
                        data.get("appointment_date"),
                        data.get("people_looking"),
                        data.get("last_checked")
                    ))
                    conn.commit()

                    # Eklenen logun ID'sini al
                    inserted_id = cursor.fetchone()

                    if not inserted_id:
                        print(f"Log zaten mevcut: unique_appointment_id={data.get('unique_appointment_id')}")
                        return None
                    else:
                        inserted_id = inserted_id[0]
                        print(f"Log başarıyla eklendi: unique_appointment_id={data.get('unique_appointment_id')}")

                    # Telegram mesajı için gerekli veriyi çek
                    query_fetch = """
                    SELECT ua.center_name, ua.visa_category, ua.visa_subcategory,
                        ua.source_country, ua.mission_country, al.appointment_date
                    FROM unique_appointments ua
                    JOIN appointment_logs al ON ua.id = al.unique_appointment_id
                    WHERE ua.id = %s 
                    ORDER BY al.last_checked DESC LIMIT 1;
                    """
                    cursor.execute(query_fetch, (data.get("unique_appointment_id"),))
                    appointment = cursor.fetchone()

                    if appointment:
                        center_name, visa_category, visa_subcategory, source_country, mission_country, appointment_date = appointment
                        message = (
                            f"🔄 Appointment Log Updated:\n"
                            f"- Center: {center_name}\n"
                            f"- Category: {visa_category}\n"
                            f"- Subcategory: {visa_subcategory}\n"
                            f"- Source: {source_country}\n"
                            f"- Destination: {mission_country}\n"
                            f"- Appointment Date: {appointment_date}"
                        )
                        self.telegramBot.send_message(message)
                        
                    return inserted_id
        except Exception as e:
            print(f"PostgreSQL'e log ekleme sırasında hata: {e}")


    def _process_response_for_appointments(self, response_data):
        """Processes a response entry and logs data into unique_appointments and appointment_logs."""
        try:
            # Parse JSON response if necessary
            if isinstance(response_data, str):
                response_data = json.loads(response_data)

            for entry in response_data:
                visa_type_id = entry.get("visa_type_id")
                appointment_date = entry.get("appointment_date")
                center_name = entry.get("center_name")
                book_now_link = entry.get("book_now_link")

                # Skip entries with missing critical data
                if not visa_type_id or not center_name or not book_now_link:
                    continue

                # Check or create a unique appointment
                unique_appointment_id = self.fetch_or_create_unique_appointment(
                    visa_type_id=visa_type_id,
                    center_name=center_name,
                    book_now_link=book_now_link,
                    visa_category=entry.get("visa_category", "Bilinmiyor"),
                    visa_subcategory=entry.get("visa_subcategory",
                                               "Bilinmiyor"),
                    source_country=entry.get("source_country", "Bilinmiyor"),
                    mission_country=entry.get("mission_country", "Bilinmiyor"))

                # Log to appointment_logs if a unique appointment is found or created
                if unique_appointment_id:
                    self.insert_appointment_log({
                        "unique_appointment_id":
                        unique_appointment_id,
                        "appointment_date":
                        appointment_date,
                        "people_looking":
                        entry.get("people_looking", 0),
                        "last_checked":
                        entry.get("last_checked", None)
                    })
        except Exception as e:
            print(f"Error processing responses for appointments: {e}")

    def insert_processed_response(self, response_id, timestamp):
        """
        İşlenmiş bir response kaydını 'processed_responses' tablosuna ekler.
        """
        processed_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        try:
            conn = self.connect()
            cursor = conn.cursor()
            query = """
            INSERT INTO processed_responses (response_id, timestamp, processed_at)
            VALUES (%s, %s, %s)
            """
            cursor.execute(query, (response_id, timestamp, processed_at))
            conn.commit()
        except Exception as e:
            print(f"PostgreSQL: Processed response eklenirken hata: {e}")
        finally:
            cursor.close()
            conn.close()

    def fetch_unprocessed_responses(self):
        """
        İşlenmeyen responses kayıtlarını getirir.
        """
        try:
            conn = self.connect()
            cursor = conn.cursor()
            query = """
            SELECT r.id, r.timestamp, r.response
            FROM responses r
            LEFT JOIN processed_responses p ON r.id = p.response_id
            WHERE p.response_id IS NULL
            """
            cursor.execute(query)
            rows = cursor.fetchall()
            return rows
        except Exception as e:
            print(
                f"PostgreSQL: İşlenmeyen responses kayıtları çekilirken hata: {e}"
            )
            return []
        finally:
            cursor.close()
            conn.close()

    def fetch_all_data(self, table_name):
        """
        PostgreSQL'deki bir tablodan tüm verileri çeker.
        """
        try:
            conn = self.connect()
            cursor = conn.cursor()
            cursor.execute(f"SELECT * FROM {table_name}")
            rows = cursor.fetchall()
            return rows
        except Exception as e:
            print(
                f"PostgreSQL: {table_name} tablosundan veri çekilirken hata: {e}"
            )
            return []
        finally:
            cursor.close()
            conn.close()
