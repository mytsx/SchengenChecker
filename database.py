import psycopg2
import sqlite3
import json
import pytz
from datetime import datetime


class Database:

    def __init__(self,
                 config_file="postgreconfig.json",
                 sqlite_file="local_data.db"):
        """
        Veritabanı sınıfını başlatır ve yapılandırma dosyasını yükler.

        Args:
            config_file (str): PostgreSQL bağlantı ayarlarını içeren dosya.
            sqlite_file (str): SQLite dosyasının yolu.
        """
        try:
            with open(config_file, "r") as file:
                self.config = json.load(file)
        except FileNotFoundError:
            print(f"{config_file} bulunamadı. Lütfen oluşturun.")
            exit(1)
        except json.JSONDecodeError:
            print(
                f"{config_file} dosyasında bir hata var. Lütfen kontrol edin.")
            exit(1)

        self.sqlite_file = sqlite_file
        self.setup_sqlite()

    def connect_postgres(self):
        """PostgreSQL bağlantısı oluşturur ve döndürür."""
        try:
            return psycopg2.connect(**self.config)
        except psycopg2.OperationalError as e:
            print(f"PostgreSQL bağlantısı başarısız: {e}")
            raise

    def connect_sqlite(self):
        """SQLite bağlantısı oluşturur ve döndürür."""
        try:
            return sqlite3.connect(self.sqlite_file)
        except sqlite3.Error as e:
            print(f"SQLite bağlantısı başarısız: {e}")
            raise

    def setup_sqlite(self):
        """SQLite tablolarını oluşturur."""
        conn = self.connect_sqlite()
        cursor = conn.cursor()
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS responses (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp TEXT NOT NULL,
            response TEXT NOT NULL
        )""")
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS logs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp TEXT NOT NULL,
            message TEXT NOT NULL
        )""")
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS appointments (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp TEXT NOT NULL,
            message TEXT NOT NULL
        )""")
        conn.commit()
        conn.close()

    def prune_sqlite_table(self, table_name, max_records=5000):
        """SQLite tablosundaki kayıt sayısını sınırlı tutar."""
        conn = self.connect_sqlite()
        cursor = conn.cursor()
        cursor.execute(f"SELECT COUNT(*) FROM {table_name}")
        row_count = cursor.fetchone()[0]
        if row_count > max_records:
            excess = row_count - max_records
            cursor.execute(
                f"DELETE FROM {table_name} WHERE id IN (SELECT id FROM {table_name} ORDER BY id LIMIT ?)",
                (excess, ))
        conn.commit()
        conn.close()

    def log_to_table(self, table_name, data):
        """
        Belirtilen tabloya PostgreSQL ve SQLite veritabanlarına veri ekler.

        Args:
            table_name (str): Veri eklenecek tablo adı.
            data (str or dict): Eklenmek istenen veri.
        """
        # Timestamp
        tz = pytz.timezone("Europe/Istanbul")
        timestamp = datetime.now(tz).strftime("%Y-%m-%d %H:%M:%S")

        # PostgreSQL'e kayıt
        try:
            conn_pg = self.connect_postgres()
            cursor_pg = conn_pg.cursor()
            if table_name == "responses":
                cursor_pg.execute(
                    f"INSERT INTO {table_name} (timestamp, response) VALUES (%s, %s)",
                    (timestamp, json.dumps(data)))
            elif table_name in ["logs", "appointments"]:
                cursor_pg.execute(
                    f"INSERT INTO {table_name} (timestamp, message) VALUES (%s, %s)",
                    (timestamp, data))
            conn_pg.commit()
        except Exception as e:
            print(f"PostgreSQL'e kayıt sırasında hata: {e}")
        finally:
            cursor_pg.close()
            conn_pg.close()

        # SQLite'e kayıt
        try:
            conn_sqlite = self.connect_sqlite()
            cursor_sqlite = conn_sqlite.cursor()
            if table_name == "responses":
                cursor_sqlite.execute(
                    f"INSERT INTO {table_name} (timestamp, response) VALUES (?, ?)",
                    (timestamp, json.dumps(data)))
            elif table_name in ["logs", "appointments"]:
                cursor_sqlite.execute(
                    f"INSERT INTO {table_name} (timestamp, message) VALUES (?, ?)",
                    (timestamp, data))
            conn_sqlite.commit()
            self.prune_sqlite_table(table_name)
        except Exception as e:
            print(f"SQLite'e kayıt sırasında hata: {e}")
        finally:
            cursor_sqlite.close()
            conn_sqlite.close()

    def fetch_table_data(self, table_name, limit=10, json_column=False):
        """SQLite'tan belirtilen tablodan veri çeker."""
        try:
            conn = self.connect_sqlite()
            cursor = conn.cursor()
            if json_column:
                query = f"SELECT timestamp, response FROM {table_name} ORDER BY id DESC LIMIT ?"
            else:
                query = f"SELECT timestamp, message FROM {table_name} ORDER BY id DESC LIMIT ?"
            cursor.execute(query, (limit, ))
            rows = cursor.fetchall()
            if json_column:
                return [{
                    "timestamp": row[0],
                    "response": json.loads(row[1])
                } for row in rows]
            return [{"timestamp": row[0], "message": row[1]} for row in rows]
        except Exception as e:
            print(f"SQLite veri çekme sırasında hata: {e}")
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
            conn = self.connect_sqlite()
            cursor = conn.cursor()
            cursor.execute(
                "SELECT response FROM responses ORDER BY id DESC LIMIT 1")
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
