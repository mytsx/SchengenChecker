import requests
import json
import time
from plyer import notification  # Masaüstü bildirimleri için gerekli

def check_appointments():
    url = "https://api.schengenvisaappointments.com/api/visa-list/?format=json"
    try:
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
                else:
                    print(f"{country} için mevcut randevu yok.")
        else:
            print(f"Hata: {response.status_code}")
    except requests.RequestException as e:
        print(f"İstek sırasında bir hata oluştu: {e}")

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
