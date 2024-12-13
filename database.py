import psycopg2
import json
import pytz
from datetime import datetime


class Database:

    def __init__(self, config_file="postgreconfig.json"):
        """
        Veritabanı sınıfını başlatır ve yapılandırma dosyasını yükler.

        Args:
            config_file (str): PostgreSQL bağlantı ayarlarını içeren dosya.
        """
        try:
            with open(config_file, "r") as file:
                self.config = json.load(file)
        except FileNotFoundError:
            print(
                f"{config_file} bulunamadı. Lütfen oluşturun ve gerekli bilgileri ekleyin."
            )
            exit(1)
        except json.JSONDecodeError:
            print(
                f"{config_file} dosyasında bir hata var. Lütfen kontrol edin.")
            exit(1)

    def connect(self):
        """Yeni bir veritabanı bağlantısı oluşturur ve döndürür."""
        try:
            conn = psycopg2.connect(**self.config)
            return conn
        except psycopg2.OperationalError as e:
            print(f"PostgreSQL bağlantısı başarısız: {e}")
            raise

    def log_to_table(self, table_name, data):
        """
        Belirtilen tabloya veri ekler.

        Args:
            table_name (str): Veri eklenecek tablo adı.
            data (str or dict): Eklenmek istenen veri. Eğer tablo 'responses' ise JSON olmalıdır.
        """
        try:
            conn = self.connect()
            cursor = conn.cursor()

            # Current timestamp
            tz = pytz.timezone("Europe/Istanbul")
            timestamp = datetime.now(tz).strftime("%Y-%m-%d %H:%M:%S")

            if table_name == "responses":
                # Son kaydı al ve karşılaştır
                cursor.execute(
                    "SELECT response FROM responses ORDER BY timestamp DESC LIMIT 1"
                )
                last_response_row = cursor.fetchone()
                last_response = json.loads(
                    last_response_row[0]) if last_response_row else None

                if last_response != data:
                    # Farklı ise yeni response'u ekle
                    cursor.execute(
                        f"INSERT INTO {table_name} (timestamp, response) VALUES (%s, %s)",
                        (timestamp, json.dumps(data)),
                    )
            elif table_name in ["logs", "appointments"]:
                cursor.execute(
                    f"INSERT INTO {table_name} (timestamp, message) VALUES (%s, %s)",
                    (timestamp, data),
                )
            else:
                raise ValueError(f"Unknown table: {table_name}")

            conn.commit()
        except Exception as e:
            print(f"Error logging to {table_name}: {e}")
        finally:
            cursor.close()
            conn.close()

    def fetch_table_data(self, table_name, limit=10, json_column=False):
        # Aynı veri çekme işlemleri
        try:
            conn = self.connect()
            cursor = conn.cursor()
            if json_column:
                query = f"SELECT timestamp, response FROM {table_name} ORDER BY timestamp DESC LIMIT %s"
            else:
                query = f"SELECT timestamp, message FROM {table_name} ORDER BY timestamp DESC LIMIT %s"
            cursor.execute(query, (limit, ))
            rows = cursor.fetchall()
            if json_column:
                result = []
                for row in rows:
                    try:
                        response_data = json.loads(row[1]) if row[1] else {}
                    except json.JSONDecodeError:
                        response_data = {"error": "Invalid JSON format"}
                    result.append({
                        "timestamp": row[0],
                        "response": response_data
                    })
            else:
                result = [{
                    "timestamp": row[0],
                    "message": row[1]
                } for row in rows]
            return result
        except Exception as e:
            print(f"Error fetching data from {table_name}: {e}")
            return []
        finally:
            cursor.close()
            conn.close()

    def get_last_response(self):
        """
        'responses' tablosundan en son kaydedilen JSON yanıtını çeker.

        Returns:
            dict: En son yanıt. Hiç yanıt yoksa None döndürür.
        """
        try:
            conn = self.connect()
            cursor = conn.cursor()
            query = "SELECT response FROM responses ORDER BY timestamp DESC LIMIT 1"
            cursor.execute(query)
            row = cursor.fetchone()
            if row and row[0]:
                return json.loads(row[0])  # JSON formatına dönüştür
            return None
        except Exception as e:
            print(f"Error fetching last response: {e}")
            return None
        finally:
            cursor.close()
            conn.close()
