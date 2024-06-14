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
        SELECT * FROM users
        ORDER BY id;
        """

        cursor.execute(query)
        results = cursor.fetchall()
            
        # if os.getenv('MODE') == "dev":
        #     print(f'user_all = {results}')
            
        return results

    except(Exception) as error:
        print(error)
        
    finally:
        connection.close()

def get(**kwargs):
    id = kwargs.get("id", "")
    discord_user_id = kwargs.get("discord_user_id", "")

    connection = db.get_db()
    try:
        connection.row_factory = sqlite3.Row
        cursor = connection.cursor()
        if id != "":
            query = """
            SELECT * FROM users
            WHERE id = ?;
            """
            cursor.execute(query, (id,))
        else:
            query = """
            SELECT * FROM users
            WHERE discord_user_id = ?;
            """
            cursor.execute(query, (discord_user_id,))

        results = cursor.fetchall()
        
        # if os.getenv('MODE') == "dev":
        #     print(f'user = {results}')
            
        return results

    except(Exception) as error:
        print(error)
        
    finally:
        connection.close()
        
def save(data):
    connection = db.get_db()
    try:
        connection.row_factory = sqlite3.Row
        cursor = connection.cursor()
        query = """
        SELECT id FROM users
        WHERE discord_user_id = ?;
        """

        cursor.execute(query, (data.id,))
        results = cursor.fetchall()
        
        if len(results) == 0:
            query = """
            INSERT INTO users (discord_username, discord_display_name, discord_user_id)
            VALUES (?, ?, ?);
            """

            cursor.execute(query, (data.name, data.global_name, data.id))
            connection.commit()
            
            data = f'New user({data.global_name}) info inserted into Database.'
        else:
            data = f'User({data.global_name}) info already exists in Database.'
            
        # if os.getenv('MODE') == "dev":
        #     print(f'user_info = {data}')
            
        return data

    except(Exception) as error:
        print(error)
        
    finally:
        connection.close()