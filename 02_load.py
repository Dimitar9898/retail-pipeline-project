import os
from dotenv import load_dotenv
import pandas as pd
import psycopg2

load_dotenv()

conn = psycopg2.connect(
    host="localhost",
    dbname="retail_pipeline",
    user="postgres",
    password=os.getenv("DB_PASSWORD")
)
cur = conn.cursor()

df = pd.read_csv(r'C:\Users\dimit\Documents\retail_pipeline_project\cleaned_data.csv')


df['date'] = pd.to_datetime(df['date'])
print(df.shape)
print(df.columns.tolist())

#redistribute the data into dimension tables

customers = df[['customer_id', 'customer_lat', 'customer_long']].drop_duplicates()

for _, row in customers.iterrows():
    cur.execute("""
        INSERT INTO dim_customer (customer_id, customer_lat, customer_long)
        VALUES (%s, %s, %s)
        ON CONFLICT (customer_id) DO NOTHING 
    """, (row['customer_id'], row['customer_lat'], row['customer_long']))

conn.commit()
print("Loaded dim_customer")


products = df[['product_name']].drop_duplicates()

for _, row in products.iterrows():
    cur.execute("""
        INSERT INTO dim_product (product_name)
        VALUES (%s)
        ON CONFLICT (product_name) DO NOTHING
    """, (row['product_name'],))

conn.commit()
print("Loaded dim_product")


warehouses = df[['nearest_warehouse']].drop_duplicates()

for _, row in warehouses.iterrows():
    cur.execute("""
        INSERT INTO dim_warehouse (warehouse_name)
        VALUES (%s)
        ON CONFLICT (warehouse_name) DO NOTHING
    """, (row['nearest_warehouse'],))

conn.commit()
print("Loaded dim_warehouse")


df['year'] = df['date'].dt.year
df['month'] = df['date'].dt.month
df['day'] = df['date'].dt.day
df['quarter'] = df['date'].dt.quarter


def get_season(month):
    if month in (12, 1, 2):
        return 'Winter'
    elif month in (3, 4, 5):
        return 'Spring'
    elif month in (6, 7, 8):
        return 'Summer'
    else:
        return 'Fall'

df['computed_season'] = df['date'].dt.month.apply(get_season)



# ==========================================================
# LOAD DIM_DATE
# ==========================================================

dates = df[['date', 'year', 'month', 'day', 'quarter', 'computed_season']].drop_duplicates()

for _, row in dates.iterrows():
    cur.execute("""
        INSERT INTO dim_date (full_date, year, month, day, quarter, season)
        VALUES (%s, %s, %s, %s, %s, %s)
        ON CONFLICT (full_date) DO NOTHING
    """, (row['date'], row['year'], row['month'], row['day'], row['quarter'], row['computed_season']))

conn.commit()
print("Loaded dim_date")



# ==========================================================
# BUILD LOOKUP DICTIONARIES
# ==========================================================

cur.execute("SELECT customer_id, customer_key FROM dim_customer")
customer_map = dict(cur.fetchall())

cur.execute("SELECT product_name, product_key FROM dim_product")
product_map = dict(cur.fetchall())

cur.execute("SELECT warehouse_name, warehouse_key FROM dim_warehouse")
warehouse_map = dict(cur.fetchall())

cur.execute("SELECT full_date, date_key FROM dim_date")
date_map = dict(cur.fetchall())


# ==========================================================
# LOAD FACT_ORDER_ITEMS
# ==========================================================

for _, row in df.iterrows():
    cur.execute("""
        INSERT INTO fact_order_items (
            order_id, customer_key, product_key, warehouse_key, date_key,
            quantity, order_price, delivery_charges, coupon_discount,
            order_total, distance_to_nearest_warehouse,
            is_expedited_delivery, is_happy_customer, latest_customer_review
        )
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
    """, (
        row['order_id'],
        customer_map[row['customer_id']],
        product_map[row['product_name']],
        warehouse_map[row['nearest_warehouse']],
        date_map[row['date'].date()],
        row['quantity'],
        row['order_price'],
        row['delivery_charges'],
        row['coupon_discount'],
        row['order_total'],
        row['distance_to_nearest_warehouse'],
        row['is_expedited_delivery'],
        row['is_happy_customer'],
        row['latest_customer_review']
    ))

conn.commit()
print("Loaded fact_order_items")