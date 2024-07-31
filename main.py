import os
import datetime
import pytz
from dotenv import load_dotenv
import discord
from discord.ext import tasks
from service import users, questions, records, report
from service.logger import logger
from config import db

load_dotenv()

BOT_TOKEN = os.getenv('BOT_TOKEN_PROD')

intents = discord.Intents.default()
intents.message_content = True
client = discord.Client(intents=intents)

db.init()


def is_eligible(message):
    # Ignore messages sent by the bot itself
    if message.author == client.user:
        logger.info("bot is not eligible")
        return False

    # Check if the message is a DM sent to the bot
    if not isinstance(message.channel, discord.DMChannel):
        logger.info("message to channel is not eligible")
        return False

    return True


def save_answer(message, question):
    user = users.get(discord_user_id=message.author.id)
    if len(user) > 0:
        user_id = user[0]["id"]
    else:
        return ""

    user_records = records.get_user_records(
        datetime.date.today(), message.author.id)
    answer_saved = False

    for row in user_records:
        for q in question:
            if row[q["tag"]] == None or len(row[q["tag"]]) == 0:
                if q["tag"] != "goal":
                    data = {
                        "id": row["id"],
                        "date": datetime.date.today(),
                        "user_id": user_id,
                        "field": q["tag"],
                        "answer": message.content,
                    }
                    records.save(data)
                else:
                    goals = message.content.split(";")
                    for index, g in enumerate(goals):
                        g = g.strip()
                        if len(g) > 0:
                            data = {
                                "id": row["id"],
                                "date": row["date"],
                                "user_id": row["user_id"],
                                "module": row["module"],
                                "goal": g,
                                "index": index,
                            }
                            records.save_goal(data)

                answer_saved = True
                break

        if answer_saved:
            return ""

    return "You already have answered all questions. To update your answers please give **/reset** command."


def get_question(message, question):
    user_records = records.get_user_records(
        datetime.date.today(), message.author.id)
    next_ques = ""

    for row in user_records:
        for q in question:
            if row[q["tag"]] == None or len(row[q["tag"]]) == 0:
                if q["tag"] == "updates":
                    next_ques = q["question"] + " (" + row["goal"] + ")?"
                else:
                    next_ques = q["question"]

                break

        if len(next_ques) > 0:
            return next_ques

    if message.content == "/update":
        return "You already have answered all questions. To update your answers please give **/reset** command."
    else:
        if user_records is not None and len(user_records) > 0:
            records.answer_close(user_records[0]["id"])
        return "Thank you. You have answered all questions. To update your answers please give **/reset** command."


@client.event
async def on_ready():
    logger.info(f'{client.user.name} has connected to Discord!')
    auto_ping.start()


@client.event
async def on_message(message):
    if not is_eligible(message):
        return

    users.save(message.author)
    logger.info(f'{message.author}: {message.content}')

    if message.content == "/reset":
        records.reset(message.author.id, datetime.date.today())
        await message.author.send("Your answers have been reset. Please start by **/update** command.")
    elif message.content == "/update":
        records.set_mark(message.author.id, datetime.date.today())

        question = questions.get_all()

        ques = get_question(message, question)
        await message.author.send(ques)
    else:
        mark = records.get_mark(message.author.id, datetime.date.today())
        if not mark:
            await message.author.send("Message ignored! Please start by **/update** command.")
            return

        question = questions.get_all()

        res = save_answer(message, question)
        if len(res) > 0:
            await message.author.send(res)
        else:
            ques = get_question(message, question)
            await message.author.send(ques)


@tasks.loop(minutes=1)
async def auto_ping():
    dhaka_tz = pytz.timezone('Asia/Dhaka')
    ten_o_clock = datetime.time(hour=22, minute=00, tzinfo=dhaka_tz)
    eleven_fifty_nine = datetime.time(hour=23, minute=59, tzinfo=dhaka_tz)
    now = datetime.datetime.now(dhaka_tz).time()

    if (now.hour == ten_o_clock.hour and now.minute == ten_o_clock.minute):
        results = records.get_per_user_status(datetime.date.today())

        for row in results:
            if row["has_started"] < 2:
                user = await client.fetch_user(row["discord_user_id"])

                await user.send(f'Hello **{row["discord_display_name"]}**, you didn\'t update your progress today. Please use **/update** command to update your progress.')
                logger.info(f"{user.name} was pinged.")

    if now.hour == eleven_fifty_nine.hour and now.minute == eleven_fifty_nine.minute:
        results = records.get_user_records(datetime.date.today())
        await report.gsheet(client, results, datetime.date.today())
        await report.discord_channel(client, results)

if __name__ == "__main__":
    client.run(BOT_TOKEN)
