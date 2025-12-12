import sqlite3

DB_NAME = "students.db"


def get_connection():
    # Always use this to get a connection
    conn = sqlite3.connect(DB_NAME)
    # Enable foreign keys for safety
    conn.execute("PRAGMA foreign_keys = ON;")
    return conn


def setup_database():
    with get_connection() as conn:
        cursor = conn.cursor()

        # Students table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS students (
                roll INTEGER PRIMARY KEY,
                name TEXT NOT NULL,
                course TEXT NOT NULL
            )
        """)

        # Marks + result table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS results (
                roll INTEGER PRIMARY KEY,
                subject1 INTEGER NOT NULL,
                subject2 INTEGER NOT NULL,
                subject3 INTEGER NOT NULL,
                total INTEGER NOT NULL,
                percentage REAL NOT NULL,
                grade TEXT NOT NULL,
                status TEXT NOT NULL,
                FOREIGN KEY (roll) REFERENCES students(roll) ON DELETE CASCADE
            )
        """)

        conn.commit()
