import os
import sqlite3
from dotenv import load_dotenv

load_dotenv()

def get_db():
    return sqlite3.connect(os.getenv("DB_NAME"))
        
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
                question TEXT NOT NULL
            )
        """)
        
        # Create records table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS records (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                date DATE NOT NULL,
                user_id INTEGER NOT NULL,
                question_id INTEGER,
                answer TEXT,
                discord_answer_id TEXT,
                has_started BOOLEAN,
                FOREIGN KEY (user_id) REFERENCES users(id),
                FOREIGN KEY (question_id) REFERENCES questions(id)
            )
        """)
        
         # Check if the questions table is empty
        cursor.execute("SELECT COUNT(*) FROM questions")
        question_count = cursor.fetchone()[0]

        # Insert initial data into questions table if it's empty
        if question_count == 0:
            questions = [
                ('What tasks have you been assigned for today?',),
                ('Which tasks have you completed?',),
                ('Are there any blockers you are facing?',)
            ]
            cursor.executemany("INSERT INTO questions (question) VALUES (?)", questions)
            print("Initial questions inserted.")
        
        # Commit the changes
        connection.commit()
        
        # Verify if tables are created successfully
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='users'")
        if cursor.fetchone() is None:
            print("Error: 'users' table was not created successfully.")
        
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='questions'")
        if cursor.fetchone() is None:
            print("Error: 'questions' table was not created successfully.")
        
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='records'")
        if cursor.fetchone() is None:
            print("Error: 'records' table was not created successfully.")
        
        print("Database initialized successfully.")
    
    except sqlite3.Error as e:
        print(f"An error occurred: {e}")
    
    finally:
        connection.close()