CREATE TABLE IF NOT EXISTS responses (
    id SERIAL PRIMARY KEY,
    timestamp TIMESTAMP NOT NULL,
    response JSONB NOT NULL 
);

CREATE TABLE IF NOT EXISTS logs (
    id SERIAL PRIMARY KEY,
    timestamp TIMESTAMP NOT NULL,
    message TEXT NOT NULL  
);

CREATE TABLE IF NOT EXISTS appointments (
    id SERIAL PRIMARY KEY,
    timestamp TIMESTAMP NOT NULL,
    message TEXT NOT NULL 
);

CREATE TABLE IF NOT EXISTS unique_appointments (
    id BIGSERIAL PRIMARY KEY,
    center_name TEXT NOT NULL,
    visa_type_id INTEGER NOT NULL,
    visa_category TEXT NOT NULL,
    visa_subcategory TEXT,
    source_country TEXT,
    mission_country TEXT,
    book_now_link TEXT,
    CONSTRAINT unique_visa_appointment UNIQUE (
        visa_type_id,
        center_name,
        visa_category,
        visa_subcategory
    )
);

CREATE TABLE IF NOT EXISTS appointment_logs (
    id BIGSERIAL PRIMARY KEY,
    unique_appointment_id BIGINT REFERENCES unique_appointments(id) ON DELETE CASCADE,
    timestamp TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    appointment_date DATE,
    people_looking INTEGER,
    last_checked TIMESTAMP NOT NULL
);

CREATE TABLE IF NOT EXISTS processed_responses (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    response_id INTEGER NOT NULL,
    timestamp TEXT NOT NULL,
    processed_at TEXT NOT NULL,
    FOREIGN KEY (response_id) REFERENCES responses(id)
);