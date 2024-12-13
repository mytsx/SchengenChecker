import requests
import json
import time
import logging
from plyer import notification  # Masaüstü bildirimleri için gerekli

# Logger ayarları
logging.basicConfig(
    filename="appointment_logs.txt",
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    encoding="utf-8"
)

# Ayrı bir logger kontrol edilen vakitler için
control_logger = logging.getLogger("control_logger")
control_handler = logging.FileHandler("control_times.txt", encoding="utf-8")
control_handler.setFormatter(logging.Formatter("%(asctime)s - %(message)s"))
control_logger.addHandler(control_handler)
control_logger.setLevel(logging.INFO)

def check_appointments():
    url = "https://api.schengenvisaappointments.com/api/visa-list/?format=json"
    try:
        control_logger.info("Kontrol başlatıldı.")  # Kontrol başlangıcını logla
        response = requests.get(url, timeout=10)  # Zaman aşımı eklendi
        if response.status_code == 200:
            data = response.json()
            for entry in data:
                country = entry.get("mission_country", "Bilinmiyor")
                appointment_date = entry.get("appointment_date")

                if appointment_date:
                    message = f"{country} için randevu tarihi: {appointment_date}"
                    print(message)
                    send_notification("Randevu Bulundu", message)
                    logging.info(message)  # Log dosyasına yaz
                else:
                    no_appointment_message = f"{country} için mevcut randevu yok."
                    print(no_appointment_message)
                    logging.info(no_appointment_message)  # Log dosyasına yaz
        else:
            error_message = f"Hata: {response.status_code}"
            print(error_message)
            logging.error(error_message)  # Hataları da logla
    except requests.RequestException as e:
        error_message = f"İstek sırasında bir hata oluştu: {e}"
        print(error_message)
        logging.error(error_message)  # Hataları da logla

def send_notification(title, message):
    notification.notify(
        title=title,
        message=message,
        timeout=10  # Bildirimin ekranda kalma süresi (saniye)
    )

if __name__ == "__main__":
    while True:
        check_appointments()
        time.sleep(600)  # 10 dakika bekle (600 saniye)
