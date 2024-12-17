import sqlite3
import json
import pytz
from datetime import datetime
from config_loader import ConfigLoader, ConfigWrapper

class SQLiteDatabase:
    def __init__(self):

        database_config_data = ConfigLoader.load_config("sqlite.json")
        self.config = ConfigWrapper(database_config_data).config_data
        self.db_file = self.config.get("file", "local_data.db")

    def connect(self):
        try:
            return sqlite3.connect(self.db_file)
        except sqlite3.Error as e:
            print(f"SQLite bağlantısı başarısız: {e}")
            raise

    def create_table_from_schema(self, table_name, schema):
        """
        PostgreSQL şemasından SQLite tablosu oluşturur.
        ID sütununu otomatik artan PRIMARY KEY olarak tanımlar.
        """
        create_query = f"CREATE TABLE IF NOT EXISTS {table_name} ("
        column_definitions = []

        for column_name, data_type in schema:
            # ID sütunu için özel bir kontrol
            if column_name.lower() == "id":
                column_definitions.append(f"{column_name} INTEGER PRIMARY KEY AUTOINCREMENT")
            else:
                # Diğer sütunlar için veri tipi dönüştürme
                sqlite_type = self.map_postgres_to_sqlite(data_type)
                column_definitions.append(f"{column_name} {sqlite_type}")

        create_query += ", ".join(column_definitions) + ");"

        try:
            conn = self.connect()
            cursor = conn.cursor()

            # Önce var olan tabloyu kaldır (isteğe bağlı, tamamen yeniden oluşturmak için)
            cursor.execute(f"DROP TABLE IF EXISTS {table_name}")

            # Yeni tabloyu oluştur
            cursor.execute(create_query)
            conn.commit()
            print(f"SQLite: {table_name} tablosu başarıyla oluşturuldu.")
        except Exception as e:
            print(f"SQLite tablosu oluşturulurken hata: {e}")
        finally:
            cursor.close()
            conn.close()


    def log_to_table(self, table_name, data):
        """Logs data into a SQLite table and triggers additional actions for `responses`."""
        tz = pytz.timezone("Europe/Istanbul")
        timestamp = datetime.now(tz).strftime("%Y-%m-%d %H:%M:%S")
        try:
            conn = self.connect()
            cursor = conn.cursor()

            # Insert data into the specified table
            if table_name == "responses":
                cursor.execute(
                    f"INSERT INTO {table_name} (timestamp, response) VALUES (?, ?)",
                    (timestamp, json.dumps(data))
                )
                conn.commit()

                # Process the inserted response for unique appointments and logs
                self._process_response_for_appointments(data)

            elif table_name in ["logs", "appointments"]:
                cursor.execute(
                    f"INSERT INTO {table_name} (timestamp, message) VALUES (?, ?)",
                    (timestamp, data)
                )
                conn.commit()

        except Exception as e:
            print(f"SQLite'e kayıt sırasında hata: {e}")
        finally:
            cursor.close()
            conn.close()

    def fetch_table_data(self, table_name, limit=10, json_column=False):
        """SQLite'tan belirtilen tablodan veri çeker."""
        try:
            conn = self.connect()
            cursor = conn.cursor()
            if json_column:
                query = f"SELECT timestamp, response FROM {table_name} ORDER BY id DESC LIMIT ?"
            else:
                query = f"SELECT timestamp, message FROM {table_name} ORDER BY id DESC LIMIT ?"
            cursor.execute(query, (limit,))
            rows = cursor.fetchall()
            if json_column:
                return [{"timestamp": row[0], "response": json.loads(row[1])} for row in rows]
            return [{"timestamp": row[0], "message": row[1]} for row in rows]
        except Exception as e:
            print(f"SQLite veri çekme sırasında hata: {e}")
            return []
        finally:
            cursor.close()
            conn.close()

    def get_last_response(self, table_name="responses"):
        """SQLite'tan belirtilen tablodan en son kaydı alır."""
        try:
            conn = self.connect()
            cursor = conn.cursor()
            cursor.execute(
                f"SELECT response FROM {table_name} ORDER BY id DESC LIMIT 1"
            )
            row = cursor.fetchone()
            if row and row[0]:
                return json.loads(row[0])  # JSON formatına dönüştür
            return None
        except Exception as e:
            print(f"SQLite'tan son yanıt alınırken hata: {e}")
            return None
        finally:
            cursor.close()
            conn.close()


    def fetch_responses(self, table_name="responses", limit=500):
        """
        Fetch JSON responses from the 'responses' table in SQLite.
        """
        try:
            conn = self.connect()
            cursor = conn.cursor()
            query = f"SELECT timestamp, response FROM {table_name} ORDER BY id DESC LIMIT ?"
            cursor.execute(query, (limit,))
            rows = cursor.fetchall()

            response_list = []
            for row in rows:
                timestamp = row[0]
                response_data = row[1]
                # Parse JSON string into dictionary
                if response_data:
                    response_data = json.loads(response_data)

                if isinstance(response_data, list):
                    for record in response_data:
                        response_list.append({"timestamp": timestamp, **record})
                else:
                    response_list.append({"timestamp": timestamp, "data": response_data})
            
            return response_list
        except Exception as e:
            print(f"SQLite fetch_responses error: {e}")
            return []
        finally:
            cursor.close()
            conn.close()

    def fetch_or_create_unique_appointment(self, visa_type_id, center_name, book_now_link,
                                           visa_category, visa_subcategory, source_country,
                                           mission_country):
        """
        Check or create a unique appointment in the SQLite database.
        """
        try:
            conn = self.connect()
            cursor = conn.cursor()

            # Check for existing entry
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
            cursor.execute(query_select, (visa_type_id, center_name, book_now_link, visa_category,
                                        visa_subcategory, source_country, mission_country))
            row = cursor.fetchone()

            if row:
                return row[0]  # Return existing ID

            # Insert new record
            query_insert = """
            INSERT INTO unique_appointments (
                center_name, visa_type_id, visa_category, visa_subcategory,
                source_country, mission_country, book_now_link
            ) VALUES (?, ?, ?, ?, ?, ?, ?)
            """
            cursor.execute(query_insert, (center_name, visa_type_id, visa_category, visa_subcategory,
                                          source_country, mission_country, book_now_link))
            conn.commit()
            return cursor.lastrowid  # Return the ID of the new record
        except Exception as e:
            print(f"SQLite fetch_or_create_unique_appointment error: {e}")
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
            conn = self.connect()
            cursor = conn.cursor()

            # Önce aynı kayıt var mı kontrol et
            query_check = """
            SELECT id FROM appointment_logs
            WHERE unique_appointment_id = %s 
            AND timestamp = %s 
            AND appointment_date = %s 
            AND people_looking = %s 
            AND last_checked = %s;
            """
            timestamp = data.get("timestamp", datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
            cursor.execute(query_check, (
                data.get("unique_appointment_id"),
                timestamp,
                data.get("appointment_date"),
                data.get("people_looking"),
                data.get("last_checked")
            ))
            existing_log = cursor.fetchone()

            if existing_log:
                print(f"Log already exists with ID: {existing_log[0]}")
                return  # Aynı kayıt varsa ekleme yapma

            # Eğer kayıt yoksa, ekle
            query_insert = """
            INSERT INTO appointment_logs (
                unique_appointment_id, timestamp, appointment_date, people_looking, last_checked
            ) VALUES (%s, %s, %s, %s, %s)
            """
            cursor.execute(query_insert, (
                data.get("unique_appointment_id"),
                timestamp,
                data.get("appointment_date"),
                data.get("people_looking"),
                data.get("last_checked")
            ))
            conn.commit()

        except Exception as e:
            print(f"PostgreSQL'e log ekleme sırasında hata: {e}")
        finally:
            cursor.close()
            conn.close()


    @staticmethod
    def map_postgres_to_sqlite(data_type):
        """
        PostgreSQL veri türlerini SQLite türlerine eşler.
        """
        mapping = {
            "integer": "INTEGER",
            "bigint": "INTEGER",
            "smallint": "INTEGER",
            "serial": "INTEGER",
            "bigserial": "INTEGER",
            "text": "TEXT",
            "character varying": "TEXT",
            "varchar": "TEXT",
            "char": "TEXT",
            "boolean": "INTEGER",  # SQLite'ta boolean 0 (False) veya 1 (True) olarak kullanılır
            "date": "TEXT",  # Tarihleri TEXT olarak saklarız
            "timestamp without time zone": "TEXT",
            "timestamp with time zone": "TEXT",
            "json": "TEXT",  # JSON türleri TEXT olarak saklanır
            "jsonb": "TEXT",
            "double precision": "REAL",  # FLOAT ve DOUBLE türleri REAL'e dönüşür
            "real": "REAL",
            "numeric": "REAL",
            "decimal": "REAL"
        }
        return mapping.get(data_type.lower(), "TEXT")  # Varsayılan olarak TEXT döner

    

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
                    visa_subcategory=entry.get("visa_subcategory", "Bilinmiyor"),
                    source_country=entry.get("source_country", "Bilinmiyor"),
                    mission_country=entry.get("mission_country", "Bilinmiyor")
                )

                # Log to appointment_logs if a unique appointment is found or created
                if unique_appointment_id:
                    self.insert_appointment_log({
                        "unique_appointment_id": unique_appointment_id,
                        "appointment_date": appointment_date,
                        "people_looking": entry.get("people_looking", 0),
                        "last_checked": entry.get("last_checked", None)
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
            VALUES (?, ?, ?)
            """
            cursor.execute(query, (response_id, timestamp, processed_at))
            conn.commit()
        except Exception as e:
            print(f"SQLite: Processed response eklenirken hata: {e}")
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
            print(f"SQLite: İşlenmeyen responses kayıtları çekilirken hata: {e}")
            return []
        finally:
            cursor.close()
            conn.close()

    def insert_bulk_data(self, table_name, schema, rows):
        """
        SQLite'a toplu veri ekler. 
        - ID sütununu otomatik artan olarak ayarlar.
        - JSON türündeki verileri string'e dönüştürür.
        """
        try:
            conn = self.connect()
            cursor = conn.cursor()

            # Şemadan sütun isimlerini al
            column_names = [col[0] for col in schema]
            
            # ID sütunu kontrolü: Eğer "id" varsa onu dışarıda bırak
            if "id" in column_names:
                columns_without_id = [col for col in column_names if col.lower() != "id"]
                placeholders = ", ".join(["?" for _ in columns_without_id])
                query = f"INSERT INTO {table_name} ({', '.join(columns_without_id)}) VALUES ({placeholders})"

                # ID sütunu hariç verileri JSON kontrolü ile dönüştür
                processed_rows = [
                    tuple(
                        json.dumps(value) if isinstance(value, (list, dict)) else value
                        for i, value in enumerate(row) if column_names[i].lower() != "id"
                    )
                    for row in rows
                ]
            else:
                # ID sütunu yoksa tüm sütunları ekle
                placeholders = ", ".join(["?" for _ in schema])
                query = f"INSERT INTO {table_name} VALUES ({placeholders})"
                processed_rows = [
                    tuple(
                        json.dumps(value) if isinstance(value, (list, dict)) else value
                        for value in row
                    )
                    for row in rows
                ]

            # Toplu veri ekleme
            cursor.executemany(query, processed_rows)
            conn.commit()
            print(f"SQLite: {table_name} tablosuna {len(rows)} kayıt eklendi.")
        except Exception as e:
            print(f"SQLite: {table_name} tablosuna veri eklenirken hata: {e}")
        finally:
            cursor.close()
            conn.close()


