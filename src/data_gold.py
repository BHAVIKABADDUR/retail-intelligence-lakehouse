# data_gold.py
# Gold layer: Business KPI generation

import pandas as pd
import logging

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)

logger = logging.getLogger(__name__)


def create_gold_layer(df):
    """
    Converts Silver data into business-ready Gold metrics
    """

    if df is None:
        logger.error("No data provided for Gold layer")
        return None

    try:
        logger.info("Creating Gold Layer KPIs")

        # 1. Revenue by Category
        revenue_by_category = df.groupby("category")["total_sales"].sum().reset_index()

        # 2. Revenue by Region
        revenue_by_region = df.groupby("region")["total_sales"].sum().reset_index()

        # 3. Top Products
        top_products = df.groupby("product")["total_sales"].sum().sort_values(ascending=False).reset_index()

        logger.info("Gold KPIs generated successfully")

        print("\nRevenue by Category:\n", revenue_by_category)
        print("\nRevenue by Region:\n", revenue_by_region)
        print("\nTop Products:\n", top_products)

        # Save Gold outputs
        revenue_by_category.to_csv("data/gold/revenue_by_category.csv", index=False)
        revenue_by_region.to_csv("data/gold/revenue_by_region.csv", index=False)
        top_products.to_csv("data/gold/top_products.csv", index=False)

        logger.info("Gold layer saved successfully")

        return {
            "category": revenue_by_category,
            "region": revenue_by_region,
            "products": top_products
        }

    except Exception as e:
        logger.error("Error in Gold layer: %s", str(e))
        return None


if __name__ == "__main__":
    logger.info("Gold layer module ready")