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
df['date'] = pd.to_datetime(df['date'], format='mixed', dayfirst=False)

# Fill the one missing review
df['latest_customer_review'] = df['latest_customer_review'].fillna('No review')

# Drop full duplicate rows (if any)
df = df.drop_duplicates()

# Standardize warehouse name — title case
df['nearest_warehouse'] = df['nearest_warehouse'].str.title()

# ==========================================================
# PARSE SHOPPING CART
# ==========================================================

# shopping_cart is stored as a string representation of a list of tuples
# ast.literal_eval safely converts it back to an actual Python list
# Title case applied to product names during parsing
def clean_cart(cart_str):
    cart = ast.literal_eval(cart_str)
    return [(product.title(), qty) for product, qty in cart]

df['shopping_cart'] = df['shopping_cart'].apply(clean_cart)

# Check for empty carts before exploding
empty_carts = df[df['shopping_cart'].apply(lambda x: len(x) == 0)]
print("Empty cart rows:", empty_carts.shape[0])

if empty_carts.shape[0] > 0:
    df = df[df['shopping_cart'].apply(lambda x: len(x) > 0)]

# Explode into one row per product per order
df_exploded = df.explode('shopping_cart')

# Split the tuple into separate columns
df_exploded[['product_name', 'quantity']] = pd.DataFrame(
    df_exploded['shopping_cart'].tolist(), index=df_exploded.index
)

df_exploded = df_exploded.drop(columns=['shopping_cart'])

print(df_exploded.shape)
print(df_exploded.head(10))

df_exploded['quantity'] = pd.to_numeric(df_exploded['quantity'], errors='coerce')

# ==========================================================
# VALIDATE EXPLODED DATA
# ==========================================================

print(df_exploded['quantity'].describe())
print(df_exploded['product_name'].nunique())
print(df_exploded.isnull().sum())

invalid_qty = df_exploded[df_exploded['quantity'] <= 0]
print("Invalid quantity rows (<=0):", invalid_qty.shape[0])

product_name_map = {
    'Istream': 'iStream',
    'Peartv': 'pearTV',
    'Iassist Line': 'iAssist Line',
}
df_exploded['product_name'] = df_exploded['product_name'].replace(product_name_map)

if invalid_qty.shape[0] > 0:
    df_exploded = df_exploded[df_exploded['quantity'] > 0]

# ==========================================================
# RESET INDEX
# ==========================================================

df_exploded = df_exploded.reset_index(drop=True)

# ==========================================================
# SAVE CLEANED OUTPUT
# ==========================================================

df_exploded.to_csv(r'C:\Users\dimit\Documents\retail_pipeline_project\cleaned_data.csv', index=False)
print(f"Original rows: {df.shape[0]}, Exploded rows: {df_exploded.shape[0]}")
print("Saved cleaned_data.csv:", df_exploded.shape)