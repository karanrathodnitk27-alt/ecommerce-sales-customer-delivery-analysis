import pandas as pd
import mysql.connector

# Load CSV
file_path = r"..\Dataset\olist_customers_dataset.csv"
df = pd.read_csv(file_path)

print(f"CSV rows: {len(df)}")

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
INSERT INTO customers
(customer_id, customer_unique_id, customer_zip_code_prefix,
 customer_city, customer_state)
VALUES (%s, %s, %s, %s, %s)
"""

# Convert DataFrame to tuples
data = list(
    df[
        [
            "customer_id",
            "customer_unique_id",
            "customer_zip_code_prefix",
            "customer_city",
            "customer_state"
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

print("Customer import completed successfully.")