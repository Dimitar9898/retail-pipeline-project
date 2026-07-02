import pandas as pd
import ast

df = pd.read_csv(r'C:\Users\dimit\Documents\retail_pipeline_project\dirty_data.csv')

# ==========================================================
# INSPECTION
# ==========================================================

print(df.shape)
print(df.dtypes)
print(df.isnull().sum())
print(df.head(5))
print(df.duplicated().sum())
print(df['date'].head(10))
print(df['shopping_cart'].head(5))

# ==========================================================
# BASIC CLEANING
# ==========================================================

# Fix date column from string to proper date type
df['date'] = pd.to_datetime(df['date'])

# Fill the one missing review
df['latest_customer_review'] = df['latest_customer_review'].fillna('No review')

# Drop full duplicate rows (if any)
df = df.drop_duplicates()

# ==========================================================
# PARSE SHOPPING CART
# ==========================================================

# shopping_cart is stored as a string representation of a list of tuples
# ast.literal_eval safely converts it back to an actual Python list
df['shopping_cart'] = df['shopping_cart'].apply(ast.literal_eval)

# Explode into one row per product per order
df_exploded = df.explode('shopping_cart')

# Split the tuple into separate columns
df_exploded[['product_name', 'quantity']] = pd.DataFrame(
    df_exploded['shopping_cart'].tolist(), index=df_exploded.index
)

df_exploded = df_exploded.drop(columns=['shopping_cart'])

print(df_exploded.shape)
print(df_exploded.head(10))