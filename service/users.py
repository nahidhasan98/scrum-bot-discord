import os
import sqlite3
import textwrap
from dotenv import load_dotenv
from config import db

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

        if os.getenv('MODE') == "dev":
            print(f'def users.get:')
            for row in results:
                print(textwrap.dedent(f'''
                    id                      : {row["id"]},
                    discord_username        : {row["discord_username"]},
                    discord_user_id         : {row["discord_user_id"]},
                    discord_display_name    : {row["discord_display_name"]}
                '''))

        return results

    except (Exception) as error:
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

            data = f'New users info inserted into Database.\n'
            data += textwrap.dedent(f'''
                        discord_username        : {data.name},
                        discord_user_id         : {data.global_name},
                        discord_display_name    : {data.id}
                    ''')
        else:
            data = f'User({data.global_name}) info already exists in Database.'

        if os.getenv('MODE') == "dev":
            print(f'def users.save:')
            print(f'{data}')

        return True

    except (Exception) as error:
        print(error)

    finally:
        connection.close()
