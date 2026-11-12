import logging
import sqlite3
from contextlib import closing
from pathlib import Path
from typing import Any


DATABASE_PATH = Path(__file__).resolve().parent / "feedback.db"
logger = logging.getLogger(__name__)


def _connect() -> sqlite3.Connection:
    connection = sqlite3.connect(DATABASE_PATH)
    connection.row_factory = sqlite3.Row
    return connection


def initialize_database() -> None:
    """Create the feedback table if it does not already exist."""
    try:
        with closing(_connect()) as connection:
            with connection:
                connection.execute(
                    """
                    CREATE TABLE IF NOT EXISTS feedback (
                        feedback_id INTEGER PRIMARY KEY AUTOINCREMENT,
                        student_name TEXT NOT NULL,
                        course_name TEXT NOT NULL,
                        rating INTEGER NOT NULL CHECK (rating BETWEEN 1 AND 5),
                        comments TEXT
                    )
                    """
                )
    except sqlite3.Error as exc:
        logger.exception("Could not initialize the feedback database")
        raise RuntimeError("Could not initialize the feedback database") from exc


def insert_feedback(
    student_name: str,
    course_name: str,
    rating: int,
    comments: str | None = None,
) -> int:
    """Insert a feedback record and return its generated ID."""
    if not isinstance(student_name, str) or not student_name.strip():
        raise ValueError("Student name is required.")
    if not isinstance(course_name, str) or not course_name.strip():
        raise ValueError("Course name is required.")
    if type(rating) is not int or not 1 <= rating <= 5:
        raise ValueError("Rating must be an integer from 1 to 5.")
    if comments is not None and not isinstance(comments, str):
        raise ValueError("Comments must be text or None.")

    try:
        with closing(_connect()) as connection:
            with connection:
                cursor = connection.execute(
                    """
                    INSERT INTO feedback (student_name, course_name, rating, comments)
                    VALUES (?, ?, ?, ?)
                    """,
                    (student_name.strip(), course_name.strip(), rating, comments),
                )
                feedback_id = cursor.lastrowid
                if feedback_id is None:
                    raise RuntimeError("The feedback record was not assigned an ID.")
                return feedback_id
    except sqlite3.Error as exc:
        logger.exception("Could not insert feedback")
        raise RuntimeError("Could not insert feedback") from exc


def get_all_feedback() -> list[dict[str, Any]]:
    """Return all feedback records in insertion order."""
    try:
        with closing(_connect()) as connection:
            rows = connection.execute(
                """
                SELECT feedback_id, student_name, course_name, rating, comments
                FROM feedback
                ORDER BY feedback_id
                """
            ).fetchall()
            return [dict(row) for row in rows]
    except sqlite3.Error as exc:
        logger.exception("Could not retrieve feedback")
        raise RuntimeError("Could not retrieve feedback") from exc


def calculate_average_rating() -> float | None:
    """Return the average of all ratings, or None when no feedback exists."""
    try:
        with closing(_connect()) as connection:
            row = connection.execute(
                "SELECT AVG(rating) AS average_rating FROM feedback"
            ).fetchone()
            return row["average_rating"]
    except sqlite3.Error as exc:
        logger.exception("Could not calculate the average rating")
        raise RuntimeError("Could not calculate the average rating") from exc


def get_highest_rated_course() -> list[dict[str, Any]]:
    """Return all courses tied for the highest average rating."""
    try:
        with closing(_connect()) as connection:
            rows = connection.execute(
                """
                SELECT course_name, AVG(rating) AS average_rating
                FROM feedback
                GROUP BY course_name
                HAVING AVG(rating) = (
                    SELECT MAX(course_average)
                    FROM (
                        SELECT AVG(rating) AS course_average
                        FROM feedback
                        GROUP BY course_name
                    )
                )
                ORDER BY course_name
                """
            ).fetchall()
            return [dict(row) for row in rows]
    except sqlite3.Error as exc:
        logger.exception("Could not identify the highest-rated course")
        raise RuntimeError("Could not identify the highest-rated course") from exc


def get_course_wise_summary() -> list[dict[str, Any]]:
    """Return each course's average rating and number of feedback records."""
    try:
        with closing(_connect()) as connection:
            rows = connection.execute(
                """
                SELECT
                    course_name,
                    AVG(rating) AS average_rating,
                    COUNT(*) AS feedback_count
                FROM feedback
                GROUP BY course_name
                ORDER BY course_name
                """
            ).fetchall()
            return [dict(row) for row in rows]
    except sqlite3.Error as exc:
        logger.exception("Could not generate the course-wise summary")
        raise RuntimeError("Could not generate the course-wise summary") from exc
