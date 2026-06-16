# generate_data.py
# Synthetic Retail Dataset Generator for RetailIQ

import pandas as pd
import numpy as np
import random
from datetime import datetime, timedelta

# ----------------------------
# CONFIGURATION
# ----------------------------

NUM_ROWS = 50000

regions = ["asia", "europe", "usa", "middle east"]

categories = {
    "electronics": ["laptop", "phone", "tablet", "headphones"],
    "fashion": ["shirt", "shoes", "jeans", "jacket"],
    "accessories": ["watch", "belt", "bag"]
}

customer_segments = ["consumer", "corporate", "home_office"]

start_date = datetime(2023, 1, 1)
end_date = datetime(2025, 12, 31)
date_range_days = (end_date - start_date).days


# ----------------------------
# HELPER FUNCTIONS
# ----------------------------

def generate_date():
    random_days = random.randint(0, date_range_days)
    return start_date + timedelta(days=random_days)


def generate_price(category):
    if category == "electronics":
        return round(random.uniform(200, 2000), 2)
    elif category == "fashion":
        return round(random.uniform(20, 200), 2)
    else:
        return round(random.uniform(10, 300), 2)


def generate_discount():
    return round(random.uniform(0, 0.3), 2)


# ----------------------------
# DATA GENERATION
# ----------------------------

data = []

for i in range(1, NUM_ROWS + 1):

    category = random.choice(list(categories.keys()))
    product = random.choice(categories[category])

    quantity = random.randint(1, 5)
    price = generate_price(category)
    discount = generate_discount()

    total_sales = quantity * price * (1 - discount)

    row = {
        "order_id": i,
        "customer_id": random.randint(1000, 9999),
        "customer_segment": random.choice(customer_segments),
        "order_date": generate_date(),
        "region": random.choice(regions),
        "category": category,
        "product": product,
        "quantity": quantity,
        "price": price,
        "discount": discount,
        "total_sales": round(total_sales, 2)
    }

    data.append(row)

# ----------------------------
# CREATE DATAFRAME
# ----------------------------

df = pd.DataFrame(data)

# Sort by date (important for analytics)
df = df.sort_values(by="order_date")

# ----------------------------
# SAVE FILE (BRONZE LAYER)
# ----------------------------

output_path = "data/bronze/raw_sales_large.csv"
df.to_csv(output_path, index=False)

print(f"Dataset generated successfully with {NUM_ROWS} rows")
print(f"Saved at: {output_path}")
print(df.head())
