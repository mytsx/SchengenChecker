from postgres_database import PostgresDatabase
from sqlite_database import SQLiteDatabase

class Database:

    def __init__(self):
        self.postgreDb = PostgresDatabase()
        self.sqliteDb = SQLiteDatabase()


    def log_to_table(self, table_name, data):
        self.postgreDb.log_to_table(table_name, data)
        self.postgreDb.log_to_table(table_name, data)


    def fetch_table_data(self, table_name, limit=10, json_column=False):
        return self.sqliteDb.fetch_table_data(table_name,limit,json_column)


    def fetch_responses_from_postgres(self, limit=500):
        return self.sqliteDb.fetch_responses(limit=limit)


    def fetch_or_create_unique_appointment(self, visa_type_id, center_name, book_now_link,
                                           visa_category, visa_subcategory, source_country, mission_country):
        """
        Hem PostgreSQL hem SQLite üzerinde benzersiz appointment kontrolü yapar veya oluşturur.
        """
        postgres_id = self.postgreDb.fetch_or_create_unique_appointment(
            visa_type_id, center_name, book_now_link,
            visa_category, visa_subcategory, source_country, mission_country
        )
        self.sqliteDb.fetch_or_create_unique_appointment(
            visa_type_id, center_name, book_now_link,
            visa_category, visa_subcategory, source_country, mission_country
        )
        return postgres_id

    def insert_appointment_log(self, data):
        """
        Hem PostgreSQL hem de SQLite üzerinde appointment log ekler.
        """
        self.postgreDb.insert_appointment_log(data)
        self.sqliteDb.insert_appointment_log(data)

    def get_last_response(self):
        return self.sqliteDb.get_last_response()
    
    def insert_processed_response(self, response_id, timestamp):
        self.postgreDb.insert_processed_response(response_id, timestamp)
        self.sqliteDb.insert_processed_response(response_id, timestamp)
