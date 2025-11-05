import os
from google.oauth2.service_account import Credentials
import gspread

print("🔍 GOOGLE_SVC_JSON =", os.getenv("GOOGLE_SVC_JSON"))
print("🔍 CWD =", os.getcwd())

try:
    SCOPES = [
        "https://www.googleapis.com/auth/spreadsheets",
        "https://www.googleapis.com/auth/drive"
    ]
    service_file = os.path.abspath(os.getenv("GOOGLE_SVC_JSON", "service_account.json"))
    print("📄 Using service account file:", service_file)

    creds = Credentials.from_service_account_file(service_file, scopes=SCOPES)
    print("✅ Authenticated as:", creds.service_account_email)

    client = gspread.authorize(creds)
    sheet = client.open("TwoPeaks_Marketing")
    print("✅ Sheets connected! Tabs:", [ws.title for ws in sheet.worksheets()])

except Exception as e:
    print("❌ ERROR:", e)