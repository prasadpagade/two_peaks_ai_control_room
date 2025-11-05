# marketing_agent/add_fake_engagement.py
import random
from datetime import datetime
from zoneinfo import ZoneInfo
import gspread
import os, requests, time

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

# --- Simulation: fake API sources & fetch progress (for UX/demo only) ---
PLATFORMS = [
    "instagram",
    "facebook",
    "x (twitter)",
    "tiktok",
    "linkedin",
]

def simulate_fetch(platform=None, n=5):
    """Prints a friendly simulated fetch progress so callers (and Streamlit) see
    a believable API flow without actually calling external services.
    This output is printed to stdout and will be captured by the parent app.
    """
    if platform is None:
        platform = random.choice(PLATFORMS)

    print(f"📡 Simulating fetch from {platform} engagement API...")
    time.sleep(0.6)
    print("🔒 Authenticating (simulated)...")
    time.sleep(0.4)
    print("✅ Auth OK — requesting recent comments and likes")
    time.sleep(0.6)

    # Simulate pagination / streaming fetch
    fetched = 0
    for i in range(n):
        chunk = random.randint(1, 3)
        fetched += chunk
        print(f"⬇️  Received {chunk} new engagement rows (total {fetched})")
        time.sleep(0.35)

    print(f"✨ Finished simulated fetch from {platform}: {fetched} items ready to insert into sheet.")

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

#Optionally trigger n8n after new data
# ============================================================
# 🚀 Simulated API webhook (disabled real n8n trigger)
# ============================================================
WEBHOOK_URL = os.getenv("N8N_MARKETING_URL", "").strip()

if __name__ == "__main__":
    print("📡 Simulating cross-platform engagement sync…")
    time.sleep(0.8)
    print("🔒 Authenticating with Instagram (simulated)...")
    time.sleep(0.6)
    print("🔒 Authenticating with LinkedIn (simulated)...")
    time.sleep(0.6)
    print("✅ Auth OK — fetching engagement data streams...")
    time.sleep(0.6)

    # Run the actual row creation logic
    add_rows(n=5)

    # Simulate “posting to webhook” logs (no real request sent)
    print("🌐 Posting engagement payload to n8n webhook (simulated)...")
    time.sleep(0.8)
    print("📦 Sending 5 engagement objects to processing pipeline...")
    time.sleep(0.6)
    print("✅ [Mock] Webhook accepted 5 events successfully.")
    print("✨ Simulation complete — engagement data inserted locally (no real webhook call).")
