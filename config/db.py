import os
import sqlite3
from dotenv import load_dotenv
from service.logger import logger

load_dotenv()


def get_db():
    return sqlite3.connect(os.getenv("DB_FILE"))


def init():
    connection = get_db()
    try:
        cursor = connection.cursor()

        # Create users table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                discord_username TEXT NOT NULL,
                discord_display_name TEXT,
                discord_user_id TEXT UNIQUE
            )
        """)

        # Create questions table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS questions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                question TEXT NOT NULL,
                tag TEXT
            )
        """)

        # Create records table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS records (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                date DATE NOT NULL,
                user_id INTEGER NOT NULL,
                module TEXT,
                goal TEXT,
                updates TEXT,
                comments TEXT,
                has_started INTEGER COMMENT '0=Not Started, 1=Started, 2=Completed',
                FOREIGN KEY (user_id) REFERENCES users(id)
            )
        """)

        # Check if the questions table is empty
        cursor.execute("SELECT COUNT(*) FROM questions")
        question_count = cursor.fetchone()[0]

        # Insert initial data into questions table if it's empty
        if question_count == 0:
            questions = [
                ('Which module are you working on?', 'module',),
                ('What tasks have you been assigned for today?\n[For multiple tasks, use semicolon (;) as separator.]', 'goal',),
                # sub question according to 2nd question
                ('Have you completed the task', 'updates',),
                # sub question according to 2nd question
                ('Any blockers/comments regarding this task?', 'comments',)
            ]
            cursor.executemany(
                "INSERT INTO questions (question, tag) VALUES (?, ?)", questions)
            logger.info("Initial questions inserted.")

        # Commit the changes
        connection.commit()

        # Verify if tables are created successfully
        cursor.execute(
            "SELECT name FROM sqlite_master WHERE type='table' AND name='users'")
        if cursor.fetchone() is None:
            logger.error("Error: 'users' table was not created successfully.")

        cursor.execute(
            "SELECT name FROM sqlite_master WHERE type='table' AND name='questions'")
        if cursor.fetchone() is None:
            logger.error(
                "Error: 'questions' table was not created successfully.")

        cursor.execute(
            "SELECT name FROM sqlite_master WHERE type='table' AND name='records'")
        if cursor.fetchone() is None:
            logger.error(
                "Error: 'records' table was not created successfully.")

        logger.info("Database initialized successfully.")

    except sqlite3.Error as e:
        logger.error(f"An error occurred: {e}")

    finally:
        connection.close()
