
CREATE TABLE IF NOT EXISTS Users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER,
    name VARCHAR(50),
    password VARCHAR(50),
    has_admin_rights BOOLEAN
);

CREATE TABLE IF NOT EXISTS Todos (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER,
    todo_text TEXT,
    FOREIGN KEY (user_id) REFERENCES Users(user_id)
);

INSERT INTO Users (name, password, has_admin_rights) VALUES ('admin', 'admin_pass', TRUE);
