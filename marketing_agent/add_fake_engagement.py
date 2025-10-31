# marketing_agent/add_fake_engagement.py
import random
from datetime import datetime
from zoneinfo import ZoneInfo
import gspread

# --- Sheets auth (service_account.json must be in project root) ---
gc = gspread.service_account(filename="service_account.json")

# Open sheet/tab
ss = gc.open("TwoPeaks_Marketing")
ws = ss.worksheet("Instagram_Engagement_Raw")

# Safety: verify headers are exactly 5 and in order
expected_headers = ["timestamp", "username", "comment", "likes", "followers"]
headers = ws.row_values(1)
if [h.strip().lower() for h in headers[:5]] != expected_headers:
    raise RuntimeError(
        f"Header mismatch.\nExpected: {expected_headers}\nFound: {headers[:5]}"
    )

# Build a uniqueness set from existing usernames (col B)
existing_usernames = set([u for u in ws.col_values(2)[1:] if u.strip()])

# Pools
comment_pool = [
    "This chai just made my morning ☕️✨",
    "Need this in a bulk pack 😍",
    "Loved the saffron notes!",
    "Best chai I’ve ever had!",
    "Can you ship internationally?",
    "The ritual is everything. Beautiful blend.",
]
# Base handles to vary; final username will always be unique
base_handles = ["chai_lover", "tea_rider", "zenleaf", "mountainbrew", "aromabliss",
                "goldenglow", "masalamaven", "rosedrifter", "saffronseeker", "wellnessbrew"]

def unique_username():
    # Try base+random until unique
    for _ in range(1000):
        handle = random.choice(base_handles)
        suffix = random.randint(100, 9999)
        candidate = f"{handle}_{suffix}"
        if candidate not in existing_usernames:
            existing_usernames.add(candidate)
            return candidate
    # Fallback (should never hit)
    return f"user_{random.randint(100000,999999)}"

def iso_mountain():
    return datetime.now(ZoneInfo("America/Denver")).isoformat(timespec="seconds")

def add_rows(n=5):
    rows = []
    for _ in range(n):
        row = [
            iso_mountain(),                   # timestamp (A)
            unique_username(),                # username  (B)
            random.choice(comment_pool),      # comment   (C)
            random.randint(10, 100),          # likes     (D)
            random.randint(500, 5000),        # followers (E)
        ]
        rows.append(row)
    # Single batch append = faster, less error-prone
    ws.append_rows(rows, value_input_option="RAW")
    for r in rows:
        print("✅ Added:", r)

if __name__ == "__main__":
    add_rows(n=5)
