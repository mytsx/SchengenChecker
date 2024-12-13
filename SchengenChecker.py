
import requests
import json
import time
import logging
import pytz
from datetime import datetime
from plyer import notification
from custom_formatter import CustomFormatter
from replit import db

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

def log_to_db(message):
    tz = pytz.timezone("Europe/Istanbul")
    timestamp = datetime.now(tz).strftime("%Y-%m-%d %H:%M:%S")
    
    # Add to logs
    logs = db.get("logs", [])
    logs.append({"timestamp": timestamp, "message": message})
    db["logs"] = logs[-100:]  # Keep last 100 logs

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

def check_appointments():
    url = "https://api.schengenvisaappointments.com/api/visa-list/?format=json"
    try:
        log_to_db("Kontrol başlatıldı.")
        control_logger.info("Kontrol başlatıldı.")
        response = requests.get(url, timeout=10)
        if response.status_code == 200:
            data = response.json()
            if data:  # Eğer data boş değilse
                for entry in data:
                    country = entry.get("mission_country", "Bilinmiyor")
                    appointment_date = entry.get("appointment_date")
                    
                    message = f"{country} için randevu tarihi: {appointment_date}" if appointment_date else f"{country} için mevcut randevu yok."
                    print(message)
                    logging.info(message)
                    log_to_db(message)
                    
                    if appointment_date and config.get("notification", True):
                        send_notification("Randevu Bulundu", message)
        else:
            error_message = f"Hata: {response.status_code}"
            print(error_message)
            logging.error(error_message)
            log_to_db(error_message)
    except requests.RequestException as e:
        error_message = f"İstek sırasında bir hata oluştu: {e}"
        print(error_message)
        logging.error(error_message)
        log_to_db(error_message)

def send_notification(title, message):
    if config.get("notification", True):
        notification.notify(
            title=title,
            message=message,
            timeout=10
        )

if __name__ == "__main__":
    while True:
        check_appointments()
        time.sleep(config.get("check_interval", 600))
