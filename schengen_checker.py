import requests
import logging


class SchengenChecker:

    def __init__(self, config, control_logger, db):
        """
        SchengenChecker sınıfını başlatır.

        Args:
            config (dict): Uygulama yapılandırması.
            control_logger (logging.Logger): Kontrol işlemleri için logger.
            db (Database): Veritabanı işlemleri için Database nesnesi.
        """
        self.config = config
        self.control_logger = control_logger
        self.db = db
        self.url = "https://api.schengenvisaappointments.com/api/visa-list/?format=json"

    def check_appointments(self):
        try:
            # Log kontrol başlangıcı
            self.db.log_to_table("logs", "Kontrol yapıldı.")
            self.control_logger.info("Kontrol yapıldı.")

            # API isteği
            response = requests.get(self.url, timeout=10)
            if response.status_code == 200:
                data = response.json()

                # Farklı response kontrolü
                last_response = self.db.get_last_response()
                if data != last_response:
                    self.db.log_to_table("responses", data)

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
                    self.db.log_to_table("logs", message)

                    # Bildirim gönder
                    if appointment_date:
                        appointment_message = f"{country} için randevu tarihi: {appointment_date}"
                        self.db.log_to_table("appointments",
                                             appointment_message)

                        # Bildirim gönder
                        if self.config.get("notification", True):
                            self.send_notification("Randevu Bulundu",
                                                   appointment_message)
            else:
                error_message = f"Hata: {response.status_code}"
                print(error_message)
                logging.error(error_message)
                self.db.log_to_table("logs", error_message)

        except requests.RequestException as e:
            error_message = f"İstek sırasında bir hata oluştu: {e}"
            print(error_message)
            logging.error(error_message)
            self.db.log_to_table("logs", error_message)

    def send_notification(self, title, message):
        if self.config.get("notification", True):
            from plyer import notification
            notification.notify(title=title, message=message, timeout=10)
