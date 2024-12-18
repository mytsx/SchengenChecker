-- UNIQUE constraint geçici olarak kaldırılır.
-- Bu, güncelleme sırasında UNIQUE constraint ihlallerini önlemek içindir.
ALTER TABLE appointment_logs DROP CONSTRAINT unique_appointment_log;

-- Tekrarlanan unique_appointments kayıtları bulunur ve her grupta en küçük id (keep_id) korunur.
-- duplicate_ids: Aynı kombinasyona sahip id'ler
-- keep_id: Tekil olarak tutulacak id
WITH cte AS (
    SELECT
        MIN(id) AS keep_id,
        ARRAY_AGG(id) AS duplicate_ids
    FROM unique_appointments
    GROUP BY visa_type_id, center_name, visa_category, visa_subcategory, book_now_link, source_country, mission_country
    HAVING COUNT(*) > 1
)
-- appointment_logs tablosundaki unique_appointment_id değerlerini günceller.
-- duplicate_ids içindeki id'ler keep_id ile değiştirilir.
UPDATE appointment_logs AS al
SET unique_appointment_id = cte.keep_id
FROM cte
WHERE al.unique_appointment_id = ANY(cte.duplicate_ids)
  AND al.unique_appointment_id != cte.keep_id;

-- appointment_logs tablosunda her unique_appointment_id, appointment_date, people_looking ve last_checked kombinasyonu için tek bir kayıt tutulur.
-- Geçici bir tablo oluşturulur ve sadece DISTINCT kayıtlar eklenir.
CREATE TEMP TABLE temp_appointment_logs AS
SELECT DISTINCT ON (unique_appointment_id, appointment_date, people_looking, last_checked)
    *
FROM appointment_logs
ORDER BY unique_appointment_id, appointment_date, people_looking, last_checked, id;

-- Geçici tabloyu kontrol etmek için
SELECT * FROM temp_appointment_logs;

-- Orijinal appointment_logs tablosunu temizler.
TRUNCATE TABLE appointment_logs;

-- Geçici tabloda tutulan tekil kayıtları tekrar appointment_logs tablosuna ekler.
INSERT INTO appointment_logs
SELECT * FROM temp_appointment_logs;

-- Geçici tabloyu kaldırır.
DROP TABLE temp_appointment_logs;

-- UNIQUE constraint tekrar eklenir.
-- unique_appointment_id, appointment_date, people_looking ve last_checked kombinasyonlarının benzersizliği sağlanır.
ALTER TABLE appointment_logs ADD CONSTRAINT unique_appointment_log
    UNIQUE (unique_appointment_id, appointment_date, people_looking, last_checked);

-- Tekrarlanan unique_appointments kayıtlarını kontrol eder.
-- duplicate_ids içindeki id'ler aynı kombinasyona sahip unique_appointments kayıtlarıdır.
SELECT
    MIN(id) AS keep_id,  -- Tekil kaydın en küçük id'si
    ARRAY_AGG(id) AS duplicate_ids,  -- Tekrarlanan id'ler
    visa_type_id,
    center_name,
    visa_category,
    visa_subcategory,
    book_now_link,
    source_country,
    mission_country,
    COUNT(*) AS tekrar_sayisi
FROM unique_appointments
GROUP BY visa_type_id, center_name, visa_category, visa_subcategory, book_now_link, source_country, mission_country
HAVING COUNT(*) > 1;

-- duplicate_ids listesindeki id'ler ve keep_id yeniden kontrol edilir.
SELECT
    MIN(id) AS keep_id,
    ARRAY_AGG(id) AS duplicate_ids
FROM unique_appointments
GROUP BY visa_type_id, center_name, visa_category, visa_subcategory, book_now_link, source_country, mission_country
HAVING COUNT(*) > 1;

-- appointment_logs ile ilişkisi olmayan duplicate_ids kayıtlarını silmek için:
-- duplicate_ids içindeki id'ler tespit edilir ve yalnızca keep_id hariç olanlar hedeflenir.
-- appointment_logs ile ilişkisi olmayan unique_appointments kayıtları belirlenir.
WITH duplicates AS (
    SELECT
        MIN(id) AS keep_id,
        ARRAY_AGG(id) AS duplicate_ids
    FROM unique_appointments
    GROUP BY visa_type_id, center_name, visa_category, visa_subcategory, book_now_link, source_country, mission_country
    HAVING COUNT(*) > 1
)
SELECT *
FROM unique_appointments
WHERE id IN (
    SELECT unnest(duplicate_ids)
    FROM duplicates
    WHERE id != keep_id
)
  AND id NOT IN (
    SELECT DISTINCT unique_appointment_id
    FROM appointment_logs
);


-- sonrasında bu kayıtlar silinir
WITH duplicates AS (
    SELECT
        MIN(id) AS keep_id,       -- Tekil olarak tutulacak id
        ARRAY_AGG(id) AS duplicate_ids -- Tekrarlanan tüm id'ler
    FROM unique_appointments
    GROUP BY visa_type_id, center_name, visa_category, visa_subcategory, book_now_link, source_country, mission_country
    HAVING COUNT(*) > 1
)
DELETE FROM unique_appointments
WHERE id IN (
    SELECT unnest(duplicate_ids)
    FROM duplicates
    WHERE id != keep_id  -- Tekil olanı silme
)
  AND id NOT IN (
    SELECT DISTINCT unique_appointment_id
    FROM appointment_logs
);
