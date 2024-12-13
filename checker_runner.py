import json
import time
from database import Database
from schengen_checker import SchengenChecker


def main():
    # Config dosyasını yükle
    try:
        with open("config.json", "r", encoding="utf-8") as file:
            config = json.load(file)
    except FileNotFoundError:
        print(
            "Config dosyası bulunamadı. Lütfen config.json dosyasını oluşturun."
        )
        return
    except json.JSONDecodeError:
        print(
            "Config dosyasını okuyamıyorum. Lütfen JSON formatını kontrol edin."
        )
        return

    # Veritabanı ve SchengenChecker başlat
    db = Database()
    checker = SchengenChecker(config, db)

    # Checker döngüsü
    while True:
        checker.check_appointments()
        time.sleep(config.get("check_interval", 600))  # Varsayılan 10 dakika


if __name__ == "__main__":
    main()
