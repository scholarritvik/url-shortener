# database.py
import sqlite3

DB_NAME = "urls.db"


def get_connection():
    return sqlite3.connect(DB_NAME)


def init_db():
    conn = get_connection()
    c = conn.cursor()

    c.execute("""
        CREATE TABLE IF NOT EXISTS urls (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            original_url TEXT NOT NULL,
            short_code TEXT UNIQUE,
            clicks INTEGER DEFAULT 0,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            expires_at TIMESTAMP
        )
    """)

    conn.commit()
    conn.close()


# ---------- INSERT ----------
def insert_url_and_get_id(original_url: str) -> int:
    conn = get_connection()
    c = conn.cursor()

    c.execute(
        "INSERT INTO urls (original_url) VALUES (?)",
        (original_url,)
    )
    conn.commit()

    url_id = c.lastrowid
    conn.close()

    return url_id


def update_short_code(url_id: int, short_code: str):
    conn = get_connection()
    c = conn.cursor()

    c.execute(
        "UPDATE urls SET short_code=? WHERE id=?",
        (short_code, url_id)
    )
    conn.commit()
    conn.close()


# ---------- FETCH ----------
def get_url_by_code(code: str):
    conn = get_connection()
    c = conn.cursor()

    c.execute(
        "SELECT original_url, clicks FROM urls WHERE short_code=?",
        (code,)
    )
    row = c.fetchone()
    conn.close()

    return row


# ---------- UPDATE ----------
def increment_clicks(code: str, clicks: int):
    conn = get_connection()
    c = conn.cursor()

    c.execute(
        "UPDATE urls SET clicks=? WHERE short_code=?",
        (clicks + 1, code)
    )
    conn.commit()
    conn.close()