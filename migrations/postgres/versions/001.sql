CREATE TABLE IF NOT EXISTS admin (
    id SERIAL PRIMARY KEY,
    user_id BIGINT NOT NULL
);

CREATE TABLE IF NOT EXISTS user_ (
    id SERIAL PRIMARY KEY,
    user_id BIGINT NOT NULL UNIQUE,
    username TEXT,
    attempts SMALLINT NOT NULL DEFAULT 3
);

CREATE TABLE IF NOT EXISTS quiz (
    id SERIAL PRIMARY KEY,
    direction TEXT,
    question TEXT NOT NULL,
    link TEXT,
    correct_answer_id SMALLINT NOT NULL,
    note TEXT
);

CREATE TABLE IF NOT EXISTS answer (
    id SERIAL PRIMARY KEY,
    quiz_id INTEGER,
    text TEXT NOT NULL,
    FOREIGN KEY (quiz_id) REFERENCES quiz(id) ON DELETE CASCADE
);
