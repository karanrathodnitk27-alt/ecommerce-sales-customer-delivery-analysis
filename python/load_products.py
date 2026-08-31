import pandas as pd
import mysql.connector

# Load CSV
file_path = r"..\Dataset\olist_products_dataset.csv"
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
INSERT INTO products (
    product_id,
    product_category_name,
    product_name_length,
    product_description_length,
    product_photos_qty,
    product_weight_g,
    product_length_cm,
    product_height_cm,
    product_width_cm
)
VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
"""

# Convert NaN to None because MySQL understands NULL, not NaN
df = df.astype(object).where(pd.notna(df), None)

data = list(
    df[
        [
            "product_id",
            "product_category_name",
            "product_name_lenght",
            "product_description_lenght",
            "product_photos_qty",
            "product_weight_g",
            "product_length_cm",
            "product_height_cm",
            "product_width_cm"
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

print("Product import completed successfully.")
