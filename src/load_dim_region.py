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

# 2. Build region dimension
dim_region = (
    df[["region"]]
    .dropna()
    .drop_duplicates()
)

logger.info(f"Unique regions found: {len(dim_region)}")

# 3. Connect SQL Server
conn = pyodbc.connect(
    r"DRIVER={ODBC Driver 17 for SQL Server};"
    r"SERVER=BHAVIKA\SQLEXPRESS;"
    r"DATABASE=RetailIQDW;"
    r"Trusted_Connection=yes;"
)

cursor = conn.cursor()

# 4. Get existing regions (idempotency)
cursor.execute("SELECT region FROM dim_region")
existing_regions = {row[0] for row in cursor.fetchall()}

# 5. Insert safely
insert_query = """
INSERT INTO dim_region (region)
VALUES (?)
"""

inserted = 0
skipped = 0

for _, row in dim_region.iterrows():
    region = str(row["region"])

    if region in existing_regions:
        skipped += 1
        continue

    cursor.execute(insert_query, region)
    inserted += 1

conn.commit()

logger.info(f"Inserted: {inserted}")
logger.info(f"Skipped: {skipped}")

cursor.close()
conn.close()