# data_loader.py
# Extract + Transform pipeline entry point

import pandas as pd
import logging
from data_transform import transform_data
from data_gold import create_gold_layer

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)

logger = logging.getLogger(__name__)


def load_data(file_path):
    """
    Loads CSV and sends it through ETL pipeline
    """

    try:
        logger.info("Starting ETL pipeline...")

        # 1. Extract
        df = pd.read_csv(file_path)
        logger.info("Data loaded successfully")
        logger.info("Shape: %s", df.shape)
        logger.info("Rows loaded: %s", len(df))

        logger.info("Sending data to transformation layer")

        # 2. Transform
        transformed_df = transform_data(df)

        if transformed_df is None:
            logger.error("Transformation failed. Stopping pipeline.")
            return None

        logger.info("Transformation completed successfully")
        logger.info("Rows after transform: %s", len(transformed_df))

        # 3. Gold Layer
        gold_output = create_gold_layer(transformed_df)

        if gold_output is None:
            logger.error("Gold layer generation failed.")
        else:
            logger.info("Gold layer generated successfully")

        logger.info("ETL pipeline completed successfully")

        return transformed_df

    except Exception as e:
        logger.error("Error in ETL pipeline: %s", str(e))
        return None


if __name__ == "__main__":

    sample_path = "data/bronze/raw_sales_large.csv"

    final_df = load_data(sample_path)

    if final_df is not None:
        print("\n--- FINAL OUTPUT ---")
        print(final_df.head())
    else:
        logger.error("Pipeline failed. No output generated.")