from database import Database
import json


def process_unprocessed_responses(db):
    """
    PostgreSQL'den işlenmeyen responses kayıtlarını okur, işler ve her iki veritabanına yazar.

    Args:
        db: Database sınıfı nesnesi.
    """
    # PostgreSQL'den işlenmeyen kayıtları çek
    unprocessed_responses = db.postgreDb.fetch_unprocessed_responses()

    if not unprocessed_responses:
        print("POSTGRESQL: İşlenecek yeni response kaydı bulunamadı.")
        return

    for response_id, timestamp, response_data in unprocessed_responses:
        try:
            # response_data'nın türünü kontrol et
            if isinstance(response_data, str):
                response_data = json.loads(response_data)
            elif isinstance(response_data, list):
                pass  # Liste ise doğrudan devam et
            else:
                print(f"Beklenmeyen response_data türü: {type(response_data)}")
                continue

            for entry in response_data:
                visa_type_id = entry.get("visa_type_id")
                appointment_date = entry.get("appointment_date")
                center_name = entry.get("center_name")
                book_now_link = entry.get("book_now_link")

                if not visa_type_id or not center_name or not book_now_link:
                    continue  # Eksik veri olan kayıtları atla

                # Unique appointment işlemleri (Database sınıfı ile her iki veritabanında çalışır)
                unique_appointment_id = db.fetch_or_create_unique_appointment(
                    visa_type_id=visa_type_id,
                    center_name=center_name,
                    book_now_link=book_now_link,
                    visa_category=entry.get("visa_category", "Bilinmiyor"),
                    visa_subcategory=entry.get("visa_subcategory", "Bilinmiyor"),
                    source_country=entry.get("source_country", "Bilinmiyor"),
                    mission_country=entry.get("mission_country", "Bilinmiyor")
                )

                if unique_appointment_id:
                    # Her iki veritabanına log ekle
                    db.insert_appointment_log({
                        "unique_appointment_id": unique_appointment_id,
                        "appointment_date": appointment_date,
                        "people_looking": entry.get("people_looking", 0),
                        "last_checked": entry.get("last_checked", None)
                    })

            # İşlenen response'u her iki veritabanına ekle
            db.insert_processed_response(response_id, timestamp)

            print(f"POSTGRESQL & SQLITE: Response ID {response_id} işlendi ve kaydedildi.")
        except Exception as e:
            print(f"POSTGRESQL: Response ID {response_id} işlenirken hata: {e}")


if __name__ == "__main__":
    # Database sınıfı üzerinden PostgreSQL ve SQLite bağlantılarını başlat
    db = Database()

    # PostgreSQL'den veriyi oku ve her iki veritabanına yaz
    process_unprocessed_responses(db)
