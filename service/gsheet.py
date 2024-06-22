import os
import gspread
from google.oauth2.service_account import Credentials
import sqlite3
from dotenv import load_dotenv
from config import db

load_dotenv()

def get_sheet():
    scopes = [
        "https://www.googleapis.com/auth/spreadsheets"
    ]

    creds = Credentials.from_service_account_file("credentials.json", scopes=scopes)
    client = gspread.authorize(creds)
    sheet_id = os.getenv('GOOGLE_SHEET_ID')

    sheet = client.open_by_key(sheet_id)
    value_list = sheet.sheet1.row_values(1)
    print(value_list)
    
    return sheet

def update_report():
    sheet = get_sheet()
    