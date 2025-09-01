CREATE TABLE transactions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    date TEXT NOT NULL,
    post_date TEXT,
    description TEXT NOT NULL,
    original_description TEXT,
    category TEXT,
    amount REAL NOT NULL,
    type TEXT,
    account TEXT,
    source TEXT NOT NULL,
    tags TEXT,
    memo TEXT
);