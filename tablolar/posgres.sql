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



CREATE INDEX idx_appointment_logs_query
    ON appointment_logs (unique_appointment_id, appointment_date, people_looking, last_checked);


-- responses
CREATE INDEX idx_responses_timestamp ON responses (timestamp);
CREATE INDEX idx_responses_response_jsonb ON responses USING GIN (response);

-- logs
CREATE INDEX idx_logs_timestamp ON logs (timestamp);

-- appointments
CREATE INDEX idx_appointments_timestamp ON appointments (timestamp);

-- unique_appointments
CREATE INDEX idx_unique_appointments_center ON unique_appointments (center_name);
CREATE INDEX idx_unique_appointments_visa ON unique_appointments (visa_type_id, visa_category, visa_subcategory);
CREATE INDEX idx_unique_appointments_country ON unique_appointments (source_country, mission_country);

-- appointment_logs
CREATE INDEX idx_appointment_logs_unique_id ON appointment_logs (unique_appointment_id);
CREATE INDEX idx_appointment_logs_date ON appointment_logs (appointment_date);
CREATE INDEX idx_appointment_logs_last_checked ON appointment_logs (last_checked);

-- processed_responses
CREATE INDEX idx_processed_responses_response_id ON processed_responses (response_id);
CREATE INDEX idx_processed_responses_timestamp ON processed_responses (timestamp);


ALTER TABLE appointment_logs ADD CONSTRAINT unique_appointment_log
    UNIQUE (unique_appointment_id, appointment_date, people_looking, last_checked);


ALTER TABLE unique_appointments DROP CONSTRAINT unique_visa_appointment;

ALTER TABLE unique_appointments ADD CONSTRAINT unique_visa_appointment
UNIQUE (visa_type_id, center_name, visa_category, visa_subcategory, source_country, mission_country);
