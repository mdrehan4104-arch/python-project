import sqlite3
from pathlib import Path

DB_PATH = Path(__file__).parent / "wastewise.db"


def get_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    """Create the food-waste table if it does not already exist."""
    with get_connection() as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS food_logs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                date TEXT NOT NULL,
                meal TEXT NOT NULL CHECK (meal IN ('Breakfast', 'Lunch', 'Snacks', 'Dinner')),
                food_item TEXT NOT NULL,
                prepared_kg REAL NOT NULL CHECK (prepared_kg > 0),
                served_kg REAL NOT NULL CHECK (served_kg >= 0),
                leftover_kg REAL NOT NULL CHECK (leftover_kg >= 0),
                notes TEXT DEFAULT '',
                created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                CHECK (served_kg + leftover_kg <= prepared_kg + 0.000001)
            )
        """)
        conn.commit()


def add_record(date, meal, food_item, prepared_kg, served_kg, leftover_kg, notes=""):
    with get_connection() as conn:
        conn.execute("""
            INSERT INTO food_logs
                (date, meal, food_item, prepared_kg, served_kg, leftover_kg, notes)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (date, meal, food_item, prepared_kg, served_kg, leftover_kg, notes))
        conn.commit()


def fetch_records():
    with get_connection() as conn:
        rows = conn.execute("""
            SELECT id, date, meal, food_item, prepared_kg, served_kg,
                   leftover_kg, notes, created_at
            FROM food_logs
            ORDER BY date DESC, id DESC
        """).fetchall()
        return [dict(row) for row in rows]


def update_record(record_id, date, meal, food_item, prepared_kg, served_kg, leftover_kg, notes=""):
    with get_connection() as conn:
        conn.execute("""
            UPDATE food_logs
            SET date=?, meal=?, food_item=?, prepared_kg=?, served_kg=?,
                leftover_kg=?, notes=?
            WHERE id=?
        """, (date, meal, food_item, prepared_kg, served_kg, leftover_kg, notes, record_id))
        conn.commit()


def delete_record(record_id):
    with get_connection() as conn:
        conn.execute("DELETE FROM food_logs WHERE id=?", (record_id,))
        conn.commit()


def insert_many(records):
    """Insert validated dictionaries; useful for tests or sample data."""
    with get_connection() as conn:
        conn.executemany("""
            INSERT INTO food_logs
                (date, meal, food_item, prepared_kg, served_kg, leftover_kg, notes)
            VALUES (:date, :meal, :food_item, :prepared_kg, :served_kg, :leftover_kg, :notes)
        """, records)
        conn.commit()
