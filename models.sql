CREATE TABLE IF NOT EXISTS users (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  source TEXT NOT NULL,
  external_id INTEGER NOT NULL,
  full_name TEXT NOT NULL,
  username TEXT,
  username_norm TEXT,
  email TEXT,
  email_norm TEXT,
  city TEXT,
  synced_at TEXT NOT NULL,
  raw_payload TEXT,
  UNIQUE(source, external_id)
);

CREATE TABLE IF NOT EXISTS posts (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  source TEXT NOT NULL,
  external_id INTEGER NOT NULL,
  user_id INTEGER NOT NULL,
  external_user_id INTEGER NOT NULL,
  title TEXT,
  title_norm TEXT,
  body_clean TEXT,
  synced_at TEXT NOT NULL,
  raw_payload TEXT,
  UNIQUE(source, external_id),
  FOREIGN KEY(user_id) REFERENCES users(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS integration_runs (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  started_at TEXT NOT NULL,
  finished_at TEXT,
  status TEXT NOT NULL,
  source TEXT NOT NULL,
  processed_users INTEGER DEFAULT 0,
  processed_posts INTEGER DEFAULT 0,
  upserted_users INTEGER DEFAULT 0,
  upserted_posts INTEGER DEFAULT 0,
  error_message TEXT,
  duration_ms INTEGER
);