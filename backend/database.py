import sqlite3
import os
from pathlib import Path

DB_DIR = Path(__file__).parent.resolve()
DB_FILE = DB_DIR / "errandquest.db"

def get_connection():
    conn = sqlite3.connect(DB_FILE, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON;")
    return conn

def init_db():
    conn = get_connection()
    cursor = conn.cursor()

    cursor.executescript("""
    CREATE TABLE IF NOT EXISTS errands (
        id TEXT PRIMARY KEY,
        title TEXT NOT NULL,
        category TEXT NOT NULL DEFAULT 'General',
        urgency TEXT NOT NULL DEFAULT 'medium',
        deadline TEXT,
        notes TEXT,
        prep_items TEXT DEFAULT '[]',
        status TEXT NOT NULL DEFAULT 'pending',
        stop_id TEXT,
        created_at TEXT NOT NULL
    );

    CREATE TABLE IF NOT EXISTS stops (
        id TEXT PRIMARY KEY,
        name TEXT NOT NULL,
        category TEXT NOT NULL DEFAULT 'General',
        location_text TEXT,
        sequence_number INTEGER DEFAULT 0
    );

    CREATE TABLE IF NOT EXISTS trips (
        id TEXT PRIMARY KEY,
        name TEXT NOT NULL,
        status TEXT NOT NULL DEFAULT 'draft',
        created_at TEXT NOT NULL,
        completed_at TEXT
    );

    CREATE TABLE IF NOT EXISTS trip_items (
        id TEXT PRIMARY KEY,
        trip_id TEXT NOT NULL,
        errand_id TEXT NOT NULL,
        stop_id TEXT,
        completed INTEGER NOT NULL DEFAULT 0,
        completed_at TEXT,
        FOREIGN KEY (trip_id) REFERENCES trips (id) ON DELETE CASCADE,
        FOREIGN KEY (errand_id) REFERENCES errands (id) ON DELETE CASCADE
    );

    CREATE TABLE IF NOT EXISTS packing_items (
        id TEXT PRIMARY KEY,
        trip_id TEXT NOT NULL,
        label TEXT NOT NULL,
        checked INTEGER NOT NULL DEFAULT 0,
        FOREIGN KEY (trip_id) REFERENCES trips (id) ON DELETE CASCADE
    );
    """)

    conn.commit()
    conn.close()
