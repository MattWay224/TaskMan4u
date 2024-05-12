CREATE TABLE IF NOT EXISTS Users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name VARCHAR(50) UNIQUE,
    password VARCHAR(50),
    has_admin_rights BOOLEAN
);

CREATE TABLE IF NOT EXISTS Todos (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER,
    todo_text TEXT,
    FOREIGN KEY (user_id) REFERENCES Users(id)
);