import pandas as pd
import mysql.connector

# Load CSV
file_path = r"..\Dataset\olist_order_reviews_dataset.csv"
df = pd.read_csv(file_path)

print(f"CSV rows: {len(df)}")

# Convert date columns
date_columns = [
    "review_creation_date",
    "review_answer_timestamp"
]

for column in date_columns:
    df[column] = pd.to_datetime(df[column], errors="coerce")

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
INSERT INTO reviews (
    review_id,
    order_id,
    review_score,
    review_comment_title,
    review_comment_message,
    review_creation_date,
    review_answer_timestamp
)
VALUES (%s, %s, %s, %s, %s, %s, %s)
"""

data = []

for row in df.itertuples(index=False, name=None):

    converted_row = list(row)

    # Convert Pandas timestamps to Python datetime
    for i in [5, 6]:
        if converted_row[i] is not None:
            converted_row[i] = converted_row[i].to_pydatetime()

    data.append(tuple(converted_row))

# Insert in batches
batch_size = 5000

for i in range(0, len(data), batch_size):

    batch = data[i:i + batch_size]

    cursor.executemany(query, batch)
    connection.commit()

    print(f"Inserted {min(i + batch_size, len(data))} / {len(data)}")

cursor.close()
connection.close()

print("Reviews import completed successfully.")