import os
import sqlite3
from dotenv import load_dotenv
from config import db
from service import users

load_dotenv()

def get_mark(discord_user_id, date):
    connection = db.get_db()
    try:
        connection.row_factory = sqlite3.Row
        cursor = connection.cursor()
        query = """
        SELECT records.id, records.has_started FROM records
        INNER JOIN users
        ON users.id = records.user_id
        WHERE users.discord_user_id = ?
        AND records.date = ?
        ORDER BY records.id;
        """

        cursor.execute(query, (discord_user_id, date))
        results = cursor.fetchall()
        data = True
        if len(results) == 0:
            data = False
        elif len(results) > 0:
            status = False
            
            for row in results:
                if row["has_started"]:
                    status = True
                    break
            
            if not status:
                data = False
        
        connection.commit()
        
        # if os.getenv('MODE') == "dev":
        #     print(f'status= {data}')
            
        return data

    except(Exception) as error:
        print(error)
        
    finally:
        connection.close()
    
def set_mark(discord_user_id, date):
    connection = db.get_db()
    try:
        connection.row_factory = sqlite3.Row
        cursor = connection.cursor()
        query = """
        SELECT records.id, records.has_started FROM records
        INNER JOIN users
        ON users.id = records.user_id
        WHERE users.discord_user_id = ?
        AND records.date = ?
        ORDER BY records.id;
        """

        cursor.execute(query, (discord_user_id, date))
        results = cursor.fetchall()
        
        if len(results) == 0:
            query = """
            INSERT INTO records (date, user_id, question_id, has_started)
            VALUES (?, (SELECT id FROM users WHERE discord_user_id = ?), 1, TRUE);
            """
            cursor.execute(query, (date, discord_user_id))
        elif len(results) > 0:
            status = False
            record_id = 0
            
            for row in results:
                if row["has_started"] == True:
                    status = True
                else:
                    record_id = row["id"]
            
            if not status:
                query = """
                UPDATE records
                SET has_started = True
                WHERE id = ?;
                """
                cursor.execute(query, (record_id,))

        connection.commit()
        
        if os.getenv('MODE') == "dev":
            print(f'set mark done')
            
        return True

    except(Exception) as error:
        print(error)
        
    finally:
        connection.close()
        
def get(date, discord_user_id, question_id):
    connection = db.get_db()
    try:
        connection.row_factory = sqlite3.Row
        cursor = connection.cursor()
        query = """
        SELECT * FROM records
        INNER JOIN users ON users.id = records.user_id
        WHERE records.date = ?
        AND users.discord_user_id = ?
        AND records.question_id = ?;
        """
        
        cursor.execute(query, (date, discord_user_id, question_id))
        results = cursor.fetchall()
        
        # if os.getenv('MODE') == "dev":
        #     print(f'record = {results}')
            
        return results

    except(Exception) as error:
        print(error)
        
    finally:
        connection.close()
        
def save_answer(data):
    connection = db.get_db()
    try:
        connection.row_factory = sqlite3.Row
        cursor = connection.cursor()
        if data["question_id"] == 1:
            query = """
            UPDATE records
            SET answer = ?, discord_answer_id = ?
            WHERE date = ? AND user_id = ? AND question_id = ?;
            """
            cursor.execute(query, (data["answer"], data["discord_answer_id"], data["date"], data["user_id"], data["question_id"]))
        else:
            query = """
            INSERT INTO records (date, user_id, question_id, answer, discord_answer_id)
            VALUES (?, ?, ?, ?, ?);
            """
            cursor.execute(query, (data["date"], data["user_id"], data["question_id"], data["answer"], data["discord_answer_id"]))

        connection.commit()
        
        # if os.getenv('MODE') == "dev":
        #     print(f'answer saved = {data}')
            
        return True

    except(Exception) as error:
        print(error)
        
    finally:
        connection.close()
        
def get_per_user_status(date):
    connection = db.get_db()
    try:
        connection.row_factory = sqlite3.Row
        cursor = connection.cursor()
        query = """
        SELECT users.id, users.discord_display_name, users.discord_user_id, COALESCE(COUNT(records.user_id), 0) AS count
        FROM users
        LEFT JOIN records ON records.user_id = users.id
        AND records.date = ?
        GROUP BY users.id, users.discord_user_id
        ORDER BY users.id;
        """

        cursor.execute(query, (date,))
        results = cursor.fetchall()
        
        if os.getenv('MODE') == "dev":
            print(f'per user status:')
            for row in results:
                print(f'id = {row["id"]}, count = {row["count"]}, discord_user_id = {row["discord_user_id"]}')
                
        return results

    except(Exception) as error:
        print(error)
        
    finally:
        connection.close()

def get_per_user_answer(date):
    connection = db.get_db()
    try:
        connection.row_factory = sqlite3.Row
        cursor = connection.cursor()
        query = """
        SELECT users.id, users.discord_display_name, users.discord_user_id, questions.question, records.answer
        FROM users
        LEFT JOIN records ON records.user_id = users.id
        AND records.date = ?
        LEFT JOIN questions ON questions.id = records.question_id 
        ORDER BY users.id, records.question_id;
        """

        cursor.execute(query, (date,))
        results = cursor.fetchall()
        
        if os.getenv('MODE') == "dev":
            print(f'per user answer:')
            for row in results:
                print(f'id = {row["id"]}, discord_display_name = {row["discord_display_name"]}, discord_user_id = {row["discord_user_id"]}, question = {row["question"]}, answer = {row["answer"]}')
                
        return results

    except(Exception) as error:
        print(error)
        
    finally:
        connection.close()
        
def reset(discord_user_id, date):
    connection = db.get_db()
    try:
        connection.row_factory = sqlite3.Row
        cursor = connection.cursor()
        user = users.get(discord_user_id=discord_user_id)
        if user is None:
            return
        user_id= user[0]["id"]
        
        query = """
        DELETE FROM records
        WHERE date = ? AND user_id = ?;
        """

        cursor.execute(query, (date, user_id))
        
        connection.commit()
        
        if os.getenv('MODE') == "dev":
            print(f'reset done')
            
        return True

    except(Exception) as error:
        print(error)
        
    finally:
        connection.close()