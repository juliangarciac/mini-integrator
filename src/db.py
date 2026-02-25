import os
import sqlite3
from pathlib import Path
from dotenv import load_dotenv


def get_db_path() -> Path:
    load_dotenv()
    db_path = os.environ.get("SQLITE_PATH", "integrator.db")
    return Path(db_path).resolve()


def get_conn() -> sqlite3.Connection:
    conn = sqlite3.connect(get_db_path())
    conn.row_factory = sqlite3.Row
    # En SQLite las FK están desactivadas por defecto; hay que activarlas.
    conn.execute("PRAGMA foreign_keys = ON;")
    return conn


def init_db() -> None:
    """
    Creates DB file (if missing) and applies schema from models.sql.
    Safe to run multiple times (idempotent) because schema uses IF NOT EXISTS.
    """
    schema_path = Path(__file__).resolve().parent.parent / "models.sql"
    if not schema_path.exists():
        raise FileNotFoundError(f"Schema file not found: {schema_path}")

    with get_conn() as conn:
        schema_sql = schema_path.read_text(encoding="utf-8")
        conn.executescript(schema_sql)
        conn.commit()


if __name__ == "__main__":
    init_db()
    print(f"DB initialized at: {get_db_path()}")