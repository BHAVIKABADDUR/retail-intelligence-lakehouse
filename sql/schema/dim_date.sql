CREATE TABLE dim_date (
    date_id INT PRIMARY KEY,
    order_date DATE,
    year INT,
    month INT,
    quarter VARCHAR(10),
    day INT
);