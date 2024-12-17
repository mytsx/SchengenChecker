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
    sync_indexes(postgres_db, sqlite_db)


def sync_indexes(postgres_db, sqlite_db):
    """
    PostgreSQL'deki index'leri SQLite'a senkronize eder.
    """
    print("Index senkronizasyonu başlatılıyor...")

    # PostgreSQL'den index bilgilerini al
    index_query = """
        SELECT 
            tablename, 
            indexname, 
            indexdef
        FROM 
            pg_indexes 
        WHERE 
            schemaname = 'public';
    """
    try:
        conn_pg = postgres_db.connect()
        cursor_pg = conn_pg.cursor()
        cursor_pg.execute(index_query)
        indexes = cursor_pg.fetchall()

        for tablename, indexname, indexdef in indexes:
            print(f"Index bulundu: {indexname} ({tablename})")
            
            # PostgreSQL index tanımını SQLite'a dönüştür
            # 'USING' gibi ifadeleri kaldır ve SQLite formatına dönüştür
            sqlite_index_def = (
                indexdef.replace("USING GIN", "")  # PostgreSQL özel index türünü kaldır
                        .replace("USING BTREE", "")
                        .replace("public.", "")
                        .replace("USING btree", "")
                        .replace("USING gin", "")
            )

            # CREATE INDEX ifadesini SQLite'a uygula
            try:
                conn_sqlite = sqlite_db.connect()
                cursor_sqlite = conn_sqlite.cursor()
                cursor_sqlite.execute(sqlite_index_def)
                conn_sqlite.commit()
                print(f"Index uygulandı: {indexname}")
            except Exception as e:
                print(f"SQLite index oluşturulurken hata: {e}")
            finally:
                cursor_sqlite.close()
                conn_sqlite.close()
                
    except Exception as e:
        print(f"PostgreSQL index bilgileri alınırken hata: {e}")
    finally:
        cursor_pg.close()
        conn_pg.close()


if __name__ == "__main__":
    sync_schemas_and_data()
