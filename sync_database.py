from postgres_database import PostgresDatabase
from sqlite_database import SQLiteDatabase
import os

def recreate_sqlite_db(sqlite_db_path):
    """
    SQLite veritabanını siler ve yeniden oluşturur.
    """
    if os.path.exists(sqlite_db_path):
        os.remove(sqlite_db_path)  # Mevcut veritabanını sil
        print(f"SQLite veritabanı silindi: {sqlite_db_path}")
    else:
        print(f"SQLite veritabanı mevcut değil: {sqlite_db_path}")
    print("Yeni SQLite veritabanı oluşturulacak.")


def sync_schemas_and_data():
    """
    PostgreSQL'deki tabloları ve verileri SQLite'a senkronize eder.
    SQLite her seferinde yeniden oluşturulur.
    """
    postgres_db = PostgresDatabase()
    sqlite_db = SQLiteDatabase()

    # 1. SQLite veritabanını yeniden oluştur
    sqlite_db_path = sqlite_db.db_file  # SQLite dosya yolu
    recreate_sqlite_db(sqlite_db_path)

    # 2. PostgreSQL'deki tabloları al
    tables_to_sync = postgres_db.get_all_table_names()

    for table_name in tables_to_sync:
        print(f"Şema senkronize ediliyor: {table_name}")
        schema = postgres_db.get_table_schema(table_name)

        if schema:
            # SQLite'da tabloyu oluştur
            sqlite_db.create_table_from_schema(table_name, schema)
            print(f"{table_name} tablosu oluşturuldu.")

            # 3. PostgreSQL'den verileri oku ve SQLite'a yaz
            print(f"{table_name} tablosundan veriler aktarılıyor...")
            rows = postgres_db.fetch_all_data(table_name)

            if rows:
                sqlite_db.insert_bulk_data(table_name, schema, rows)
                print(f"{table_name} tablosundan {len(rows)} kayıt aktarıldı.")
            else:
                print(f"{table_name} tablosunda veri bulunamadı.")
        else:
            print(f"{table_name} için şema bulunamadı.")

    print("Tüm veriler başarıyla senkronize edildi.")


if __name__ == "__main__":
    sync_schemas_and_data()
