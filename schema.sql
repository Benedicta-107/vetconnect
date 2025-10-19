PRAGMA foreign_keys = ON;

CREATE TABLE IF NOT EXISTS users (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  name TEXT NOT NULL,
  email TEXT NOT NULL UNIQUE,
  password_hash TEXT NOT NULL,
  is_admin INTEGER NOT NULL DEFAULT 0
);

CREATE TABLE IF NOT EXISTS appointments (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  user_id INTEGER NOT NULL,
  pet_name TEXT NOT NULL,
  service TEXT NOT NULL,
  date TEXT NOT NULL,   -- ISO: YYYY-MM-DD
  time TEXT NOT NULL,   -- HH:MM
  status TEXT NOT NULL DEFAULT 'pending', -- pending|confirmed|cancelled
  created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
  FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS messages (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  name TEXT NOT NULL,
  email TEXT NOT NULL,
  message TEXT NOT NULL,
  submitted_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
);

ALTER TABLE appointments ADD COLUMN hidden_by_user  INTEGER DEFAULT 0;
ALTER TABLE appointments ADD COLUMN hidden_by_admin INTEGER DEFAULT 0;
/* To do later: create an initial admin account later via the app or manually */
