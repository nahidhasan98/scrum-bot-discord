import os
from datetime import date
from dotenv import load_dotenv
import discord
from discord.ext import commands
from service import users, questions, records
from config import db

load_dotenv()
TOKEN = os.getenv('DISCORD_BOT_TOKEN')
GUILD = os.getenv('DISCORD_BOT_GUILD')
TODO_CHANNEL_ID = int(os.getenv('TODO_CHANNEL_ID'))
BOT_ID = int(os.getenv('BOT_ID'))

intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix='/', intents=intents)

db.init()

def is_eligible(message):
    # Ignore messages sent by the bot itself
    if message.author == bot.user:
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
        db_records = records.get(date.today(), message.author.id, value["id"])

        if len(db_records) > 0 and db_records[0]['answer'] is not None and len(db_records[0]['answer']) > 0:
            answered_counter += 1
            continue
        else:
            if message.content != "/update":
                data = {
                    "date": date.today(),
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
        return "Thank you. You have answered all 3 questions. To update your answers please give **/reset** command."
        
@bot.event
async def on_ready():
    print(f'{bot.user.name} has connected to Discord!')
    channel = bot.get_channel(TODO_CHANNEL_ID)
    print(f'Channel {channel} is active')
    
@bot.event
async def on_message(message):
    if not is_eligible(message):
        return
    
    users.save(message.author)
    
    print(f'{message.author}: {message.content}')

    if message.content == "/reset":
        records.reset(message.author.id, date.today())
        await message.author.send("Your answers have been reset. Please start by **/update** command.")
        return
    elif message.content == "/update":
        records.set_mark(message.author.id, date.today())
        ques = get_question(message)
        await message.author.send(ques)
        return
    else:    
        mark = records.get_mark(message.author.id, date.today())
        if not mark:
            await message.author.send("Message ignored! Please start by **/update** command.")
            return

        ques = get_question(message)
        await message.author.send(ques)
        return

if __name__ == "__main__":
    bot.run(TOKEN)
    
    

    
        
    