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

# 2. Build product dimension
dim_product = (
    df[["product", "category"]]
    .dropna()
    .drop_duplicates(subset=["product"])
)

logger.info(f"Unique products found: {len(dim_product)}")

# 3. Connect SQL Server
conn = pyodbc.connect(
    r"DRIVER={ODBC Driver 17 for SQL Server};"
    r"SERVER=BHAVIKA\SQLEXPRESS;"
    r"DATABASE=RetailIQDW;"
    r"Trusted_Connection=yes;"
)

cursor = conn.cursor()

# 4. Get existing products (for idempotency)
cursor.execute("SELECT product FROM dim_product")
existing_products = {row[0] for row in cursor.fetchall()}

# 5. Insert safely
insert_query = """
INSERT INTO dim_product (product, category)
VALUES (?, ?)
"""

inserted = 0
skipped = 0

for _, row in dim_product.iterrows():
    product = str(row["product"])

    if product in existing_products:
        skipped += 1
        continue

    cursor.execute(insert_query, product, str(row["category"]))
    inserted += 1

conn.commit()

logger.info(f"Inserted: {inserted}")
logger.info(f"Skipped: {skipped}")

cursor.close()
conn.close()