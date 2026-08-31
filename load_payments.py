import pandas as pd
import mysql.connector

# Load CSV
file_path = r"..\Dataset\olist_order_payments_dataset.csv"
df = pd.read_csv(file_path)

print(f"CSV rows: {len(df)}")

# Convert missing values to None
df = df.astype(object).where(pd.notna(df), None)

# Connect to MySQL
password = input("Enter MySQL root password: ")

connection = mysql.connector.connect(
    host="localhost",
    user="root",
    password=password,
    database="retail_bi"
)

cursor = connection.cursor()

query = """
INSERT INTO payments (
    order_id,
    payment_sequential,
    payment_type,
    payment_installments,
    payment_value
)
VALUES (%s, %s, %s, %s, %s)
"""

data = list(
    df[
        [
            "order_id",
            "payment_sequential",
            "payment_type",
            "payment_installments",
            "payment_value"
        ]
    ].itertuples(index=False, name=None)
)

# Insert in batches
batch_size = 5000

for i in range(0, len(data), batch_size):

    batch = data[i:i + batch_size]

    cursor.executemany(query, batch)
    connection.commit()

    print(f"Inserted {min(i + batch_size, len(data))} / {len(data)}")

cursor.close()
connection.close()

print("Payments import completed successfully.")