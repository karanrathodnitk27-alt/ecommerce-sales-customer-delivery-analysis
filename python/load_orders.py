import pandas as pd
import mysql.connector

# -----------------------------
# 1. Load CSV
# -----------------------------
file_path = r"..\Dataset\olist_orders_dataset.csv"

df = pd.read_csv(file_path)

print(f"CSV rows: {len(df)}")

# -----------------------------
# 2. Convert date columns
# -----------------------------
date_columns = [
    "order_purchase_timestamp",
    "order_approved_at",
    "order_delivered_carrier_date",
    "order_delivered_customer_date",
    "order_estimated_delivery_date"
]

for column in date_columns:
    df[column] = pd.to_datetime(df[column], errors="coerce")

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
# 4. SQL INSERT
# -----------------------------
query = """
INSERT INTO orders (
    order_id,
    customer_id,
    order_status,
    order_purchase_timestamp,
    order_approved_at,
    order_delivered_carrier_date,
    order_delivered_customer_date,
    order_estimated_delivery_date
)
VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
"""

# -----------------------------
# 5. Prepare records
# -----------------------------
data = []

for row in df.itertuples(index=False, name=None):

    converted_row = list(row)

    # Convert Pandas Timestamp → Python datetime
    for i in range(3, 8):
        if converted_row[i] is not None:
            converted_row[i] = converted_row[i].to_pydatetime()

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

print("Orders import completed successfully.")
