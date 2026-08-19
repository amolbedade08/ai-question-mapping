import sqlite3
from pathlib import Path


DATABASE_PATH = Path("output/mapping.db")


def get_connection():
    """Create and return a database connection."""
    DATABASE_PATH.parent.mkdir(parents=True, exist_ok=True)

    return sqlite3.connect(DATABASE_PATH)


def create_tables():
    """Create the question mapping table if it does not exist."""

    connection = get_connection()

    cursor = connection.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS question_mappings (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            student_id TEXT NOT NULL,
            student_question TEXT NOT NULL,
            matched_model_question TEXT,
            similarity REAL,
            number_match BOOLEAN,
            threshold_used REAL,
            status TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)

    connection.commit()
    connection.close()


def save_mapping(student_id, question_id, mapping):
    """Save one question mapping into the database."""

    connection = get_connection()

    cursor = connection.cursor()

    cursor.execute("""
        INSERT INTO question_mappings (
            student_id,
            student_question,
            matched_model_question,
            similarity,
            number_match,
            threshold_used,
            status
        )
        VALUES (?, ?, ?, ?, ?, ?, ?)
    """, (
        student_id,
        question_id,
        mapping.get("matched_model_question"),
        mapping.get("similarity", 0.0),
        mapping.get("number_match", False),
        mapping.get("threshold_used", 0.0),
        mapping.get("status")
    ))

    connection.commit()
    connection.close()


def get_mappings(student_id):
    """Retrieve all mappings for a student."""

    connection = get_connection()

    cursor = connection.cursor()

    cursor.execute("""
        SELECT
            student_question,
            matched_model_question,
            similarity,
            number_match,
            threshold_used,
            status,
            created_at
        FROM question_mappings
        WHERE student_id = ?
        ORDER BY student_question
    """, (student_id,))

    rows = cursor.fetchall()

    connection.close()

    return rows
def get_student_mappings(student_id):
    """Retrieve all mappings for a student as a list of dictionaries."""

    connection = get_connection()

    cursor = connection.cursor()

    cursor.execute("""
        SELECT
            student_question,
            matched_model_question,
            similarity,
            number_match,
            threshold_used,
            status,
            created_at
        FROM question_mappings
        WHERE student_id = ?
        ORDER BY student_question
    """, (student_id,))

    rows = cursor.fetchall()

    connection.close()

    mappings = []

    for row in rows:
        mappings.append({
            "student_question": row[0],
            "matched_model_question": row[1],
            "similarity": row[2],
            "number_match": bool(row[3]),
            "threshold": row[4],
            "status": row[5],
            "created_at": row[6]
        })

    return mappings