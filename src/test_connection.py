import pyodbc
import pandas as pd

conn = pyodbc.connect(
    r"DRIVER={ODBC Driver 17 for SQL Server};"
    r"SERVER=BHAVIKA\SQLEXPRESS;"
    r"DATABASE=RetailIQDW;"
    r"Trusted_Connection=yes;"
)

query = """
SELECT TABLE_NAME
FROM INFORMATION_SCHEMA.TABLES
WHERE TABLE_TYPE = 'BASE TABLE'
"""

df = pd.read_sql(query, conn)

print(df)

conn.close()