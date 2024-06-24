import os
import time
import gspread
from google.oauth2.service_account import Credentials
from dotenv import load_dotenv
from service import records

load_dotenv()

async def discord_channel(client, date):
    channel = client.get_channel(int(os.getenv('TODO_CHANNEL_ID')))
    
    if channel:
        results = records.get_per_user_answer(date)
        user_id = 0
        msg = f'```'
        
        for row in results:
            if user_id != row["id"]:
                if user_id != 0:
                    msg += f'```'
                    await channel.send(msg)
                    time.sleep(3)
                
                user_id = row["id"]
                msg = "<@" + row['discord_user_id'] + ">\n"
                msg += f'```md\n'
            
            if row["question"] is None or row["question"] == "":
                msg += f': No answer given at all.\n'
            else:
                msg += f'> {row["question"]}\n'
                
                if row["answer"] is None or row["answer"] == "":
                    msg += "Not answered.\n"
                else:
                    msg += f': {row["answer"]}\n\n'

        if len(results) > 0:
            msg += f'```'
            await channel.send(msg)

def get_sheet():
    scopes = [
        "https://www.googleapis.com/auth/spreadsheets"
    ]

    creds = Credentials.from_service_account_file("credentials.json", scopes=scopes)
    client = gspread.authorize(creds)
    sheet_id = os.getenv('GOOGLE_SHEET_ID')

    sheet = client.open_by_key(sheet_id)
    
    return sheet

def gsheet():
    sheet = get_sheet()
    
    worksheet_list = sheet.worksheets()
    print(worksheet_list)
    
    worksheet = sheet.worksheet("SenseVoice")
    print(worksheet)
    
    list_of_lists = worksheet.get_all_values()
    print(list_of_lists)
    
    list_of_dicts = worksheet.get_all_records()
    print(list_of_dicts)
    
    # Data to be added (as a list)
    row_data = ["Data1", "Data2", "Data3", "Data4"]

    # Append the data to the sheet
    worksheet.append_row(row_data)