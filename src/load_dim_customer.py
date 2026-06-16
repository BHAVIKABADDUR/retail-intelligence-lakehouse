import pandas as pd
import pyodbc
import logging

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)

logger = logging.getLogger(__name__)

# 1. Read Silver data
df = pd.read_csv("data/silver/silver_sales.csv")

# 2. Build clean dimension (REMOVE DUPLICATES PROPERLY)
dim_customer = (
    df[["customer_id", "customer_segment"]]
    .dropna()
    .drop_duplicates(subset=["customer_id"])
)

logger.info(f"Unique customers after cleaning: {len(dim_customer)}")

# 3. Connect SQL Server
conn = pyodbc.connect(
    r"DRIVER={ODBC Driver 17 for SQL Server};"
    r"SERVER=BHAVIKA\SQLEXPRESS;"
    r"DATABASE=RetailIQDW;"
    r"Trusted_Connection=yes;"
)

cursor = conn.cursor()

# 4. Get existing IDs from SQL
cursor.execute("SELECT customer_id FROM dim_customer")
existing_ids = set(row[0] for row in cursor.fetchall())

# 5. Insert safely
insert_query = """
INSERT INTO dim_customer (customer_id, customer_segment)
VALUES (?, ?)
"""

inserted = 0
skipped = 0

for _, row in dim_customer.iterrows():
    cid = int(row["customer_id"])

    if cid in existing_ids:
        skipped += 1
        continue

    try:
        cursor.execute(insert_query, cid, str(row["customer_segment"]))
        inserted += 1
    except Exception as e:
        logger.warning(f"Skipping customer_id={cid} due to error: {e}")
        skipped += 1

conn.commit()

logger.info(f"Inserted: {inserted}")
logger.info(f"Skipped: {skipped}")

cursor.close()
conn.close()