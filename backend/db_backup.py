import sqlite3
import os

BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
DB_PATH = os.path.join(BASE_DIR, "data", "backup.db")


def get_connection():
    conn = sqlite3.connect(DB_PATH)
    return conn


def init_db():
    conn = get_connection()
    cur = conn.cursor()

    # Users table (backup)
    cur.execute("""
    CREATE TABLE IF NOT EXISTS users_backup (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT,
        role TEXT,
        timestamp TEXT
    )
    """)

    # Audit table (backup)
    cur.execute("""
    CREATE TABLE IF NOT EXISTS audit_backup (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user TEXT,
        action TEXT,
        timestamp TEXT
    )
    """)

    conn.commit()
    conn.close()
