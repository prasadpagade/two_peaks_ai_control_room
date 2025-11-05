
import pandas as pd
from datetime import datetime, timezone
import gspread

def load_customer_data():
    import pandas as pd
    import gspread

    try:
        gc = gspread.service_account(filename="service_account.json")
        sh = gc.open("TwoPeaks_Marketing")
        ws = sh.worksheet("Customer_Insights_Data")
        data = ws.get_all_records()

        if not data:
            raise ValueError("Empty Google Sheet detected")

        orders_df = pd.DataFrame(data)
    except Exception as e:
        print(f"⚠️ Using fallback mock data due to: {e}")
        orders_df = pd.DataFrame([
            ["Order #1001", "asha@chai.com", "Paid", "Delivered", "2025-10-01", "2025-10-01", "2025-10-03", "USD", 45, 5, 50, 1, "Rose Radiance Chai", 45, "Boulder", "CO", "US", "Asha", "Verma", "Loyal customer", "Returning"],
            ["Order #1002", "raj@chai.com", "Paid", "Shipped", "2025-10-02", "2025-10-02", "2025-10-04", "USD", 70, 6, 76, 2, "Saffron Infused Chai", 35, "Denver", "CO", "US", "Raj", "Singh", "Loves saffron chai", "New"],
            ["Order #1003", "maya@chai.com", "Paid", "Delivered", "2025-10-03", "2025-10-03", "2025-10-05", "USD", 40, 5, 45, 1, "Assam Breakfast Chai", 40, "Chicago", "IL", "US", "Maya", "Patel", "Great review", "Returning"],
            ["Order #1004", "geeta@chai.com", "Paid", "Delivered", "2025-10-04", "2025-10-04", "2025-10-06", "USD", 55, 5, 60, 1, "Cardamom Bliss Chai", 55, "Austin", "TX", "US", "Geeta", "Sharma", "Referred by friend", "Promo"],
            ["Order #1005", "karan@chai.com", "Paid", "Shipped", "2025-10-05", "2025-10-05", "2025-10-08", "USD", 60, 6, 66, 2, "Signature Masala Chai", 30, "Portland", "OR", "US", "Karan", "Mehta", "Prefers bold flavor", "New"],
            ["Order #1006", "neha@chai.com", "Paid", "Delivered", "2025-10-06", "2025-10-06", "2025-10-08", "USD", 48, 4, 52, 1, "Tulsi Serenity Chai", 48, "Seattle", "WA", "US", "Neha", "Gupta", "Repeat customer", "Returning"],
            ["Order #1007", "john@chai.com", "Paid", "Delivered", "2025-10-07", "2025-10-07", "2025-10-09", "USD", 72, 6, 78, 3, "Ginger Zest Chai", 24, "Los Angeles", "CA", "US", "John", "Miller", "Bulk order", "VIP"],
            ["Order #1008", "priya@chai.com", "Paid", "Shipped", "2025-10-08", "2025-10-08", "2025-10-10", "USD", 37, 5, 42, 1, "Himalayan Honey Chai", 37, "Denver", "CO", "US", "Priya", "Nair", "Gift purchase", "Gift"],
            ["Order #1009", "rohan@chai.com", "Paid", "Delivered", "2025-10-09", "2025-10-09", "2025-10-12", "USD", 68, 7, 75, 2, "Rose Radiance Chai", 34, "New York", "NY", "US", "Rohan", "Iyer", "Excellent feedback", "Returning"],
            ["Order #1010", "vikram@chai.com", "Paid", "Delivered", "2025-10-10", "2025-10-10", "2025-10-12", "USD", 39, 4, 43, 1, "Assam Breakfast Chai", 39, "Phoenix", "AZ", "US", "Vikram", "Rao", "Enjoys strong chai", "New"],
            ["Order #1011", "emma@chai.com", "Paid", "Shipped", "2025-10-11", "2025-10-11", "2025-10-13", "USD", 50, 5, 55, 2, "Rose Radiance Chai", 25, "San Francisco", "CA", "US", "Emma", "Moore", "Subscription user", "Subscription"],
            ["Order #1012", "liam@chai.com", "Paid", "Delivered", "2025-10-12", "2025-10-12", "2025-10-14", "USD", 75, 6, 81, 3, "Cardamom Bliss Chai", 25, "Miami", "FL", "US", "Liam", "Thomas", "High AOV customer", "VIP"],
            ["Order #1013", "anita@chai.com", "Paid", "Delivered", "2025-10-13", "2025-10-13", "2025-10-15", "USD", 58, 5, 63, 2, "Saffron Infused Chai", 29, "Chicago", "IL", "US", "Anita", "Desai", "Loves saffron aroma", "Returning"],
            ["Order #1014", "karishma@chai.com", "Paid", "Delivered", "2025-10-14", "2025-10-14", "2025-10-16", "USD", 64, 5, 69, 2, "Masala Chai Sampler", 32, "Boulder", "CO", "US", "Karishma", "Mehra", "Enjoys variety packs", "New"],
            ["Order #1015", "rajesh@chai.com", "Paid", "Shipped", "2025-10-15", "2025-10-15", "2025-10-18", "USD", 45, 5, 50, 1, "Ginger Zest Chai", 45, "Austin", "TX", "US", "Rajesh", "Kapoor", "Prefers organic", "Returning"],
            ["Order #1016", "sophia@chai.com", "Paid", "Delivered", "2025-10-16", "2025-10-16", "2025-10-19", "USD", 53, 6, 59, 1, "Saffron Infused Chai", 53, "San Diego", "CA", "US", "Sophia", "Taylor", "Gift for friend", "Gift"],
            ["Order #1017", "nathan@chai.com", "Paid", "Delivered", "2025-10-17", "2025-10-17", "2025-10-20", "USD", 42, 4, 46, 1, "Assam Breakfast Chai", 42, "Chicago", "IL", "US", "Nathan", "Clark", "Chai enthusiast", "Returning"],
            ["Order #1018", "arjun@chai.com", "Paid", "Delivered", "2025-10-18", "2025-10-18", "2025-10-21", "USD", 38, 5, 43, 1, "Tulsi Serenity Chai", 38, "Boulder", "CO", "US", "Arjun", "Singh", "Prefers light blends", "New"],
            ["Order #1019", "priya.p@chai.com", "Paid", "Delivered", "2025-10-19", "2025-10-19", "2025-10-22", "USD", 61, 6, 67, 2, "Rose Radiance Chai", 30.5, "Seattle", "WA", "US", "Priya", "Patel", "Multi-pack purchase", "Returning"],
            ["Order #1020", "rohit@chai.com", "Paid", "Delivered", "2025-10-20", "2025-10-20", "2025-10-22", "USD", 44, 5, 49, 1, "Ginger Zest Chai", 44, "Denver", "CO", "US", "Rohit", "Sharma", "New customer", "New"]
        ], columns=["Name", "Email", "Financial Status", "Fulfillment Status", "Created at", "Paid at", "Fulfilled at", "Currency", "Subtotal", "Shipping", "Total", "Lineitem quantity", "Lineitem name", "Lineitem price", "Shipping City", "Shipping Province", "Shipping Country", "Customer First Name", "Customer Last Name", "Notes", "Tags"])

    orders_df["Created at"] = pd.to_datetime(orders_df["Created at"], errors="coerce")
    return orders_df

def segment_customers(df: pd.DataFrame) -> pd.DataFrame:
    """
    Aggregate and classify customers into behavioral segments.
    Args:
        df (pd.DataFrame): Cleaned orders DataFrame.
    Returns:
        pd.DataFrame: Segmented and aggregated customer DataFrame.
    """
    agg = (
        df.groupby(["Email", "Customer First Name", "Customer Last Name"])
        .agg(
            total_orders=("Name", "count"),
            total_spent=("Total", "sum"),
            avg_order_value=("Total", "mean"),
            last_order=("Created at", "max"),
        )
        .reset_index()
    )
    today = datetime.now()
    agg["last_order"] = pd.to_datetime(agg["last_order"], errors="coerce").dt.tz_localize(None)
    agg["recency_days"] = (today - agg["last_order"]).dt.days

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
    agg.fillna("", inplace=True)
    return agg

def save_to_sheets(df: pd.DataFrame, worksheet_name="Customer_Segments"):
    """
    Optional: Save the segmented results to a new Google Sheets tab.
    Args:
        df (pd.DataFrame): Segmented customer DataFrame.
        worksheet_name (str): Name of the worksheet/tab to write to.
    """
    gc = gspread.service_account(filename="service_account.json")
    ss = gc.open("TwoPeaks_Marketing")
    try:
        ws_old = ss.worksheet(worksheet_name)
        ss.del_worksheet(ws_old)
    except Exception:
        pass
    ws_new = ss.add_worksheet(title=worksheet_name, rows=100, cols=10)
    df_copy = df.copy()
    if "last_order" in df_copy.columns:
        # Convert datetimes to string for upload
        df_copy["last_order"] = df_copy["last_order"].astype(str)
    records = [df_copy.columns.tolist()] + df_copy.astype(str).values.tolist()
    ws_new.update(records)
    print(f"✅ Saved segmented data to '{worksheet_name}' tab.")