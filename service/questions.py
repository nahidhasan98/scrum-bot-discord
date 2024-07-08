import os
import sqlite3
import textwrap
from dotenv import load_dotenv
from config import db

load_dotenv()


def get_all():
    connection = db.get_db()
    try:
        connection.row_factory = sqlite3.Row
        cursor = connection.cursor()
        query = """
        SELECT * FROM questions;
        """

        cursor.execute(query)
        results = cursor.fetchall()

        if os.getenv('MODE') == "dev":
            print(f'def questions.get_all:')
            for row in results:
                print(textwrap.dedent(f'''
                    id          : {row["id"]},
                    question    : {row["question"]},
                    tag         : {row["tag"]}
                '''))

        return results

    except (Exception) as error:
        print(error)

    finally:
        connection.close()
