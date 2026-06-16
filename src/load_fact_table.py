# load_fact_sales.py
# Loads fact_sales table in RetailIQDW

import pandas as pd
import pyodbc
import logging

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)

logger = logging.getLogger(__name__)

# ── 1. Load Silver data ──────────────────────────────────────────────────────
df = pd.read_csv("data/silver/silver_sales.csv")
df["order_date"] = pd.to_datetime(df["order_date"])
logger.info("Silver data loaded: %s rows", len(df))

# ── 2. Connect to SQL Server ─────────────────────────────────────────────────
conn = pyodbc.connect(
    r"DRIVER={ODBC Driver 17 for SQL Server};"
    r"SERVER=localhost\SQLEXPRESS;"
    r"DATABASE=RetailIQDW;"
    r"Trusted_Connection=yes;"
    r"Connection Timeout=30;"
)
cursor = conn.cursor()
logger.info("Connected to RetailIQDW")

# ── 3. Load dimension lookups into memory ────────────────────────────────────

# dim_customer: customer_id is the same key
cursor.execute("SELECT customer_id FROM dim_customer")
valid_customers = {row[0] for row in cursor.fetchall()}

# dim_product: product_id, product (name column)
cursor.execute("SELECT product_id, product FROM dim_product")
product_map = {row[1].lower(): row[0] for row in cursor.fetchall()}

# dim_region: region_id, region (name column)
cursor.execute("SELECT region_id, region FROM dim_region")
region_map = {row[1].lower(): row[0] for row in cursor.fetchall()}

# dim_date: date_id, order_date
cursor.execute("SELECT date_id, order_date FROM dim_date")
date_map = {str(row[1]): row[0] for row in cursor.fetchall()}

logger.info("Dimension lookups loaded")
logger.info("  Customers: %s", len(valid_customers))
logger.info("  Products : %s", len(product_map))
logger.info("  Regions  : %s", len(region_map))
logger.info("  Dates    : %s", len(date_map))

# ── 4. Clear existing rows (idempotent reload) ───────────────────────────────
cursor.execute("DELETE FROM fact_sales")
conn.commit()
logger.info("Existing fact_sales rows cleared")

# ── 5. Insert rows ───────────────────────────────────────────────────────────
insert_query = """
INSERT INTO fact_sales
    (order_id, customer_id, product_id, region_id, date_id,
     quantity, price, discount, total_sales)
VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
"""

inserted = 0
skipped  = 0

for _, row in df.iterrows():
    cid      = int(row["customer_id"])
    pid      = product_map.get(str(row["product"]).lower())
    rid      = region_map.get(str(row["region"]).lower())
    date_key = str(row["order_date"].date())
    did      = date_map.get(date_key)

    if cid not in valid_customers or pid is None or rid is None or did is None:
        skipped += 1
        continue

    cursor.execute(
        insert_query,
        int(row["order_id"]),
        cid,
        pid,
        rid,
        did,
        int(row["quantity"]),
        float(row["price"]),
        float(row["discount"]),
        float(row["total_sales"])
    )
    inserted += 1

    if inserted % 1000 == 0:
        conn.commit()
        logger.info("  Progress: %s rows inserted...", inserted)

conn.commit()

logger.info("fact_sales load complete")
logger.info("  Inserted : %s", inserted)
logger.info("  Skipped  : %s (FK lookup failed)", skipped)

cursor.close()
conn.close()