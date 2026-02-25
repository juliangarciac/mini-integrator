import json
import sqlite3


UPSERT_USER = """
INSERT INTO users (source, external_id, full_name, username, username_norm, email, email_norm, city, synced_at, raw_payload)
VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
ON CONFLICT(source, external_id) DO UPDATE SET
  full_name=excluded.full_name,
  username=excluded.username,
  username_norm=excluded.username_norm,
  email=excluded.email,
  email_norm=excluded.email_norm,
  city=excluded.city,
  synced_at=excluded.synced_at,
  raw_payload=excluded.raw_payload;
"""

GET_USER_ID = """
SELECT id FROM users WHERE source=? AND external_id=?;
"""

UPSERT_POST = """
INSERT INTO posts (source, external_id, user_id, external_user_id, title, title_norm, body_clean, synced_at, raw_payload)
VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
ON CONFLICT(source, external_id) DO UPDATE SET
  user_id=excluded.user_id,
  external_user_id=excluded.external_user_id,
  title=excluded.title,
  title_norm=excluded.title_norm,
  body_clean=excluded.body_clean,
  synced_at=excluded.synced_at,
  raw_payload=excluded.raw_payload;
"""


def upsert_user(cur: sqlite3.Cursor, row: dict) -> None:
    cur.execute(
        UPSERT_USER,
        (
            row["source"],
            row["external_id"],
            row["full_name"],
            row.get("username"),
            row.get("username_norm"),
            row.get("email"),
            row.get("email_norm"),
            row.get("city"),
            row["synced_at"],
            json.dumps(row.get("raw_payload"), ensure_ascii=False),
        ),
    )


def get_user_id(cur: sqlite3.Cursor, source: str, external_id: int) -> int | None:
    cur.execute(GET_USER_ID, (source, external_id))
    r = cur.fetchone()
    return int(r["id"]) if r else None


def upsert_post(cur: sqlite3.Cursor, row: dict) -> None:
    cur.execute(
        UPSERT_POST,
        (
            row["source"],
            row["external_id"],
            row["user_id"],
            row["external_user_id"],
            row.get("title"),
            row.get("title_norm"),
            row.get("body_clean"),
            row["synced_at"],
            json.dumps(row.get("raw_payload"), ensure_ascii=False),
        ),
    )