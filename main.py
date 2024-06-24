import os
import datetime
import pytz
from dotenv import load_dotenv
import discord
from discord.ext import tasks
from service import users, questions, records, report
from config import db

load_dotenv()
TOKEN = os.getenv('DISCORD_BOT_TOKEN')
GUILD = os.getenv('DISCORD_BOT_GUILD')
TODO_CHANNEL_ID = int(os.getenv('TODO_CHANNEL_ID'))
BOT_ID = int(os.getenv('BOT_ID'))

intents = discord.Intents.default()
intents.message_content = True
client = discord.Client(intents=intents)

db.init()

def is_eligible(message):
    # Ignore messages sent by the bot itself
    if message.author == client.user:
        print("bot is not eligible")
        return False
    
    # Check if the command was invoked in the desired channel
    if message.channel.id != BOT_ID:
        print("channel is not eligible")
        return False # Ignore commands not in the desired channel
    
    return True

def get_question(message):
    user = users.get(discord_user_id=message.author.id)
    if len(user) > 0:
        user_id= user[0]["id"]
    
    answered_counter = 0
    
    db_questions = questions.get_all()
    for index, value in enumerate(db_questions):
        db_records = records.get(datetime.date.today(), message.author.id, value["id"])

        if len(db_records) > 0 and db_records[0]['answer'] is not None and len(db_records[0]['answer']) > 0:
            answered_counter += 1
            continue
        else:
            if message.content != "/update":
                data = {
                    "date": datetime.date.today(),
                    "user_id": user_id,
                    "question_id": value["id"],
                    "answer": message.content,
                    "discord_answer_id": message.id,
                }
                records.save_answer(data)
                print(index)
                print(value)
                if value["id"] <= 2:
                    return db_questions[value["id"]]['question']
                else:
                    return "Thank you. You have answered all 3 questions. To update your answers please give **/reset** command."
            else:
                return value['question']
    
    if answered_counter >= 3:
        return "You already have answered all 3 questions. To update your answers please give **/reset** command."
 
@client.event
async def on_ready():
    print(f'{client.user.name} has connected to Discord!')
    auto_ping.start()
    
@client.event
async def on_message(message):
    if not is_eligible(message):
        return
    
    users.save(message.author)
    
    print(f'{message.author}: {message.content}')

    if message.content == "/reset":
        records.reset(message.author.id, datetime.date.today())
        await message.author.send("Your answers have been reset. Please start by **/update** command.")
        return
    elif message.content == "/update":
        records.set_mark(message.author.id, datetime.date.today())
        ques = get_question(message)
        await message.author.send(ques)
        return
    else:    
        mark = records.get_mark(message.author.id, datetime.date.today())
        if not mark:
            await message.author.send("Message ignored! Please start by **/update** command.")
            return

        ques = get_question(message)
        await message.author.send(ques)
        return

dhaka_tz = pytz.timezone('Asia/Dhaka')
ten_o_clock = datetime.time(hour=22, minute=00, tzinfo=dhaka_tz)
eleven_o_clock = datetime.time(hour=23, minute=00, tzinfo=dhaka_tz)
twelve_five = datetime.time(hour=00, minute=5, tzinfo=dhaka_tz)
    
@tasks.loop(minutes=1)
async def auto_ping():
    now = datetime.datetime.now(dhaka_tz).time()

    if (now.hour == ten_o_clock.hour and now.minute == ten_o_clock.minute) or (now.hour == eleven_o_clock.hour and now.minute == eleven_o_clock.minute):
        results = records.get_per_user_status(datetime.date.today())
    
        for row in results:
            if row["count"] < 3:
                user = await client.fetch_user(row["discord_user_id"])
                if user:
                    await user.send(f'Hello **{row["discord_display_name"]}**, you didn\'t update your progress today. Please use **/update** command to update your progress.')
                    print(f"{user.name} was pinged.")
                else:
                    print(f'User with ID {row["discord_user_id"]} not found')
    
    if now.hour == twelve_five.hour and now.minute == twelve_five.minute:
        report.discord_channel(client, datetime.date.today())
        report.gsheet()
    
if __name__ == "__main__":
    client.run(TOKEN)
    
    

    
        
    