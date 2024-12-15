import time
from database import Database
from schengen_checker import SchengenChecker


def main():
    # Veritabanı ve SchengenChecker başlat
    db = Database()
    checker = SchengenChecker(db)

    # Checker döngüsü
    while True:
        checker.check_appointments()
        time.sleep(checker.config.get("check_interval",
                                      600))  # Varsayılan 10 dakika


if __name__ == "__main__":
    main()
