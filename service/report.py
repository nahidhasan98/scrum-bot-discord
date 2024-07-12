import os
import time
import gspread
from google.oauth2.service_account import Credentials
from dotenv import load_dotenv
from service.logger import logger

load_dotenv()

if os.getenv('MODE') == "prod":
    TODO_CHANNEL_ID = int(os.getenv('TODO_CHANNEL_ID_PROD'))
    MODERATORS = os.getenv('MODERATORS_PROD')
else:
    TODO_CHANNEL_ID = int(os.getenv('TODO_CHANNEL_ID_DEV'))
    MODERATORS = os.getenv('MODERATORS_DEV')

sheet_id = os.getenv('GOOGLE_SHEET_ID')


def prepare_final_message(counter, goal, updates, comments):
    msg = f'> What tasks have you been assigned for today?\n'
    msg += f'{goal}\n\n'

    if counter == 1:
        msg += f'> Have you completed the task?\n'
    else:
        msg += f'> Have you completed the tasks?\n'
    msg += f'{updates}\n\n'

    if counter == 1:
        msg += f'> Any blockers/comments regarding this task?\n'
    else:
        msg += f'> Any blockers/comments regarding these tasks?\n'
    msg += f'{comments}\n\n'

    return msg


async def discord_channel(client, results):
    channel = client.get_channel(TODO_CHANNEL_ID)

    if channel:
        user_id = 0
        counter, goal, updates, comments = 0, "", "", ""

        for row in results:
            if user_id != int(row["user_id"]):
                if user_id != 0:
                    msg += prepare_final_message(
                        counter, goal, updates, comments
                    )
                    msg += f'```'   # end tags
                    await channel.send(msg)

                    counter, goal, updates, comments = 0, "", "", ""
                    time.sleep(3)

            if counter == 0:
                user_id = row["user_id"]
                msg = "<@" + row['discord_user_id'] + ">\n"
                msg += f'```md\n'   # start tags
                msg += f'> Which module are you working on?\n'
                msg += f': {row["module"]}\n\n'

            counter += 1
            goal += f'{counter}. {row["goal"]}\n'
            updates += f'{counter}. {row["updates"]}\n'
            comments += f'{counter}. {row["comments"]}\n'

        if len(results) > 0:    # for last row/user
            msg += prepare_final_message(
                counter, goal, updates, comments
            )
            msg += f'```'   # end tags
            await channel.send(msg)


def get_sheet():
    scopes = [
        "https://www.googleapis.com/auth/spreadsheets"
    ]

    creds = Credentials.from_service_account_file(
        "credentials.json", scopes=scopes)
    client = gspread.authorize(creds)

    sheet = client.open_by_key(sheet_id)

    return sheet


async def gsheet(client, results, date):
    sheet = get_sheet()

    worksheet = sheet.worksheet(os.getenv('GOOGLE_WORKSHEET_NAME'))
    logger.info(f'worksheet: {worksheet}')

    knock_moderators = False
    row_data = []

    for row in results:
        row_data.append(f'{date}')
        row_data.append(os.getenv('PROJECT'))
        row_data.append(row["module"])
        row_data.append(row["goal"])
        row_data.append(row["updates"])
        row_data.append(row["comments"])
        row_data.append(row["discord_display_name"])

        worksheet.append_row(row_data)
        knock_moderators = True
        row_data.clear()
        time.sleep(3)

    if knock_moderators:
        # send dm to (moderators) Kabir vaia and Swaradip vaia
        moderators = MODERATORS
        if moderators:
            moderator_list = moderators.split(',')
            for moderator in moderator_list:
                logger.info(f"Moderator Discord ID: {moderator}")
                user = await client.fetch_user(moderator)

                msg = f'```md\n'
                msg += f'There are some updates in [google sheet](https://docs.google.com/spreadsheets/d/{sheet_id}/).\n'
                msg += f'Please check.\n'
                msg += f'```\n'
                await user.send(msg)
                logger.info(f"Moderator {user.name} was pinged.")
        else:
            logger.info("No moderators found in the environment variable.")
