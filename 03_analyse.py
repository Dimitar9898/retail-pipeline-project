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
        SUM(f.order_total) AS total_revenue
    FROM fact_order_items f
    JOIN dim_customer c ON f.customer_key = c.customer_key
    GROUP BY c.customer_id
    ORDER BY total_revenue DESC
""", conn)

print("Revenue per customer:")
print(q1)