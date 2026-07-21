import os
from dotenv import load_dotenv
import psycopg2
import pandas as pd

load_dotenv()

conn = psycopg2.connect(
    host="localhost",
    dbname="retail_pipeline",
    user="postgres",
    password=os.getenv("DB_PASSWORD")
)
# Query 1 - total revenue per customer
q1 = pd.read_sql("""
    SELECT 
        c.customer_id,
        SUM(o.order_total) AS total_revenue
    FROM fact_orders o
    JOIN dim_customer c ON o.customer_key = c.customer_key
    GROUP BY c.customer_id
    ORDER BY total_revenue DESC
""", conn)

print("Revenue per customer:")
print(q1)


# Query 2 - rank customers by total revenue
q2 = pd.read_sql("""
    SELECT 
        c.customer_id,
        SUM(o.order_total) AS total_revenue,
        RANK() OVER (ORDER BY SUM(o.order_total) DESC) AS revenue_rank
    FROM fact_orders o
    JOIN dim_customer c ON o.customer_key = c.customer_key
    GROUP BY c.customer_id
    ORDER BY revenue_rank
""", conn)

print("Customer revenue ranking:")
print(q2)


q3 = pd.read_sql("""
    WITH product_revenue AS (
        SELECT 
            o.warehouse_key,
            i.product_key,
            SUM(i.quantity * i.order_price) AS product_revenue
        FROM fact_order_items i
        JOIN fact_orders o ON i.order_key = o.order_key
        GROUP BY o.warehouse_key, i.product_key
    )
    SELECT 
        w.warehouse_name,
        p.product_name,
        pr.product_revenue
    FROM product_revenue pr
    JOIN dim_warehouse w ON pr.warehouse_key = w.warehouse_key
    JOIN dim_product p ON pr.product_key = p.product_key
    ORDER BY w.warehouse_name, pr.product_revenue DESC
""", conn)

print("Product revenue per warehouse:")
print(q3)

# Query 4 - month-over-month revenue change (LAG)
q4 = pd.read_sql("""
    WITH monthly_revenue AS (
        SELECT 
            d.year,
            d.month,
            SUM(o.order_total) AS revenue
        FROM fact_orders o
        JOIN dim_date d ON o.date_key = d.date_key
        GROUP BY d.year, d.month
    )
    SELECT 
        year,
        month,
        revenue,
        LAG(revenue) OVER (ORDER BY year, month) AS prev_month_revenue,
        ROUND(
            (revenue - LAG(revenue) OVER (ORDER BY year, month)) 
            / NULLIF(LAG(revenue) OVER (ORDER BY year, month), 0) * 100, 2
        ) AS pct_change
    FROM monthly_revenue
    ORDER BY year, month
""", conn)

print("Month-over-month revenue change:")
print(q4)


# Query 5 - running total of revenue over time
q5 = pd.read_sql("""
    WITH monthly_revenue AS (
        SELECT 
            d.year,
            d.month,
            SUM(o.order_total) AS revenue
        FROM fact_orders o
        JOIN dim_date d ON o.date_key = d.date_key
        GROUP BY d.year, d.month
    )
    SELECT 
        year,
        month,
        revenue,
        SUM(revenue) OVER (
            ORDER BY year, month 
            ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW
        ) AS running_total
    FROM monthly_revenue
    ORDER BY year, month
""", conn)

print("Running total of revenue:")
print(q5)