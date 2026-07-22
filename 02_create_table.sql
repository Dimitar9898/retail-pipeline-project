CREATE TABLE dim_customer (
    customer_key SERIAL PRIMARY KEY,
    customer_id VARCHAR(20) NOT NULL UNIQUE,
    customer_lat FLOAT NOT NULL,
    customer_long FLOAT NOT NULL
);

CREATE TABLE dim_product (
    product_key SERIAL PRIMARY KEY,
    product_name VARCHAR(100) NOT NULL UNIQUE
);

CREATE TABLE dim_warehouse (
    warehouse_key SERIAL PRIMARY KEY,
    warehouse_name VARCHAR(50) NOT NULL UNIQUE
);

CREATE TABLE dim_date (
    date_key SERIAL PRIMARY KEY,
    full_date DATE NOT NULL UNIQUE,
    year INT NOT NULL,
    month INT NOT NULL,
    day INT NOT NULL,
    quarter INT NOT NULL,
    season VARCHAR(10) NOT NULL
);

CREATE TABLE fact_orders (
    order_key SERIAL PRIMARY KEY,
    order_id VARCHAR(20) NOT NULL UNIQUE,
    customer_key INT NOT NULL REFERENCES dim_customer(customer_key),
    warehouse_key INT NOT NULL REFERENCES dim_warehouse(warehouse_key),
    date_key INT NOT NULL REFERENCES dim_date(date_key),
    delivery_charges NUMERIC(10,2) NOT NULL,
    coupon_discount INT NOT NULL,
    order_total NUMERIC(10,2) NOT NULL,
    distance_to_nearest_warehouse FLOAT NOT NULL,
    is_expedited_delivery BOOLEAN NOT NULL,
    is_happy_customer BOOLEAN NOT NULL,
    latest_customer_review TEXT
);


CREATE TABLE fact_order_items (
    order_item_key SERIAL PRIMARY KEY,
    order_key INT NOT NULL REFERENCES fact_orders(order_key),
    product_key INT NOT NULL REFERENCES dim_product(product_key),
    quantity INT NOT NULL,
    order_price NUMERIC(10,2) NOT NULL
);