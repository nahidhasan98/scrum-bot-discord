import os
import sqlite3
from dotenv import load_dotenv
from config import db

load_dotenv()

def get_all():
    connection = db.get_db()
    try:
        connection.row_factory = sqlite3.Row
        cursor = connection.cursor()
        query = """
        SELECT * FROM questions
        ORDER BY id;
        """

        cursor.execute(query)
        results = cursor.fetchall()
        
        # if os.getenv('MODE') == "dev":
        #     print(f'question_all = {results}')
            
        return results

    except(Exception) as error:
        print(error)
        
    finally:
        connection.close()