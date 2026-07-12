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

# date column had mixed formats (some YYYY-MM-DD, some MM-DD-YYYY)
# so a single fixed format broke on parsing - using 'mixed' lets pandas
# infer the format row by row instead
df['date'] = pd.to_datetime(df['date'], format='mixed', dayfirst=False)

# only 1 missing review in the whole dataset, just fill it instead of dropping the row
df['latest_customer_review'] = df['latest_customer_review'].fillna('No review')

# drop any full duplicate rows if they exist
df = df.drop_duplicates()

# ==========================================================
# PARSE SHOPPING CART
# ==========================================================

# shopping_cart is stored as a string that looks like a list of tuples
# ast.literal_eval safely turns it back into an actual Python list
df['shopping_cart'] = df['shopping_cart'].apply(ast.literal_eval)

# check for empty carts before exploding - an empty list would break
# the tuple unpacking step later on
empty_carts = df[df['shopping_cart'].apply(lambda x: len(x) == 0)]
print("Empty cart rows:", empty_carts.shape[0])

if empty_carts.shape[0] > 0:
    df = df[df['shopping_cart'].apply(lambda x: len(x) > 0)]

# explode so each product in the cart gets its own row
df_exploded = df.explode('shopping_cart')

# split each (product_name, quantity) tuple into its own columns
df_exploded[['product_name', 'quantity']] = pd.DataFrame(
    df_exploded['shopping_cart'].tolist(), index=df_exploded.index
)

df_exploded = df_exploded.drop(columns=['shopping_cart'])

print(df_exploded.shape)
print(df_exploded.head(10))

# make sure quantity is actually numeric, coerce anything unparseable to NaN
df_exploded['quantity'] = pd.to_numeric(df_exploded['quantity'], errors='coerce')

# ==========================================================
# VALIDATE EXPLODED DATA
# ==========================================================

print(df_exploded['quantity'].describe())          # catch negative/zero/absurd values
print(df_exploded['product_name'].nunique())
print(df_exploded.isnull().sum())                  # nulls can appear post-explode

# zero or negative quantity doesn't make sense for an order, flag and drop
invalid_qty = df_exploded[df_exploded['quantity'] <= 0]
print("Invalid quantity rows (<=0):", invalid_qty.shape[0])

if invalid_qty.shape[0] > 0:
    df_exploded = df_exploded[df_exploded['quantity'] > 0]

# ==========================================================
# RESET INDEX
# ==========================================================

# index has duplicates after explode since each original row repeats
df_exploded = df_exploded.reset_index(drop=True)

# ==========================================================
# SAVE CLEANED OUTPUT
# ==========================================================

df_exploded.to_csv(r'C:\Users\dimit\Documents\retail_pipeline_project\cleaned_data.csv', index=False)

print("Saved cleaned_data.csv:", df_exploded.shape)