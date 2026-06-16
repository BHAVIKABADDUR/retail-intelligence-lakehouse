CREATE TABLE dim_product (
    product_id INT IDENTITY(1,1) PRIMARY KEY,
    product VARCHAR(100),
    category VARCHAR(100)
);