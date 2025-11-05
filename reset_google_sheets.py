import gspread
from google.oauth2.service_account import Credentials
import os

# Load credentials from service_account.json
SERVICE_ACCOUNT_FILE = os.getenv("GOOGLE_SVC_JSON", "service_account.json")
SHEET_NAME = os.getenv("SHEETS_SPREADSHEET_NAME", "TwoPeaks_Marketing")

# Authenticate and open the sheet
creds = Credentials.from_service_account_file(
    SERVICE_ACCOUNT_FILE,
    scopes=[
        "https://www.googleapis.com/auth/spreadsheets",
        "https://www.googleapis.com/auth/drive"
    ]
)
client = gspread.authorize(creds)
spreadsheet = client.open(SHEET_NAME)

# Tabs to clear
tabs_to_clear = [
    "Instagram_Engagement_Raw",
    "Qualified_Leads",
    "PostPurchase_Engagement_Log",
    "Customer_Insights_Data"
]

# Function to clear all rows except the header
def clear_sheet(sheet_name):
    try:
        worksheet = spreadsheet.worksheet(sheet_name)
        all_values = worksheet.get_all_values()
        if all_values:
            header = all_values[0]
            worksheet.clear()
            worksheet.append_row(header)
            print(f"✅ Cleared '{sheet_name}' but kept header.")
        else:
            print(f"⚠️ '{sheet_name}' was empty.")
    except Exception as e:
        print(f"❌ Error clearing '{sheet_name}': {e}")

# Execute clearing for each tab
for tab in tabs_to_clear:
    clear_sheet(tab)

print("\n🎉 All selected sheets have been reset and are ready for a fresh demo!")