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