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