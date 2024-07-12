import os
import sqlite3
import textwrap
from dotenv import load_dotenv
from config import db
from service.logger import logger

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

        logMsg = f'def questions.get_all:\n'
        for row in results:
            logMsg += textwrap.dedent(f'''
                id          : {row["id"]},
                question    : {row["question"]},
                tag         : {row["tag"]}\n\n
            ''')
        logger.info(logMsg)

        return results

    except (Exception) as error:
        logger.error(error)

    finally:
        connection.close()
