# Databricks notebook source
# MAGIC %md
# MAGIC # RetailIQ – Databricks Lakehouse Pipeline
# MAGIC
# MAGIC ## Architecture
# MAGIC ```
# MAGIC raw_sales_large.csv (50,000 rows)
# MAGIC           ↓
# MAGIC     Bronze Layer
# MAGIC     (raw ingestion, no transformations)
# MAGIC           ↓
# MAGIC     Silver Layer (silver_sales)
# MAGIC     (type casting, data standardization)
# MAGIC           ↓
# MAGIC     Gold Layer (5 KPI tables)
# MAGIC     ├── gold_revenue_by_category
# MAGIC     ├── gold_revenue_by_region
# MAGIC     ├── gold_top_products
# MAGIC     ├── gold_customer_segment
# MAGIC     └── gold_monthly_trend
# MAGIC ```
# MAGIC
# MAGIC ## Tech Stack
# MAGIC - Apache Spark (PySpark)
# MAGIC - Databricks Lakehouse
# MAGIC - Delta Lake (persistent tables)
# MAGIC
# MAGIC ## Dataset
# MAGIC - 50,000 synthetic retail transactions
# MAGIC - Date range: 2023 – 2025
# MAGIC - Products: Electronics, Fashion, Accessories
# MAGIC - Regions: Asia, Europe, USA, Middle East
# MAGIC - Customer Segments: Consumer, Corporate, Home Office
# MAGIC
# MAGIC ## Key Results
# MAGIC | Gold Table | Purpose |
# MAGIC |---|---|
# MAGIC | gold_revenue_by_category | Revenue split by product category |
# MAGIC | gold_revenue_by_region | Revenue performance across regions |
# MAGIC | gold_top_products | Top performing products by revenue |
# MAGIC | gold_customer_segment | Revenue by customer type |
# MAGIC | gold_monthly_trend | Month-over-month revenue trend |

# COMMAND ----------

spark

# COMMAND ----------

data = [
    ("Laptop", "Electronics", 2, 800),
    ("Phone", "Electronics", 3, 500),
    ("Shoes", "Fashion", 5, 100)
]

columns = ["product", "category", "quantity", "price"]

df = spark.createDataFrame(data, columns)

# COMMAND ----------

df.show()

# COMMAND ----------

from pyspark.sql.functions import col

df = df.withColumn(
    "total_sales",
    col("quantity") * col("price")
)

# COMMAND ----------

df.show()

# COMMAND ----------

df.select("product", "total_sales").show()

# COMMAND ----------

df.filter(
    col("total_sales") > 1000
).show()

# COMMAND ----------

from pyspark.sql.functions import sum

df.groupBy("category") \
  .agg(sum("total_sales").alias("revenue")) \
  .show()

# COMMAND ----------

bronze_df = spark.read.option("header", "true").csv(
    "/Volumes/workspace/default/retailiq_bronze/raw_sales_large.csv"
)

# COMMAND ----------

bronze_df.printSchema()

# COMMAND ----------

bronze_df.count()

# COMMAND ----------

from pyspark.sql.functions import col

silver_df = bronze_df \
    .withColumn("quantity", col("quantity").cast("int")) \
    .withColumn("price", col("price").cast("double")) \
    .withColumn("discount", col("discount").cast("double")) \
    .withColumn("total_sales", col("total_sales").cast("double"))

# COMMAND ----------

silver_df.printSchema()

# COMMAND ----------

from pyspark.sql.functions import sum

gold_category_df = silver_df.groupBy("category") \
    .agg(
        sum("total_sales").alias("revenue")
    ) \
    .orderBy("revenue", ascending=False)

gold_category_df.show()


# COMMAND ----------

silver_df.write \
    .mode("overwrite") \
    .saveAsTable("silver_sales")

# COMMAND ----------

spark.sql("SHOW TABLES").show()

# COMMAND ----------

spark.sql("""
SELECT *
FROM silver_sales
LIMIT 5
""").show()

# COMMAND ----------

silver_table_df = spark.table("silver_sales")

silver_table_df.show(5)

# COMMAND ----------

silver_table_df.count()

# COMMAND ----------

from pyspark.sql.functions import sum

gold_revenue_by_category = (
    silver_table_df
    .groupBy("category")
    .agg(
        sum("total_sales").alias("revenue")
    )
    .orderBy("revenue", ascending=False)
)

# COMMAND ----------

gold_revenue_by_category.show()

# COMMAND ----------

gold_revenue_by_category.write \
    .mode("overwrite") \
    .saveAsTable("gold_revenue_by_category")

# COMMAND ----------

spark.sql("""
SELECT *
FROM gold_revenue_by_category
""").show()

# COMMAND ----------

from pyspark.sql.functions import sum

gold_revenue_by_region = (
    silver_table_df
    .groupBy("region")
    .agg(
        sum("total_sales").alias("revenue")
    )
    .orderBy("revenue", ascending=False)
)

# COMMAND ----------

gold_revenue_by_region.show()

# COMMAND ----------

gold_revenue_by_region.write \
    .mode("overwrite") \
    .saveAsTable("gold_revenue_by_region")

# COMMAND ----------

from pyspark.sql.functions import sum

gold_top_products = (
    silver_table_df
    .groupBy("product")
    .agg(
        sum("total_sales").alias("revenue")
    )
    .orderBy("revenue", ascending=False)
)

# COMMAND ----------

gold_top_products.show()

# COMMAND ----------

gold_top_products.write \
    .mode("overwrite") \
    .saveAsTable("gold_top_products")

# COMMAND ----------

spark.sql("SHOW TABLES").show(truncate=False)

# COMMAND ----------

gold_customer_segment = (
    silver_table_df
    .groupBy("customer_segment")
    .agg(sum("total_sales").alias("revenue"))
    .orderBy("revenue", ascending=False)
)
gold_customer_segment.write.mode("overwrite").saveAsTable("gold_customer_segment")

# COMMAND ----------

from pyspark.sql.functions import month, year

gold_monthly_trend = (
    silver_table_df
    .withColumn("month", month("order_date"))
    .withColumn("year", year("order_date"))
    .groupBy("year", "month")
    .agg(sum("total_sales").alias("revenue"))
    .orderBy("year", "month")
)
gold_monthly_trend.write.mode("overwrite").saveAsTable("gold_monthly_trend")

# COMMAND ----------

spark.sql("SHOW TABLES").show(truncate=False)