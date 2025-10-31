import os
import gspread
from oauth2client.service_account import ServiceAccountCredentials
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Define scopes
scope = [
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive"
]

# Authenticate using the JSON key
creds = ServiceAccountCredentials.from_json_keyfile_name(
    os.getenv("GOOGLE_SVC_JSON"), scope)
client = gspread.authorize(creds)

# Open the spreadsheet and tab
ss = client.open(os.getenv("SHEETS_SPREADSHEET_NAME"))
worksheet = ss.worksheet("Instagram_Engagement_Raw")

# Append a test row
worksheet.append_row(["timestamp", "username", "comment", "likes", "followers"])

print("✅ Test row appended successfully to Google Sheet!")
