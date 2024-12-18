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
            error_message = f"Şema alınırken hata: {e}"
            print(error_message)
            self.log_error_to_db(
                error_message=error_message,
                source_function="get_table_schema",
            )
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
            error_message = f"Tablo isimleri alınırken hata: {e}"
            print(error_message)
            self.log_error_to_db(
                error_message=error_message,
                source_function="get_all_table_names",
            )
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

            elif table_name in ["logs", "appointments"]:
                cursor.execute(
                    f"INSERT INTO {table_name} (timestamp, message) VALUES (%s, %s)",
                    (timestamp, data))
            
            inserted_id = cursor.fetchone()[0]
            conn.commit()

        except Exception as e:
            error_message = f"Log kaydı sırasında hata: {e}"
            print(error_message)
            self.log_error_to_db(
                error_message=error_message,
                source_function="log_to_table",
                additional_data=data
            )
        finally:
            cursor.close()
            conn.close()
        
        return inserted_id

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
            error_message = f"Error fetching responses: {e}"
            print(error_message)
            self.log_error_to_db(
                error_message=error_message,
                source_function="fetch_responses_from_postgres",
            )
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

            row = cursor.fetchone()
            if row:
                conn.commit()  # Yeni kayıt oluşturulduysa commit yap
                appointment_id = row[0]
                appointment_date_text = f"🗓️ Randevu Tarihi: {appointment_date}" if appointment_date else "🗓️ Randevu Tarihi Henüz Belirtilmedi"
                message = (
                    f"🎉 Yeni Randevu İşlendi:\n"
                    f"📍 Başvuru Merkezi: {center_name}\n"
                    f"📋 Kategori: {visa_category}\n"
                    f"🔖 Alt Kategori: {visa_subcategory}\n"
                    f"🌍 Kaynak Ülke: {source_country}\n"
                    f"✈️ Hedef Ülke: {mission_country}\n"
                    f"{appointment_date_text}"
                )
                self.telegramBot.send_message(message)

                return appointment_id

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
            conn.commit()
            if row:
                return row[0]

            return None

        except Exception as e:
            error_message = f"Error creating or fetching unique appointment: {e}"
            print(error_message)
            self.log_error_to_db(
                error_message=error_message,
                source_function="fetch_or_create_unique_appointment",
            )
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
                        if appointment_date:  
                            message = (
                                f"✅ Randevu Güncellendi:\n"
                                f"📍 Başvuru Merkezi: {center_name}\n"
                                f"📋 Kategori: {visa_category}\n"
                                f"🔖 Alt Kategori: {visa_subcategory}\n"
                                f"🌍 Kaynak Ülke: {source_country}\n"
                                f"✈️ Hedef Ülke: {mission_country}\n"
                                f"🗓️ Randevu Tarihi: {appointment_date}"
                            )
                            self.telegramBot.send_message(message)
                        else:
                            print("Appointment date not available, skipping Telegram notification.")

                        
                    return inserted_id
        except Exception as e:
            error_message = f"Appointment log'u ekleme sırasında hata: {e}"
            print(error_message)
            self.log_error_to_db(
                error_message=error_message,
                source_function="insert_appointment_log",
                additional_data=data
            )


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
            error_message = f"Processed response eklenirken hata: {e}"
            print(error_message)
            self.log_error_to_db(
                error_message=error_message,
                source_function="insert_processed_response",
            )
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
            error_message = f"İşlenmeyen responses kayıtları çekilirken hata: {e}"
            print(error_message)
            self.log_error_to_db(
                error_message=error_message,
                source_function="fetch_unprocessed_responses",
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
            error_message = f"{table_name} tablosundan veri çekilirken hata: {e}"
            print(error_message)
            self.log_error_to_db(
                error_message=error_message,
                source_function="fetch_all_data",
            )
            return []
        finally:
            cursor.close()
            conn.close()

    def log_error_to_db(self, error_message, source_function=None, additional_data=None):
        """
        Hataları error_logs tablosuna yazar.

        Args:
            error_message (str): Hata mesajı.
            source_function (str): Hatanın oluştuğu fonksiyon adı.
            additional_data (dict): Ek veri (isteğe bağlı).
        """
        try:
            class_name = self.__class__.__name__
            full_message = f"[{class_name}] {error_message}"
            conn = self.connect()
            cursor = conn.cursor()
            query = """
            INSERT INTO error_logs (error_message, source_function, additional_data)
            VALUES (%s, %s, %s);
            """
            cursor.execute(query, (
                full_message,
                source_function,
                json.dumps(additional_data) if additional_data else None
            ))
            conn.commit()
        except Exception as e:
            print(f"Error logging to error_logs: {e}")
        finally:
            cursor.close()
            conn.close()
