import os
import sqlite3
import textwrap
from dotenv import load_dotenv
from config import db
from service.logger import logger

load_dotenv()


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

        logMsg = f'def users.get:\n'
        for row in results:
            logMsg += textwrap.dedent(f'''
                id                      : {row["id"]},
                discord_username        : {row["discord_username"]},
                discord_user_id         : {row["discord_user_id"]},
                discord_display_name    : {row["discord_display_name"]}\n\n
            ''')
        logger.info(logMsg)

        return results

    except (Exception) as error:
        logger.error(error)

    finally:
        connection.close()


def save(user):
    connection = db.get_db()
    try:
        connection.row_factory = sqlite3.Row
        cursor = connection.cursor()
        query = """
        SELECT id FROM users
        WHERE discord_user_id = ?;
        """

        cursor.execute(query, (user.id,))
        results = cursor.fetchall()

        if len(results) == 0:
            query = """
            INSERT INTO users (discord_username, discord_display_name, discord_user_id)
            VALUES (?, ?, ?);
            """

            cursor.execute(query, (user.name, user.global_name, user.id))
            connection.commit()

            data = f'New users info inserted into Database.\n'
            data += textwrap.dedent(f'''
                        discord_username        : {user.name},
                        discord_user_id         : {user.global_name},
                        discord_display_name    : {user.id}
                    ''')
        else:
            data = f'User({user.global_name}) info already exists in Database.'

        logger.info(f'def users.save: {data}')

        return True

    except (Exception) as error:
        logger.error(error)

    finally:
        connection.close()
