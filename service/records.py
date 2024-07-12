import os
import sqlite3
import textwrap
from dotenv import load_dotenv
from config import db
from service import users
from service.logger import logger

load_dotenv()


def get_mark(discord_user_id, date):
    connection = db.get_db()
    try:
        connection.row_factory = sqlite3.Row
        cursor = connection.cursor()
        query = """
        SELECT records.id FROM records
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

        logger.info(f'def records.get_mark: {data}')

        return data

    except (Exception) as error:
        logger.error(error)

    finally:
        connection.close()


def set_mark(discord_user_id, date):
    connection = db.get_db()
    try:
        connection.row_factory = sqlite3.Row
        cursor = connection.cursor()
        query = """
        SELECT records.id FROM records
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
            INSERT INTO records (date, user_id, has_started)
            VALUES (?, (SELECT id FROM users WHERE discord_user_id = ?), 1);
            """
            cursor.execute(query, (date, discord_user_id))
            connection.commit()

        logger.info(f'def records.set_mark: done')

        return True

    except (Exception) as error:
        logger.error(error)

    finally:
        connection.close()


def save(data):
    connection = db.get_db()
    try:
        connection.row_factory = sqlite3.Row
        cursor = connection.cursor()

        query = f"""
        UPDATE records
        SET {data["field"]} = ?
        WHERE id = ? AND date = ? AND user_id = ?;
        """
        cursor.execute(
            query, (data["answer"], data["id"], data["date"], data["user_id"]))

        connection.commit()

        logger.info(f'def records.save: {data}')

        return True

    except (Exception) as error:
        logger.error(error)

    finally:
        connection.close()


def save_goal(data):
    connection = db.get_db()
    try:
        connection.row_factory = sqlite3.Row
        cursor = connection.cursor()

        if data["index"] == 0:
            query = """
            UPDATE records
            SET goal = ?
            WHERE id = ?;
            """
            cursor.execute(query, (data["goal"], data["id"]))
        else:
            query = """
            INSERT INTO records (date, user_id, module, goal)
            VALUES (?, ?, ?,?);
            """
            cursor.execute(
                query, (data["date"], data["user_id"], data["module"], data["goal"]))

        connection.commit()

        logger.info(f'def records.save_goal: {data}')

        return True

    except (Exception) as error:
        logger.error(error)

    finally:
        connection.close()


def answer_close(row_id):
    connection = db.get_db()
    try:
        connection.row_factory = sqlite3.Row
        cursor = connection.cursor()

        query = """
        UPDATE records
        SET has_started = 2
        WHERE id = ?;
        """
        cursor.execute(query, (row_id,))
        connection.commit()

        logger.info(f'def records.answer_closed: id= {row_id}')

        return True

    except (Exception) as error:
        logger.error(error)

    finally:
        connection.close()


def get_per_user_status(date):
    connection = db.get_db()
    try:
        connection.row_factory = sqlite3.Row
        cursor = connection.cursor()
        query = """
        SELECT users.id, users.discord_display_name, users.discord_user_id, COALESCE(records.has_started, 0) AS has_started
        FROM users
        LEFT JOIN records ON records.user_id = users.id
        AND records.date = ?
        """

        cursor.execute(query, (date,))
        results = cursor.fetchall()

        logMsg = f'def records.get_per_user_status:\n'
        for row in results:
            logMsg += textwrap.dedent(f'''
                id              : {row["id"]},
                count           : {row["count"]},
                discord_user_id : {row["discord_user_id"]}\n\n
            ''')
        logger.info(logMsg)

        return results

    except (Exception) as error:
        logger.error(error)

    finally:
        connection.close()


def get_user_records(date, discord_user_id=None):
    connection = db.get_db()
    try:
        connection.row_factory = sqlite3.Row
        cursor = connection.cursor()

        if discord_user_id is None:
            query = """
            SELECT records.*, users.discord_display_name, users.discord_user_id
            FROM records
            LEFT JOIN users ON users.id = records.user_id
            WHERE records.date = ?
            ORDER BY records.user_id;
            """
            cursor.execute(query, (date,))
        else:
            query = """
            SELECT records.*, users.discord_display_name, users.discord_user_id
            FROM records
            LEFT JOIN users ON users.id = records.user_id
            WHERE users.discord_user_id = ?
            AND records.date = ?;
            """
            cursor.execute(query, (discord_user_id, date,))

        results = cursor.fetchall()

        logMsg = f'def records.get_user_records:\n'
        for row in results:
            logMsg += textwrap.dedent(f'''
                id                      : {row["id"]},
                date                    : {row["date"]},
                user_id                 : {row["user_id"]},
                module                  : {row["module"]},
                goal                    : {row["goal"]},
                updates                 : {row["updates"]},
                comments                : {row["comments"]},
                has_started             : {row["has_started"]},
                discord_display_name    : {row["discord_display_name"]}\n\n
            ''')
        logger.info(logMsg)

        return results

    except (Exception) as error:
        logger.error(error)

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
        user_id = user[0]["id"]

        query = """
        DELETE FROM records
        WHERE date= ? AND user_id= ?;
        """

        cursor.execute(query, (date, user_id))

        connection.commit()

        logger.info(f'def records.reset: done')

        return True

    except (Exception) as error:
        logger.error(error)

    finally:
        connection.close()
