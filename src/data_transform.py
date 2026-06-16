# data_transform.py
# Transformation layer for RetailIQ pipeline

import pandas as pd
import logging

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)

logger = logging.getLogger(__name__)


def transform_data(df):

    if df is None:
        logger.error("No data to transform")
        return None

    try:
        logger.info("Starting transformation layer...")

        # 1. Handle missing values (basic safety)
        df = df.dropna(subset=["quantity", "price"])

        # 2. Create total sales column
        df["total_sales"] = df["quantity"] * df["price"]

        # 3. Safe string normalization (IMPORTANT FIX)
        for col in ["product", "category", "region"]:
            if col in df.columns:
                df[col] = df[col].astype(str).str.lower()

        logger.info("Transformation complete")

        print("\nSample data:")
        print(df.head())

        # 4. Save Silver Layer output
        output_path = "data/silver/silver_sales.csv"
        df.to_csv(output_path, index=False)

        logger.info("Silver layer saved at: %s", output_path)

        # 5. Revenue summary
        logger.info("Total revenue: %s", df["total_sales"].sum())

        return df

    except Exception as e:
        logger.error("Error in transformation layer: %s", str(e))
        return None


if __name__ == "__main__":
    print("Run this through data_loader pipeline later")