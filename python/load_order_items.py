import pandas as pd
import mysql.connector

# -----------------------------
# 1. Load CSV
# -----------------------------
file_path = r"..\Dataset\olist_order_items_dataset.csv"

df = pd.read_csv(file_path)

print(f"CSV rows: {len(df)}")

# -----------------------------
# 2. Convert date column
# -----------------------------
df["shipping_limit_date"] = pd.to_datetime(
    df["shipping_limit_date"],
    errors="coerce"
)

# Convert missing values to None
df = df.astype(object).where(pd.notna(df), None)

# -----------------------------
# 3. Connect to MySQL
# -----------------------------
password = input("Enter MySQL root password: ")

connection = mysql.connector.connect(
    host="localhost",
    user="root",
    password=password,
    database="retail_bi"
)

cursor = connection.cursor()

# -----------------------------
# 4. Insert query
# -----------------------------
query = """
INSERT INTO order_items (
    order_id,
    order_item_id,
    product_id,
    seller_id,
    shipping_limit_date,
    price,
    freight_value
)
VALUES (%s, %s, %s, %s, %s, %s, %s)
"""

# -----------------------------
# 5. Prepare records
# -----------------------------
data = []

for row in df.itertuples(index=False, name=None):

    converted_row = list(row)

    # Convert Pandas Timestamp → Python datetime
    if converted_row[4] is not None:
        converted_row[4] = converted_row[4].to_pydatetime()

    data.append(tuple(converted_row))

# -----------------------------
# 6. Insert in batches
# -----------------------------
batch_size = 5000

for i in range(0, len(data), batch_size):

    batch = data[i:i + batch_size]

    cursor.executemany(query, batch)
    connection.commit()

    print(
        f"Inserted {min(i + batch_size, len(data))} / {len(data)}"
    )

# -----------------------------
# 7. Close connection
# -----------------------------
cursor.close()
connection.close()

print("Order items import completed successfully.")
