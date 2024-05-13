CREATE TABLE IF NOT EXISTS Users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name VARCHAR(50) UNIQUE,
    password VARCHAR(50)
);

CREATE TABLE IF NOT EXISTS Todos (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER,
    todo_text TEXT,
    todo_date DATE,
    FOREIGN KEY(user_id) REFERENCES Users(id)
);

INSERT INTO Users (id, name, password) VALUES (1, 'admin', 'password');
