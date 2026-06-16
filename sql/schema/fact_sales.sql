CREATE TABLE fact_sales (
    sales_key INT IDENTITY(1,1) PRIMARY KEY,

    order_id INT,

    customer_id INT,
    product_id INT,
    region_id INT,
    date_id INT,

    quantity INT,
    price DECIMAL(10,2),
    discount DECIMAL(5,2),
    total_sales DECIMAL(12,2),

    FOREIGN KEY (customer_id)
        REFERENCES dim_customer(customer_id),

    FOREIGN KEY (product_id)
        REFERENCES dim_product(product_id),

    FOREIGN KEY (region_id)
        REFERENCES dim_region(region_id),

    FOREIGN KEY (date_id)
        REFERENCES dim_date(date_id)
);