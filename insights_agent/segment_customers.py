# insights_agent/segment_customers.py
import pandas as pd
from datetime import datetime, timezone
import gspread

# ---- 1. Google Sheets Auth ----
gc = gspread.service_account(filename="service_account.json")

# Open spreadsheet
ss = gc.open("TwoPeaks_Marketing")

# Load data from Customer_Insights_Data tab
orders_ws = ss.worksheet("Customer_Insights_Data")
orders_df = pd.DataFrame(orders_ws.get_all_records())

# ---- 2. Parse and normalize ----
orders_df["Created at"] = pd.to_datetime(orders_df["Created at"], errors="coerce")
orders_df["Subtotal"] = pd.to_numeric(orders_df["Subtotal"], errors="coerce")
orders_df["Total"] = pd.to_numeric(orders_df["Total"], errors="coerce")

# ---- 3. Aggregate by Customer ----
agg = (
    orders_df.groupby(["Email", "Customer First Name", "Customer Last Name"])
    .agg(
        total_orders=("Name", "count"),
        total_spent=("Total", "sum"),
        avg_order_value=("Total", "mean"),
        last_order=("Created at", "max"),
    )
    .reset_index()
)

# ---- 4. Compute Recency ----
today = datetime.now(timezone.utc)
agg["recency_days"] = (today - agg["last_order"]).dt.days

# ---- 5. Basic Scoring Logic ----
def score_segment(row):
    if row["total_orders"] >= 3 and row["recency_days"] < 30:
        return "Loyalist"
    elif row["total_orders"] == 1 and row["total_spent"] > 40:
        return "High-Value Newcomer"
    elif row["total_orders"] == 1:
        return "First-time Buyer"
    elif row["total_orders"] >= 2 and row["recency_days"] > 45:
        return "At-Risk Repeat"
    else:
        return "Engaged Customer"

agg["segment"] = agg.apply(score_segment, axis=1)

# ---- 6. Add some human-readable summaries ----
def insight(row):
    if row["segment"] == "Loyalist":
        return f"{row['Customer First Name']} orders often and recently — a loyal fan of Two Peaks."
    elif row["segment"] == "High-Value Newcomer":
        return f"New but premium — high order value, ripe for follow-up campaign."
    elif row["segment"] == "At-Risk Repeat":
        return f"Hasn’t ordered recently — consider sending reactivation offer."
    elif row["segment"] == "Engaged Customer":
        return f"Engaged customer, orders semi-regularly."
    else:
        return f"First-time buyer — send nurturing welcome series."

agg["insight_summary"] = agg.apply(insight, axis=1)

# ---- 7. Save to new tab ----
try:
    ws_new = ss.worksheet("Customer_Segments")
    ss.del_worksheet(ws_new)
except Exception:
    pass

new_ws = ss.add_worksheet(title="Customer_Segments", rows=100, cols=10)
# ---- 7. Save to new tab ----
try:
    ws_new = ss.worksheet("Customer_Segments")
    ss.del_worksheet(ws_new)
except Exception:
    pass

new_ws = ss.add_worksheet(title="Customer_Segments", rows=100, cols=10)

# Convert datetimes to strings for upload
agg_for_upload = agg.copy()
agg_for_upload["last_order"] = agg_for_upload["last_order"].dt.strftime("%Y-%m-%d %H:%M:%S")

# Fill NaNs with empty string for safety
agg_for_upload = agg_for_upload.fillna("")

# Convert everything to string for Sheets upload
records = [agg_for_upload.columns.tolist()] + agg_for_upload.astype(str).values.tolist()
new_ws.update(records)

print("✅ Segmentation complete! Results written to 'Customer_Segments' tab.")
print(agg.head())