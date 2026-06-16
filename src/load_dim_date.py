import pandas as pd
import pyodbc
import logging

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)

logger = logging.getLogger(__name__)

# 1. Load Silver data
df = pd.read_csv("data/silver/silver_sales.csv")

# 2. Validate date column
if "order_date" not in df.columns:
    raise Exception("order_date column not found in dataset")

df["order_date"] = pd.to_datetime(df["order_date"])

# 3. Build dim_date correctly (MATCH YOUR SQL SCHEMA)
dim_date = pd.DataFrame()

dim_date["order_date"] = df["order_date"].dt.date
dim_date["year"] = df["order_date"].dt.year
dim_date["month"] = df["order_date"].dt.month
dim_date["quarter"] = df["order_date"].dt.quarter
dim_date["day"] = df["order_date"].dt.day

dim_date = dim_date.drop_duplicates()

logger.info(f"Unique dates found: {len(dim_date)}")

# 4. Connect SQL Server
conn = pyodbc.connect(
    r"DRIVER={ODBC Driver 17 for SQL Server};"
    r"SERVER=localhost\SQLEXPRESS;"
    r"DATABASE=RetailIQDW;"
    r"Trusted_Connection=yes;"
    r"Connection Timeout=30;"
)

cursor = conn.cursor()

# 5. Get existing dates from SQL (FIXED COLUMN NAME)
cursor.execute("SELECT order_date FROM dim_date")
existing_dates = {row[0] for row in cursor.fetchall()}

# 6. Insert safely
insert_query = """
INSERT INTO dim_date (order_date, year, month, quarter, day)
VALUES (?, ?, ?, ?, ?)
"""

inserted = 0
skipped = 0

for _, row in dim_date.iterrows():

    if row["order_date"] in existing_dates:
        skipped += 1
        continue

    cursor.execute(
        insert_query,
        str(row["order_date"]),
        int(row["year"]),
        int(row["month"]),
        int(row["quarter"]),
        int(row["day"])
    )

    inserted += 1

conn.commit()

logger.info(f"Inserted: {inserted}")
logger.info(f"Skipped: {skipped}")

cursor.close()
conn.close()