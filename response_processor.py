import json
class ResponseProcessor:
    def __init__(self, db ):
        """
        ResponseProcessor sınıfını başlatır ve Database nesnesini oluşturur.
        """
        self.db = db
    def process_unprocessed_responses(self, data):
        """
        Gelen response verilerini işler ve her iki veritabanına yazar.

        Args:
            data (list[dict]): İşlenecek response verileri.
        """
        if not data:
            print("İşlenecek response verisi bulunamadı.")
            return

        for entry in data:
            try:
                self.process_single_entry(entry)
                print(f"Veri işlendi: {entry.get('visa_type_id')}, {entry.get('appointment_date')}")
            except Exception as e:
                print(f"Bir kayıt işlenirken hata oluştu: {e}")

    def process_single_entry(self, entry):
        """
        Tek bir response girişini işler ve her iki veritabanında gerekli kayıtları oluşturur.

        Args:
            entry (dict): Tek bir response kaydı.
        """
        visa_type_id = entry.get("visa_type_id")
        appointment_date = entry.get("appointment_date")
        center_name = entry.get("center_name")
        book_now_link = entry.get("book_now_link")

        # Eksik veri kontrolü
        if not visa_type_id or not center_name or not book_now_link:
            print("Eksik veri bulunan bir kayıt atlandı.")
            return

        # Unique appointment işlemleri
        unique_appointment_id = self.db.fetch_or_create_unique_appointment(
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
            self.db.insert_appointment_log({
                "unique_appointment_id": unique_appointment_id,
                "appointment_date": appointment_date,
                "people_looking": entry.get("people_looking", 0),
                "last_checked": entry.get("last_checked", None)
            })

    def process_all_unprocessed_responses(self):
        """
        İşlenmeyen response kayıtlarını veritabanından çekerek işleyen ana çalışma fonksiyonu.
        """
        datas = self.db.postgreDb.fetch_unprocessed_responses()
        for data in datas:
            response_id, timestamp, response_data = data
            if isinstance(response_data, str):
                try:
                    response_data = json.loads(response_data)
                except json.JSONDecodeError:
                    print(f"Response ID {response_id}: JSON verisi çözülürken hata.")
                    continue
            elif not isinstance(response_data, list):
                print(f"Response ID {response_id}: Beklenmeyen response_data türü: {type(response_data)}")
                continue

            self.process_unprocessed_responses(response_data)
