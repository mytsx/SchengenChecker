SELECT unique_appointment_id,  appointment_date, people_looking, last_checked, COUNT(*)
FROM appointment_logs
GROUP BY unique_appointment_id,  appointment_date, people_looking, last_checked
HAVING COUNT(*) > 1;


SELECT
    unique_appointment_id,
    appointment_date,
    people_looking,
    DATE_TRUNC('second', last_checked) AS last_checked_rounded,
    COUNT(*) AS tekrar_sayisi
FROM
    appointment_logs
GROUP BY
    unique_appointment_id,
    appointment_date,
    people_looking,
    DATE_TRUNC('second', last_checked)
HAVING
    COUNT(*) > 1;


CREATE TEMP TABLE temp_appointment_logs AS
SELECT DISTINCT ON (unique_appointment_id, appointment_date, people_looking, last_checked)
    *
FROM appointment_logs
ORDER BY unique_appointment_id, appointment_date, people_looking, last_checked, id;

select * from temp_appointment_logs;

-- Orijinal tabloyu temizle
TRUNCATE TABLE appointment_logs;

-- Tekil kayıtları geri yükle
INSERT INTO appointment_logs
SELECT * FROM temp_appointment_logs;

-- Temp tabloyu kaldır
DROP TABLE temp_appointment_logs;