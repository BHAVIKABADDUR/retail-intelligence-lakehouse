# db_connection.py

import pyodbc
import logging

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)

logger = logging.getLogger(__name__)


def get_connection():
    """
    Creates SQL Server connection
    """

    try:
        conn = pyodbc.connect(
            r"DRIVER={ODBC Driver 17 for SQL Server};"
            r"SERVER=BHAVIKA\SQLEXPRESS;"
            r"DATABASE=RetailIQDW;"
            r"Trusted_Connection=yes;"
        )

        logger.info("Connected to SQL Server successfully")

        return conn

    except Exception as e:
        logger.error("Database connection failed: %s", str(e))
        return None


if __name__ == "__main__":

    connection = get_connection()

    if connection:
        print("Connection successful!")
        connection.close()