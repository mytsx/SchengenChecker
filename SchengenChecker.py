import requests
import json
import time
import logging
import pytz
from datetime import datetime
import psycopg2
from plyer import notification
from custom_formatter import CustomFormatter

# Logger configurations
logging.basicConfig(filename="appointment_logs.txt",
                    level=logging.INFO,
                    format="%(asctime)s - %(levelname)s - %(message)s",
                    encoding="utf-8",
                    datefmt="%Y-%m-%d %H:%M:%S")

# Control logger with custom formatter
control_logger = logging.getLogger("control_logger")
control_handler = logging.FileHandler("control_times.txt", encoding="utf-8")
custom_formatter = CustomFormatter("%(asctime)s - %(message)s",
                                   datefmt="%Y-%m-%d %H:%M:%S")
control_handler.setFormatter(custom_formatter)
control_logger.addHandler(control_handler)
control_logger.setLevel(logging.INFO)

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

try:
    conn = psycopg2.connect(**DATABASE_CONFIG)
    cursor = conn.cursor()
    print("PostgreSQL bağlantısı başarılı.")
except psycopg2.OperationalError as e:
    print(f"PostgreSQL bağlantısı başarısız: {e}")
    exit(1)

# Config dosyasını yükle
try:
    with open("config.json", "r", encoding="utf-8") as config_file:
        config = json.load(config_file)
except FileNotFoundError:
    print("config.json dosyası bulunamadı. Lütfen oluşturun.")
    exit(1)
except json.JSONDecodeError:
    print("config.json dosyasında bir hata var. Lütfen kontrol edin.")
    exit(1)


def log_to_db(table_name, data):
    """
    Log data to the specified PostgreSQL table.

    Args:
        table_name (str): The name of the table to log the data into.
        data (str or dict): The data to log. If logging to 'responses',
                            this should be a dictionary (JSON-compatible).
    """
    try:
        # Current timestamp
        tz = pytz.timezone("Europe/Istanbul")
        timestamp = datetime.now(tz).strftime("%Y-%m-%d %H:%M:%S")

        if table_name == "responses":
            # Insert JSON data into the 'responses' table
            cursor.execute(
                f"INSERT INTO {table_name} (timestamp, response) VALUES (%s, %s)",
                (timestamp, json.dumps(data))  # Store as JSON
            )
        elif table_name in ["logs", "appointments"]:
            # Insert message into 'logs' or 'appointments' table
            cursor.execute(
                f"INSERT INTO {table_name} (timestamp, message) VALUES (%s, %s)",
                (timestamp, data)  # Store as plain text
            )
        else:
            raise ValueError(f"Unknown table: {table_name}")

        # Commit changes
        conn.commit()
    except Exception as e:
        logging.error(f"Error logging to {table_name}: {e}")


def check_appointments():
    url = "https://api.schengenvisaappointments.com/api/visa-list/?format=json"
    try:
        # Log kontrol başlangıcı
        log_to_db("logs", "Kontrol yapıldı.")
        control_logger.info("Kontrol yapıldı.")

        # API isteği
        response = requests.get(url, timeout=10)
        if response.status_code == 200:
            data = response.json()

            # Farklı response kontrolü
            cursor.execute(
                "SELECT response FROM responses ORDER BY id DESC LIMIT 1")
            last_response = cursor.fetchone()
            last_response = last_response[0] if last_response else None

            if data != last_response:
                # Yeni response'u kaydet
                log_to_db("responses", data)

            if data:  # Eğer data boş değilse
                for entry in data:
                    country = entry.get("mission_country", "Bilinmiyor")
                    appointment_date = entry.get("appointment_date")

                    # Mesajı oluştur
                    message = (
                        f"{country} için randevu tarihi: {appointment_date}"
                        if appointment_date else
                        f"{country} için mevcut randevu yok.")
                    print(message)

                    # Loglama
                    logging.info(message)
                    log_to_db("logs", message)

                    # Bildirim gönder
                    if appointment_date:
                        appointment_message = f"{country} için randevu tarihi: {appointment_date}"
                        log_to_db("appointments", appointment_message)

                        # Bildirim gönder
                        if config.get("notification", True):
                            send_notification("Randevu Bulundu",
                                              appointment_message)
        else:
            # Hata durumunu logla
            error_message = f"Hata: {response.status_code}"
            print(error_message)
            logging.error(error_message)
            log_to_db("logs", error_message)

    except requests.RequestException as e:
        # İstek sırasında oluşan hatayı logla
        error_message = f"İstek sırasında bir hata oluştu: {e}"
        print(error_message)
        logging.error(error_message)
        log_to_db("logs", error_message)


def send_notification(title, message):
    if config.get("notification", True):
        notification.notify(title=title, message=message, timeout=10)


if __name__ == "__main__":
    while True:
        check_appointments()
        time.sleep(config.get("check_interval", 600))
