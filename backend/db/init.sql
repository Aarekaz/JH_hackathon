CREATE TABLE debates (
    id SERIAL PRIMARY KEY,
    title VARCHAR(255),
    status VARCHAR(50),
    created_at TIMESTAMP
);

CREATE TABLE mp_responses (
    id SERIAL PRIMARY KEY,
    debate_id INTEGER,
    mp_role VARCHAR(100),
    content TEXT,
    timestamp TIMESTAMP
);