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
# format mixed means not all same format some can be YYYY-MM-DD and some can be MM/DD/YYYY
# day first is for 01/02/2023 to be interpreted as january not february, so month first 
df['date'] = pd.to_datetime(df['date'], format='mixed', dayfirst=False)

# Fill the one missing review
df['latest_customer_review'] = df['latest_customer_review'].fillna('No review')

# Drop full duplicate rows (if any)
df = df.drop_duplicates()

# Standardize warehouse name — title case
df['nearest_warehouse'] = df['nearest_warehouse'].str.title()

# ==========================================================
# VALIDATE ORDER_TOTAL
# ==========================================================

# order_total should equal order_price * (1 - discount%) + delivery_charges
# Rows where this deviates by more than 1% indicate corrupted source data and are removed
df['expected_total'] = round(
    df['order_price'] * (1 - df['coupon_discount'] / 100) + df['delivery_charges'], 2
)

df['pct_diff'] = abs(df['order_total'] - df['expected_total']) / df['expected_total'].replace(0, pd.NA)

bad_orders = df[df['pct_diff'] > 0.01]

print(f"Removing {bad_orders.shape[0]} orders with inconsistent order_total")
print(bad_orders[['order_id', 'order_price', 'coupon_discount', 'delivery_charges', 'order_total', 'expected_total', 'pct_diff']])

df = df[df['pct_diff'] <= 0.01]
df = df.drop(columns=['expected_total', 'pct_diff'])

# ==========================================================
# PARSE SHOPPING CART
# ==========================================================

# converts from string to list of tuples, to loop over and access each product and quantity
def clean_cart(shopping_cart_str):
    cart = ast.literal_eval(shopping_cart_str)
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


#to check for invalid quantities 
if invalid_qty.shape[0] > 0:
    df_exploded = df_exploded[df_exploded['quantity'] > 0]

# ==========================================================
# RESET INDEX
# ==========================================================

# Reset index after all cleaning and exploding as after exploding the index can be messy and not sequential, which can cause issues when saving or further processing the data. Resetting the index ensures that the DataFrame has a clean, sequential index.
df_exploded = df_exploded.reset_index(drop=True)

# ==========================================================
# SAVE CLEANED OUTPUT
# ==========================================================

df_exploded.to_csv(r'C:\Users\dimit\Documents\retail_pipeline_project\cleaned_data.csv', index=False)
print(f"Original rows: {df.shape[0]}, Exploded rows: {df_exploded.shape[0]}")
print("Saved cleaned_data.csv:", df_exploded.shape)