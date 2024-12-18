from postgres_database import PostgresDatabase
from sqlite_database import SQLiteDatabase
from response_processor import ResponseProcessor
from datetime import datetime
import pytz

class Database:

    def __init__(self):
        self.postgreDb = PostgresDatabase()
        self.sqliteDb = SQLiteDatabase()
        self.responseProcessor = ResponseProcessor(self)

    def log_to_table(self, table_name, data):
        """
        Veriyi hem PostgreSQL hem de SQLite veritabanlarına loglar.
        Eğer 'responses' tablosuna log eklenirse, işlem sonrası response'u işler.
        """
        inserted_id = self.postgreDb.log_to_table(table_name, data)
        self.sqliteDb.log_to_table(table_name, data)

        if table_name == "responses":
            self.responseProcessor.process_unprocessed_responses(data)
            tz = pytz.timezone("Europe/Istanbul")
            timestamp = datetime.now(tz).strftime("%Y-%m-%d %H:%M:%S")
            self.insert_processed_response(inserted_id, timestamp)

    def fetch_table_data(self, table_name, limit=10, json_column=False):
        return self.sqliteDb.fetch_table_data(table_name, limit, json_column)

    def fetch_responses_from_postgres(self, limit=500):
        return self.sqliteDb.fetch_responses(limit=limit)

    def fetch_or_create_unique_appointment(self,
                                        visa_type_id,
                                        center_name,
                                        book_now_link,
                                        visa_category,
                                        visa_subcategory,
                                        source_country,
                                        mission_country,
                                        appointment_date=None):
        """
        PostgreSQL'de benzersiz bir randevu kaydı oluşturduktan sonra SQLite'da da aynı kaydı oluşturur.
        """
        try:
            # PostgreSQL'de kaydı kontrol et veya oluştur
            postgres_id = self.postgreDb.fetch_or_create_unique_appointment(
                visa_type_id, center_name, book_now_link, visa_category,
                visa_subcategory, source_country, mission_country, appointment_date
            )

            if postgres_id:
                # Eğer PostgreSQL'de kayıt başarılı olduysa, SQLite'a ekle
                self.sqliteDb.fetch_or_create_unique_appointment(
                    visa_type_id, center_name, book_now_link, visa_category,
                    visa_subcategory, source_country, mission_country
                )

            return postgres_id
        except Exception as e:
            print(f"Error in fetch_or_create_unique_appointment: {e}")
            return None


    def insert_appointment_log(self, data):
        """
        Hem PostgreSQL hem de SQLite üzerinde appointment log ekler.
        Sadece PostgreSQL'e ekleme başarılı olursa SQLite'a ekler.
        """
        try:
            # PostgreSQL'de log ekleme ve ID alma
            postgres_id = self.postgreDb.insert_appointment_log(data)
            
            # Eğer PostgreSQL'e ekleme başarılı olduysa SQLite'a ekle
            if postgres_id:
                self.sqliteDb.insert_appointment_log(data)
                print(f"Log başarıyla hem PostgreSQL hem de SQLite'a eklendi. ID: {postgres_id}")
            else:
                print("Log zaten PostgreSQL'de mevcut, SQLite'a ekleme yapılmadı.")
        except Exception as e:
            print(f"insert_appointment_log işleminde hata: {e}")


    def get_last_response(self):
        return self.sqliteDb.get_last_response()

    def insert_processed_response(self, response_id, timestamp):
        self.postgreDb.insert_processed_response(response_id, timestamp)
        self.sqliteDb.insert_processed_response(response_id, timestamp)

if __name__ == "__main__":
    db = Database()
    db.responseProcessor.process_all_unprocessed_responses()