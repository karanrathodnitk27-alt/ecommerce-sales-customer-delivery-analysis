import matplotlib.pyplot as plt
from sqlalchemy import create_engine, URL
import pandas as pd

# ---------------------------------------
# 1. Connect to MySQL
# ---------------------------------------

password = "Karan@77950"

connection_url = URL.create(
    drivername="mysql+pymysql",
    username="root",
    password=password,
    host="localhost",
    port=3306,
    database="retail_bi"
)
print("Username: root")
print("Host: localhost")
print("Port: 3306")
print("Database: retail_bi")
print("Password is set:", bool(password))

engine = create_engine(connection_url)
print("MySQL connection successful!")


# ---------------------------------------
# 2. Load tables into Pandas
# ---------------------------------------

orders = pd.read_sql("SELECT * FROM orders", engine)
customers = pd.read_sql("SELECT * FROM customers", engine)
order_items = pd.read_sql("SELECT * FROM order_items", engine)
payments = pd.read_sql("SELECT * FROM payments", engine)
products = pd.read_sql("SELECT * FROM products", engine)
reviews = pd.read_sql("SELECT * FROM reviews", engine)
sellers = pd.read_sql("SELECT * FROM sellers", engine)
category_translation = pd.read_sql(
    "SELECT * FROM category_translation",
    engine
)

# ---------------------------------------
# 3. DATA PROFILING
# ---------------------------------------

tables = {
    "orders": orders,
    "customers": customers,
    "order_items": order_items,
    "payments": payments,
    "products": products,
    "reviews": reviews,
    "sellers": sellers,
    "category_translation": category_translation
}


# ---------------------------------------
# 3.1 Basic information
# ---------------------------------------

for name, df in tables.items():

    print("\n" + "=" * 60)
    print(f"TABLE: {name}")
    print("=" * 60)

    print("\nShape:")
    print(df.shape)

    print("\nColumns:")
    print(df.columns.tolist())

    print("\nData Types:")
    print(df.dtypes)

    # ---------------------------------------
# 3.2 Unique values
# ---------------------------------------

for name, df in tables.items():

    print("\n" + "=" * 60)
    print(f"UNIQUE VALUES: {name}")
    print("=" * 60)

    print(df.nunique())

    # ---------------------------------------
# 3.3 Missing values
# ---------------------------------------

for name, df in tables.items():

    print("\n" + "=" * 60)
    print(f"MISSING VALUES: {name}")
    print("=" * 60)

    missing = df.isnull().sum()

    print(missing[missing > 0])

    # ---------------------------------------
# 3.4 Duplicate rows
# ---------------------------------------

for name, df in tables.items():

    print("\n" + "=" * 60)
    print(f"DUPLICATES: {name}")
    print("=" * 60)

    print("Duplicate rows:", df.duplicated().sum())

# ---------------------------------------
# 4. DATA QUALITY ANALYSIS
# ---------------------------------------

# 4.1 Order status distribution
print("\n" + "=" * 60)
print("ORDER STATUS DISTRIBUTION")
print("=" * 60)

print(orders["order_status"].value_counts())


# ---------------------------------------
# 4.2 Missing values in orders by status
# ---------------------------------------

print("\n" + "=" * 60)
print("MISSING ORDER DATES BY ORDER STATUS")
print("=" * 60)

print(
    orders.groupby("order_status")[
        [
            "order_approved_at",
            "order_delivered_carrier_date",
            "order_delivered_customer_date"
        ]
    ].apply(lambda x: x.isnull().sum())
)

# ---------------------------------------
# 4.3 Delivery performance
# ---------------------------------------

orders["delivery_days"] = (
    orders["order_delivered_customer_date"]
    - orders["order_purchase_timestamp"]
).dt.total_seconds() / (24 * 60 * 60)

orders["estimated_delivery_days"] = (
    orders["order_estimated_delivery_date"]
    - orders["order_purchase_timestamp"]
).dt.total_seconds() / (24 * 60 * 60)

orders["delivery_delay_days"] = (
    orders["order_delivered_customer_date"]
    - orders["order_estimated_delivery_date"]
).dt.total_seconds() / (24 * 60 * 60)


print("\n" + "=" * 60)
print("DELIVERY METRICS")
print("=" * 60)

print(
    orders[
        [
            "delivery_days",
            "estimated_delivery_days",
            "delivery_delay_days"
        ]
    ].describe()
)
# ---------------------------------------
# 4.4 Product data quality
# ---------------------------------------

print("\n" + "=" * 60)
print("PRODUCT DATA QUALITY")
print("=" * 60)

product_missing = products.isnull().sum()

print(product_missing[product_missing > 0])

print("\nProducts without category:")
print(
    products["product_category_name"]
    .isnull()
    .sum()
)

# ---------------------------------------
# 4.5 Product numerical statistics
# ---------------------------------------

print("\n" + "=" * 60)
print("PRODUCT NUMERICAL STATISTICS")
print("=" * 60)

print(
    products[
        [
            "product_name_length",
            "product_description_length",
            "product_photos_qty",
            "product_weight_g",
            "product_length_cm",
            "product_height_cm",
            "product_width_cm"
        ]
    ].describe()
)
# ---------------------------------------
# 4.6 Order item statistics
# ---------------------------------------

print("\n" + "=" * 60)
print("ORDER ITEM STATISTICS")
print("=" * 60)

print(
    order_items[
        [
            "price",
            "freight_value"
        ]
    ].describe()
)
# ---------------------------------------
# 4.7 Payment data quality
# ---------------------------------------

print("\n" + "=" * 60)
print("PAYMENT TYPES")
print("=" * 60)

print(payments["payment_type"].value_counts())


print("\n" + "=" * 60)
print("PAYMENT INSTALLMENTS")
print("=" * 60)

print(payments["payment_installments"].describe())

# ---------------------------------------
# 4.8 Review scores
# ---------------------------------------

print("\n" + "=" * 60)
print("REVIEW SCORE DISTRIBUTION")
print("=" * 60)

print(
    reviews["review_score"]
    .value_counts()
    .sort_index()
)

print("\nReview score statistics:")
print(reviews["review_score"].describe())


# ============================================================
# PHASE 2 — BUILD ANALYTICAL DATASET
# ============================================================

print("\n" + "=" * 60)
print("BUILDING ANALYTICAL DATASET")
print("=" * 60)

# Merge orders with order items
analysis_df = orders.merge(
    order_items,
    on="order_id",
    how="inner"
)

# Merge product information
analysis_df = analysis_df.merge(
    products,
    on="product_id",
    how="left"
)

# Merge category translation
analysis_df = analysis_df.merge(
    category_translation,
    on="product_category_name",
    how="left"
)

# Merge customer information
analysis_df = analysis_df.merge(
    customers,
    on="customer_id",
    how="left"
)

# Merge seller information
analysis_df = analysis_df.merge(
    sellers,
    on="seller_id",
    how="left"
)

# Merge payment information
analysis_df = analysis_df.merge(
    payments,
    on="order_id",
    how="left"
)

# Merge reviews
analysis_df = analysis_df.merge(
    reviews,
    on="order_id",
    how="left"
)

print("\nAnalytical dataset created successfully!")

print("\nShape:")
print(analysis_df.shape)

print("\nColumns:")
print(analysis_df.columns.tolist())

print("\nFirst 5 rows:")
print(analysis_df.head())

print("\nMissing values:")
print(
    analysis_df.isnull().sum()
    .sort_values(ascending=False)
    .head(15)
)

# ============================================================
# PHASE 2 — SALES AGGREGATION
# ============================================================

print("\n" + "=" * 60)
print("SALES AGGREGATION")
print("=" * 60)

# ------------------------------------------------------------
# 1. ITEM-LEVEL SALES
# One row = one product purchased in an order
# ------------------------------------------------------------

item_sales = order_items.copy()

item_sales["total_item_value"] = (
    item_sales["price"] + item_sales["freight_value"]
)

print("\nItem-level sales:")
print("Rows:", len(item_sales))

# ------------------------------------------------------------
# 2. ORDER-LEVEL SALES
# One row = one order
# ------------------------------------------------------------

order_sales = item_sales.groupby("order_id").agg(
    product_value=("price", "sum"),
    freight_value=("freight_value", "sum"),
    total_order_value=("total_item_value", "sum"),
    item_count=("order_item_id", "count")
).reset_index()

print("\nOrder-level sales:")
print("Rows:", len(order_sales))

# ------------------------------------------------------------
# 3. OVERALL SALES METRICS
# ------------------------------------------------------------

total_revenue = order_sales["product_value"].sum()
total_freight = order_sales["freight_value"].sum()
total_order_value = order_sales["total_order_value"].sum()

total_orders = order_sales["order_id"].nunique()
total_items = len(item_sales)

average_order_value = total_revenue / total_orders
average_item_price = item_sales["price"].mean()

print("\n" + "-" * 60)
print("OVERALL SALES METRICS")
print("-" * 60)

print(f"Total Orders          : {total_orders:,}")
print(f"Total Items Sold      : {total_items:,}")
print(f"Product Revenue       : {total_revenue:,.2f}")
print(f"Total Freight         : {total_freight:,.2f}")
print(f"Revenue + Freight     : {total_order_value:,.2f}")
print(f"Average Order Value   : {average_order_value:,.2f}")
print(f"Average Item Price    : {average_item_price:,.2f}")

# ------------------------------------------------------------
# 4. VALIDATION
# ------------------------------------------------------------

print("\n" + "-" * 60)
print("VALIDATION")
print("-" * 60)

print("Expected orders      : 99,441")
print("Calculated orders    :", total_orders)

print("Expected items       : 112,650")
print("Calculated items     :", total_items)

print("\nSales aggregation completed successfully.")


# ------------------------------------------------------------
# ORDER VALIDATION - ORDERS WITHOUT ORDER ITEMS
# ------------------------------------------------------------

orders_with_items = order_items["order_id"].nunique()

orders_without_items = orders[
    ~orders["order_id"].isin(order_items["order_id"])
]

print("\n------------------------------------------------------------")
print("ORDER VALIDATION")
print("------------------------------------------------------------")
print(f"Total orders in orders table       : {orders['order_id'].nunique()}")
print(f"Orders with order items             : {orders_with_items}")
print(f"Orders without order items          : {len(orders_without_items)}")

print("\nOrder status of orders without items:")
print(orders_without_items["order_status"].value_counts())

print("\nSample orders without items:")
print(orders_without_items.head(10))

# ------------------------------------------------------------
# MONTHLY SALES ANALYSIS
# ------------------------------------------------------------

order_items["order_purchase_timestamp"] = pd.to_datetime(
    orders.set_index("order_id")
    .loc[order_items["order_id"], "order_purchase_timestamp"]
).values

order_items["month"] = (
    order_items["order_purchase_timestamp"]
    .dt.to_period("M")
    .astype(str)
)

monthly_sales = (
    order_items
    .groupby("month")
    .agg(
        orders=("order_id", "nunique"),
        items_sold=("order_item_id", "count"),
        product_revenue=("price", "sum"),
        freight=("freight_value", "sum")
    )
    .reset_index()
)

monthly_sales["total_revenue"] = (
    monthly_sales["product_revenue"]
    + monthly_sales["freight"]
)

monthly_sales["average_order_value"] = (
    monthly_sales["total_revenue"]
    / monthly_sales["orders"]
)

print("\n------------------------------------------------------------")
print("MONTHLY SALES ANALYSIS")
print("------------------------------------------------------------")

print(monthly_sales.to_string(index=False))

print("\n------------------------------------------------------------")
print("TOP 5 MONTHS BY REVENUE")
print("------------------------------------------------------------")

print(
    monthly_sales
    .sort_values("total_revenue", ascending=False)
    .head(5)
    .to_string(index=False)
)

print("\n------------------------------------------------------------")
print("BOTTOM 5 MONTHS BY REVENUE")
print("------------------------------------------------------------")

print(
    monthly_sales
    .sort_values("total_revenue")
    .head(5)
    .to_string(index=False)
)

# ============================================================
# MONTHLY REVENUE VISUALIZATION
# ============================================================

plt.figure(figsize=(12, 6))

plt.plot(
    monthly_sales["month"],
    monthly_sales["total_revenue"],
    marker="o"
)

plt.title("Monthly Revenue Trend")
plt.xlabel("Month")
plt.ylabel("Total Revenue")

plt.xticks(rotation=45)
plt.grid(True, alpha=0.3)

plt.tight_layout()
plt.show()
# ============================================================
# MONTHLY ORDERS VISUALIZATION
# ============================================================

plt.figure(figsize=(12, 6))

plt.plot(
    monthly_sales["month"],
    monthly_sales["orders"],
    marker="o"
)

plt.title("Monthly Order Volume")
plt.xlabel("Month")
plt.ylabel("Number of Orders")

plt.xticks(rotation=45)
plt.grid(True, alpha=0.3)

plt.tight_layout()
plt.show()

# 

# ------------------------------------------------------------
# PRODUCT CATEGORY ANALYSIS
# ------------------------------------------------------------

print("\n============================================================")
print("PRODUCT CATEGORY ANALYSIS")
print("============================================================")

# Merge order items with products
category_sales = order_items.merge(
    products[["product_id", "product_category_name"]],
    on="product_id",
    how="left"
)

# Merge English category names
category_sales = category_sales.merge(
    category_translation,
    on="product_category_name",
    how="left"
)

# Use English category name where available
category_sales["category"] = (
    category_sales["product_category_name_english"]
    .fillna(category_sales["product_category_name"])
)

# Aggregate category performance
category_analysis = (
    category_sales
    .groupby("category")
    .agg(
        orders=("order_id", "nunique"),
        items_sold=("order_item_id", "count"),
        product_revenue=("price", "sum"),
        freight=("freight_value", "sum")
    )
    .reset_index()
)

# Total revenue
category_analysis["total_revenue"] = (
    category_analysis["product_revenue"]
    + category_analysis["freight"]
)

# Average item price
category_analysis["average_item_price"] = (
    category_analysis["product_revenue"]
    / category_analysis["items_sold"]
)

# Average order value
category_analysis["average_order_value"] = (
    category_analysis["total_revenue"]
    / category_analysis["orders"]
)

print(
    category_analysis
    .sort_values("total_revenue", ascending=False)
    .to_string(index=False)
)


# ------------------------------------------------------------
# TOP 10 CATEGORIES BY REVENUE
# ------------------------------------------------------------

top_categories = (
    category_analysis
    .sort_values("total_revenue", ascending=False)
    .head(10)
)

print("\n------------------------------------------------------------")
print("TOP 10 CATEGORIES BY REVENUE")
print("------------------------------------------------------------")

print(
    top_categories.to_string(index=False)
)


# # ------------------------------------------------------------
# TOP 10 CATEGORIES REVENUE VISUALIZATION
# ------------------------------------------------------------

plt.figure(figsize=(12, 6))

plt.bar(
    top_categories["category"],
    top_categories["total_revenue"]
)

plt.title("Top 10 Categories by Total Revenue")
plt.xlabel("Category")
plt.ylabel("Total Revenue")

plt.xticks(
    rotation=45,
    ha="right"
)

plt.tight_layout()

# Save the chart
plt.savefig(
    "top_categories_revenue.png",
    dpi=300,
    bbox_inches="tight"
)

# Display the chart
plt.show()

print("\nCategory revenue chart completed successfully.")
print("top_categories_revenue.png")

# ------------------------------------------------------------
# TOP 10 CATEGORIES BY ITEMS SOLD
# ------------------------------------------------------------

top_categories_items = (
    category_analysis
    .sort_values("items_sold", ascending=False)
    .head(10)
)

plt.figure(figsize=(12, 6))

plt.bar(
    top_categories_items["category"],
    top_categories_items["items_sold"]
)

plt.title("Top 10 Categories by Items Sold")
plt.xlabel("Category")
plt.ylabel("Items Sold")

plt.xticks(
    rotation=45,
    ha="right"
)

plt.tight_layout()

plt.savefig(
    "top_categories_items_sold.png",
    dpi=300,
    bbox_inches="tight"
)

plt.show()

print("Category items-sold chart completed successfully.")
# ------------------------------------------------------------
# SELLER PERFORMANCE ANALYSIS
# ------------------------------------------------------------

seller_sales = order_items.merge(
    sellers[["seller_id"]],
    on="seller_id",
    how="left"
)

seller_analysis = (
    seller_sales
    .groupby("seller_id")
    .agg(
        orders=("order_id", "nunique"),
        items_sold=("order_item_id", "count"),
        product_revenue=("price", "sum"),
        freight=("freight_value", "sum")
    )
    .reset_index()
)

seller_analysis["total_revenue"] = (
    seller_analysis["product_revenue"]
    + seller_analysis["freight"]
)

seller_analysis["average_item_price"] = (
    seller_analysis["product_revenue"]
    / seller_analysis["items_sold"]
)

seller_analysis["average_order_value"] = (
    seller_analysis["total_revenue"]
    / seller_analysis["orders"]
)

print("\n------------------------------------------------------------")
print("SELLER PERFORMANCE ANALYSIS")
print("------------------------------------------------------------")

print(
    seller_analysis
    .sort_values("total_revenue", ascending=False)
    .head(20)
    .to_string(index=False)
)

print("\n------------------------------------------------------------")
print("TOP 10 SELLERS BY REVENUE")
print("------------------------------------------------------------")

print(
    seller_analysis
    .sort_values("total_revenue", ascending=False)
    .head(10)
    .to_string(index=False)
)

print("\n------------------------------------------------------------")
print("TOP 10 SELLERS BY ITEMS SOLD")
print("------------------------------------------------------------")

print(
    seller_analysis
    .sort_values("items_sold", ascending=False)
    .head(10)
    .to_string(index=False)
)

# ============================================================
# CUSTOMER ANALYSIS
# ============================================================

print("\n")
print("=" * 60)
print("CUSTOMER ANALYSIS")
print("=" * 60)

customer_analysis = pd.read_sql("""
    SELECT
        c.customer_unique_id,
        COUNT(DISTINCT o.order_id) AS orders,
        COUNT(oi.order_item_id) AS items_sold,
        ROUND(SUM(oi.price), 2) AS product_revenue,
        ROUND(SUM(oi.freight_value), 2) AS freight,
        ROUND(SUM(oi.price + oi.freight_value), 2) AS total_revenue,
        ROUND(AVG(oi.price), 2) AS average_item_price,
        ROUND(
            SUM(oi.price + oi.freight_value) /
            COUNT(DISTINCT o.order_id),
            2
        ) AS average_order_value
    FROM customers c
    JOIN orders o
        ON c.customer_id = o.customer_id
    JOIN order_items oi
        ON o.order_id = oi.order_id
    GROUP BY c.customer_unique_id
""", engine)

print("\nCUSTOMER SUMMARY")
print("-" * 60)

print(
    f"Unique purchasing customers : {customer_analysis['customer_unique_id'].nunique():,}")
print(f"Total customer orders       : {customer_analysis['orders'].sum():,}")
print(
    f"Total items purchased       : {customer_analysis['items_sold'].sum():,}")
print(
    f"Total customer revenue      : {customer_analysis['total_revenue'].sum():,.2f}")

print("\n")


# ============================================================
# TOP 10 CUSTOMERS BY REVENUE
# ============================================================

print("TOP 10 CUSTOMERS BY REVENUE")
print("-" * 60)

top_customers_revenue = customer_analysis.sort_values(
    by="total_revenue",
    ascending=False
).head(10)

print(
    top_customers_revenue.to_string(index=False)
)


# ============================================================
# TOP 10 CUSTOMERS BY ORDERS
# ============================================================

print("\n")
print("TOP 10 CUSTOMERS BY NUMBER OF ORDERS")
print("-" * 60)

top_customers_orders = customer_analysis.sort_values(
    by="orders",
    ascending=False
).head(10)

print(
    top_customers_orders.to_string(index=False)
)


# ============================================================
# REPEAT CUSTOMER ANALYSIS
# ============================================================

print("\n")
print("CUSTOMER PURCHASE FREQUENCY")
print("-" * 60)

total_customers = len(customer_analysis)

repeat_customers = (customer_analysis["orders"] > 1).sum()
one_time_customers = (customer_analysis["orders"] == 1).sum()

repeat_percentage = (repeat_customers / total_customers) * 100
one_time_percentage = (one_time_customers / total_customers) * 100

print(
    f"One-time customers : {one_time_customers:,} ({one_time_percentage:.2f}%)")
print(f"Repeat customers   : {repeat_customers:,} ({repeat_percentage:.2f}%)")


# ============================================================
# CUSTOMER REVENUE DISTRIBUTION
# ============================================================

print("\n")
print("CUSTOMER REVENUE SUMMARY")
print("-" * 60)

print(
    customer_analysis["total_revenue"].describe().to_string()
)

# ============================================================
# PAYMENT ANALYSIS
# ============================================================

print("\n")
print("=" * 60)
print("PAYMENT ANALYSIS")
print("=" * 60)

payment_analysis = pd.read_sql("""
    SELECT
        payment_type,
        COUNT(*) AS payment_transactions,
        COUNT(DISTINCT order_id) AS orders,
        ROUND(SUM(payment_value), 2) AS total_payment_value,
        ROUND(AVG(payment_value), 2) AS average_payment_value,
        ROUND(AVG(payment_installments), 2) AS average_installments,
        MAX(payment_installments) AS max_installments
    FROM payments
    GROUP BY payment_type
    ORDER BY total_payment_value DESC
""", engine)

print("\nPAYMENT METHOD PERFORMANCE")
print("-" * 60)

print(payment_analysis.to_string(index=False))


# ============================================================
# TOP PAYMENT METHODS BY TRANSACTION COUNT
# ============================================================

print("\n")
print("TOP PAYMENT METHODS BY TRANSACTION COUNT")
print("-" * 60)

top_payment_methods = payment_analysis.sort_values(
    by="payment_transactions",
    ascending=False
).head(10)

print(top_payment_methods.to_string(index=False))


# ============================================================
# INSTALLMENT ANALYSIS
# ============================================================

print("\n")
print("INSTALLMENT ANALYSIS")
print("-" * 60)

installment_analysis = pd.read_sql("""
    SELECT
        payment_installments,
        COUNT(*) AS transactions,
        ROUND(SUM(payment_value), 2) AS total_payment_value,
        ROUND(AVG(payment_value), 2) AS average_payment_value
    FROM payments
    GROUP BY payment_installments
    ORDER BY payment_installments
""", engine)

print(installment_analysis.to_string(index=False))


# ============================================================
# PAYMENT VALIDATION
# ============================================================

print("\n")
print("PAYMENT VALIDATION")
print("-" * 60)

payment_total = payment_analysis["total_payment_value"].sum()
payment_transactions = payment_analysis["payment_transactions"].sum()

print(f"Total payment transactions : {payment_transactions:,}")
print(f"Total payment value        : {payment_total:,.2f}")

# ============================================================
# REVIEW ANALYSIS
# ============================================================

print("\n")
print("=" * 60)
print("REVIEW ANALYSIS")
print("=" * 60)

review_analysis = pd.read_sql("""
    SELECT
        review_score,
        COUNT(*) AS review_count,
        ROUND(AVG(review_score), 2) AS average_score
    FROM reviews
    GROUP BY review_score
    ORDER BY review_score
""", engine)

print("\nREVIEW SCORE DISTRIBUTION")
print("-" * 60)

print(review_analysis.to_string(index=False))


# ============================================================
# OVERALL REVIEW METRICS
# ============================================================

print("\n")
print("OVERALL REVIEW METRICS")
print("-" * 60)

total_reviews = len(reviews)
average_review_score = reviews["review_score"].mean()

print(f"Total reviews       : {total_reviews:,}")
print(f"Average review score: {average_review_score:.2f}")


# ============================================================
# LOW VS HIGH RATING
# ============================================================

print("\n")
print("REVIEW QUALITY")
print("-" * 60)

low_ratings = (reviews["review_score"] <= 2).sum()
high_ratings = (reviews["review_score"] >= 4).sum()

low_rating_percentage = (low_ratings / total_reviews) * 100
high_rating_percentage = (high_ratings / total_reviews) * 100

print(
    f"Low ratings (1-2) : {low_ratings:,} "
    f"({low_rating_percentage:.2f}%)"
)

print(
    f"High ratings (4-5): {high_ratings:,} "
    f"({high_rating_percentage:.2f}%)"
)


# ============================================================
# REVIEW SCORE BY CATEGORY
# ============================================================

print("\n")
print("REVIEW SCORE BY CATEGORY")
print("-" * 60)

category_reviews = pd.read_sql("""
    SELECT
        COALESCE(ct.product_category_name_english,
                 p.product_category_name) AS category,
        COUNT(r.review_id) AS review_count,
        ROUND(AVG(r.review_score), 2) AS average_review_score
    FROM reviews r
    JOIN order_items oi
        ON r.order_id = oi.order_id
    JOIN products p
        ON oi.product_id = p.product_id
    LEFT JOIN category_translation ct
        ON p.product_category_name = ct.product_category_name
    GROUP BY category
    HAVING COUNT(r.review_id) >= 50
    ORDER BY average_review_score DESC
""", engine)

print(category_reviews.head(10).to_string(index=False))


# ============================================================
# LOWEST RATED CATEGORIES
# ============================================================

print("\n")
print("BOTTOM 10 CATEGORIES BY REVIEW SCORE")
print("-" * 60)

print(
    category_reviews
    .sort_values("average_review_score")
    .head(10)
    .to_string(index=False)
)


# ============================================================
# REVIEW VALIDATION
# ============================================================

print("\n")
print("REVIEW VALIDATION")
print("-" * 60)

print(f"Reviews table records : {len(reviews):,}")
print(
    f"Review score records  : "
    f"{review_analysis['review_count'].sum():,}"
)

# ============================================================
# SELLER PERFORMANCE ANALYSIS
# ============================================================

print("\nSELLER PERFORMANCE ANALYSIS")
print("=" * 60)

seller_performance = pd.read_sql("""
SELECT
    oi.seller_id,
    COUNT(DISTINCT oi.order_id) AS orders,
    COUNT(*) AS items_sold,
    ROUND(SUM(oi.price), 2) AS product_revenue,
    ROUND(SUM(oi.freight_value), 2) AS freight,
    ROUND(SUM(oi.price + oi.freight_value), 2) AS total_revenue,
    ROUND(AVG(oi.price), 2) AS average_item_price
FROM order_items oi
GROUP BY oi.seller_id
""", engine)

seller_performance["average_order_value"] = (
    seller_performance["total_revenue"]
    / seller_performance["orders"]
)

print("\nTOP 10 SELLERS BY TOTAL REVENUE")
print("-" * 60)

print(
    seller_performance
    .sort_values("total_revenue", ascending=False)
    .head(10)
    .to_string(index=False)
)

print("\nTOP 10 SELLERS BY NUMBER OF ITEMS SOLD")
print("-" * 60)

print(
    seller_performance
    .sort_values("items_sold", ascending=False)
    .head(10)
    .to_string(index=False)
)

print("\nTOP 10 SELLERS BY AVERAGE ITEM PRICE")
print("-" * 60)

print(
    seller_performance
    .sort_values("average_item_price", ascending=False)
    .head(10)
    .to_string(index=False)
)

print("\nSELLER PERFORMANCE SUMMARY")
print("-" * 60)

print(
    f"Total sellers              : {seller_performance['seller_id'].nunique():,}")
print(
    f"Average seller revenue     : {seller_performance['total_revenue'].mean():,.2f}")
print(
    f"Median seller revenue      : {seller_performance['total_revenue'].median():,.2f}")
print(
    f"Maximum seller revenue     : {seller_performance['total_revenue'].max():,.2f}")
print(
    f"Average items per seller   : {seller_performance['items_sold'].mean():,.2f}")

# ============================================================
# DELIVERY & LOGISTICS ANALYSIS
# ============================================================

print("\nDELIVERY & LOGISTICS ANALYSIS")
print("=" * 60)

# ------------------------------------------------------------
# DELIVERY TIME ANALYSIS
# ------------------------------------------------------------

delivery_query = """
SELECT
    order_id,
    order_status,
    order_purchase_timestamp,
    order_delivered_customer_date,
    order_estimated_delivery_date,
    DATEDIFF(
        order_delivered_customer_date,
        order_purchase_timestamp
    ) AS delivery_days,
    DATEDIFF(
        order_delivered_customer_date,
        order_estimated_delivery_date
    ) AS delivery_delay_days
FROM orders
WHERE order_delivered_customer_date IS NOT NULL
"""

delivery = pd.read_sql(delivery_query, engine)

print("\nDELIVERY SUMMARY")
print("-" * 60)

print(f"Delivered orders : {len(delivery):,}")
print(f"Average delivery time : {delivery['delivery_days'].mean():.2f} days")
print(f"Median delivery time  : {delivery['delivery_days'].median():.2f} days")
print(f"Minimum delivery time : {delivery['delivery_days'].min():.0f} days")
print(f"Maximum delivery time : {delivery['delivery_days'].max():.0f} days")


# ------------------------------------------------------------
# ON-TIME VS LATE DELIVERY
# ------------------------------------------------------------

delivery["delivery_status"] = delivery["delivery_delay_days"].apply(
    lambda x: "Late" if x > 0 else "On Time"
)

delivery_status = (
    delivery["delivery_status"]
    .value_counts()
    .rename_axis("delivery_status")
    .reset_index(name="orders")
)

delivery_status["percentage"] = (
    delivery_status["orders"] / len(delivery) * 100
)

print("\nDELIVERY PERFORMANCE")
print("-" * 60)

print(delivery_status.to_string(index=False))


# ------------------------------------------------------------
# DELIVERY DELAY SUMMARY
# ------------------------------------------------------------

print("\nDELIVERY DELAY SUMMARY")
print("-" * 60)

print(
    f"Average delay : "
    f"{delivery['delivery_delay_days'].mean():.2f} days"
)

print(
    f"Average late delivery delay : "
    f"{delivery.loc[delivery['delivery_delay_days'] > 0, 'delivery_delay_days'].mean():.2f} days"
)

print(
    f"Maximum delay : "
    f"{delivery['delivery_delay_days'].max():.0f} days"
)


# ------------------------------------------------------------
# TOP 10 WORST DELIVERY DELAYS
# ------------------------------------------------------------

worst_deliveries = (
    delivery
    .sort_values("delivery_delay_days", ascending=False)
    .head(10)
)

print("\nTOP 10 WORST DELIVERY DELAYS")
print("-" * 60)

print(
    worst_deliveries[
        [
            "order_id",
            "order_status",
            "delivery_days",
            "delivery_delay_days"
        ]
    ].to_string(index=False)
)


# ------------------------------------------------------------
# DELIVERY TIME DISTRIBUTION
# ------------------------------------------------------------

print("\nDELIVERY TIME DISTRIBUTION")
print("-" * 60)

print(delivery["delivery_days"].describe())

# ============================================================
# GEOGRAPHIC ANALYSIS
# ============================================================

print("\nGEOGRAPHIC ANALYSIS")
print("=" * 60)

# ------------------------------------------------------------
# STATE-LEVEL SALES ANALYSIS
# ------------------------------------------------------------

geo_query = """
SELECT
    c.customer_state,
    COUNT(DISTINCT o.order_id) AS orders,
    COUNT(oi.order_item_id) AS items_sold,
    ROUND(SUM(oi.price), 2) AS product_revenue,
    ROUND(SUM(oi.freight_value), 2) AS freight,
    ROUND(SUM(oi.price + oi.freight_value), 2) AS total_revenue,
    ROUND(AVG(oi.price), 2) AS average_item_price
FROM orders o
JOIN customers c
    ON o.customer_id = c.customer_id
JOIN order_items oi
    ON o.order_id = oi.order_id
GROUP BY c.customer_state
ORDER BY total_revenue DESC
"""

geo = pd.read_sql(geo_query, engine)

print("\nSTATE PERFORMANCE BY REVENUE")
print("-" * 60)

print(
    geo.head(10).to_string(index=False)
)


# ------------------------------------------------------------
# TOP 10 STATES BY NUMBER OF ORDERS
# ------------------------------------------------------------

print("\nTOP 10 STATES BY ORDERS")
print("-" * 60)

print(
    geo.sort_values(
        "orders",
        ascending=False
    ).head(10).to_string(index=False)
)


# ------------------------------------------------------------
# TOP 10 STATES BY REVENUE
# ------------------------------------------------------------

print("\nTOP 10 STATES BY TOTAL REVENUE")
print("-" * 60)

print(
    geo.sort_values(
        "total_revenue",
        ascending=False
    ).head(10).to_string(index=False)
)


# ------------------------------------------------------------
# AVERAGE ORDER VALUE BY STATE
# ------------------------------------------------------------

geo["average_order_value"] = (
    geo["total_revenue"] / geo["orders"]
)

print("\nTOP 10 STATES BY AVERAGE ORDER VALUE")
print("-" * 60)

print(
    geo.sort_values(
        "average_order_value",
        ascending=False
    )
    .head(10)
    .to_string(index=False)
)


# ------------------------------------------------------------
# DELIVERY PERFORMANCE BY STATE
# ------------------------------------------------------------

delivery_geo_query = """
SELECT
    c.customer_state,
    COUNT(DISTINCT o.order_id) AS delivered_orders,

    ROUND(
        AVG(
            DATEDIFF(
                o.order_delivered_customer_date,
                o.order_purchase_timestamp
            )
        ),
        2
    ) AS average_delivery_days,

    ROUND(
        AVG(
            CASE
                WHEN o.order_delivered_customer_date
                     <= o.order_estimated_delivery_date
                THEN 1
                ELSE 0
            END
        ) * 100,
        2
    ) AS on_time_percentage

FROM orders o

JOIN customers c
    ON o.customer_id = c.customer_id

WHERE o.order_delivered_customer_date IS NOT NULL

GROUP BY c.customer_state
"""

delivery_geo = pd.read_sql(
    delivery_geo_query,
    engine
)


# ------------------------------------------------------------
# BEST STATES FOR DELIVERY
# ------------------------------------------------------------

print("\nBEST 10 STATES BY ON-TIME DELIVERY")
print("-" * 60)

print(
    delivery_geo
    .sort_values(
        "on_time_percentage",
        ascending=False
    )
    .head(10)
    .to_string(index=False)
)


# ------------------------------------------------------------
# WORST STATES FOR DELIVERY
# ------------------------------------------------------------

print("\nWORST 10 STATES BY ON-TIME DELIVERY")
print("-" * 60)

print(
    delivery_geo
    .sort_values(
        "on_time_percentage",
        ascending=True
    )
    .head(10)
    .to_string(index=False)
)


# ------------------------------------------------------------
# STATE-LEVEL SUMMARY
# ------------------------------------------------------------

print("\nGEOGRAPHIC SUMMARY")
print("-" * 60)

print(
    f"Number of states : {geo['customer_state'].nunique()}"
)

print(
    f"Highest revenue state : "
    f"{geo.iloc[0]['customer_state']}"
)

print(
    f"Highest revenue : "
    f"{geo.iloc[0]['total_revenue']:,.2f}"
)

print(
    f"Highest order volume state : "
    f"{geo.sort_values('orders', ascending=False).iloc[0]['customer_state']}"
)

print(
    f"Highest order volume : "
    f"{geo['orders'].max():,}"
)

print(
    f"Highest average order value state : "
    f"{geo.sort_values('average_order_value', ascending=False).iloc[0]['customer_state']}"
)

print(
    f"Highest average order value : "
    f"{geo['average_order_value'].max():,.2f}"
)


# ============================================================
# FINAL BUSINESS KPI SUMMARY
# ============================================================

print("\n")
print("=" * 70)
print("                 FINAL BUSINESS KPI SUMMARY")
print("=" * 70)

# ------------------------------------------------------------
# CORE SALES KPIs
# ------------------------------------------------------------

total_orders = order_items["order_id"].nunique()
total_items = len(order_items)

product_revenue = order_items["price"].sum()
total_freight = order_items["freight_value"].sum()
total_revenue = product_revenue + total_freight

average_order_value = total_revenue / total_orders
average_item_price = product_revenue / total_items

# ------------------------------------------------------------
# CUSTOMER KPIs
# ------------------------------------------------------------

unique_customers = customer_analysis["customer_unique_id"].nunique()

repeat_customers = (
    customer_analysis["orders"] > 1
).sum()

repeat_customer_percentage = (
    repeat_customers / unique_customers * 100
)

# ------------------------------------------------------------
# DELIVERY KPIs
# ------------------------------------------------------------

# Keep only orders that were actually delivered
delivered_data = orders[
    orders["order_delivered_customer_date"].notna()
].copy()

# Calculate delivery time in days
delivered_data["delivery_days"] = (
    delivered_data["order_delivered_customer_date"]
    - delivered_data["order_purchase_timestamp"]
).dt.days

delivered_orders = len(delivered_data)

# Calculate delivery delay
delivered_data["delivery_delay_days"] = (
    delivered_data["order_delivered_customer_date"]
    - delivered_data["order_estimated_delivery_date"]
).dt.days

# On-time orders
on_time_orders = (
    delivered_data["delivery_delay_days"] <= 0
).sum()

# On-time percentage
on_time_percentage = (
    on_time_orders / delivered_orders * 100
)

# Average delivery time
average_delivery_days = (
    delivered_data["delivery_days"].mean()
)
# ------------------------------------------------------------
# REVIEW KPIs
# ------------------------------------------------------------

total_reviews = len(reviews)
average_review_score = reviews["review_score"].mean()

high_rating_percentage = (
    (reviews["review_score"] >= 4).sum()
    / total_reviews * 100
)

# ------------------------------------------------------------
# SELLER KPIs
# ------------------------------------------------------------

total_sellers = sellers["seller_id"].nunique()

# ------------------------------------------------------------
# TOP CATEGORY
# ------------------------------------------------------------

top_category_row = (
    category_analysis
    .sort_values("total_revenue", ascending=False)
    .iloc[0]
)

top_category = top_category_row["category"]
top_category_revenue = top_category_row["total_revenue"]

# ------------------------------------------------------------
# TOP REVENUE STATE
# ------------------------------------------------------------

state_sales = order_items.merge(
    orders[["order_id", "customer_id"]],
    on="order_id",
    how="left"
)

state_sales = state_sales.merge(
    customers[["customer_id", "customer_state"]],
    on="customer_id",
    how="left"
)

state_analysis_kpi = (
    state_sales
    .groupby("customer_state")
    .agg(
        orders=("order_id", "nunique"),
        items_sold=("order_item_id", "count"),
        product_revenue=("price", "sum"),
        freight=("freight_value", "sum")
    )
    .reset_index()
)

state_analysis_kpi["total_revenue"] = (
    state_analysis_kpi["product_revenue"]
    + state_analysis_kpi["freight"]
)

top_state_row = (
    state_analysis_kpi
    .sort_values("total_revenue", ascending=False)
    .iloc[0]
)

top_state = top_state_row["customer_state"]
top_state_revenue = top_state_row["total_revenue"]
# ------------------------------------------------------------
# TOP PAYMENT METHOD
# ------------------------------------------------------------

top_payment_row = (
    payment_analysis
    .sort_values("payment_transactions", ascending=False)
    .iloc[0]
)

top_payment_method = top_payment_row["payment_type"]

# ------------------------------------------------------------
# DISPLAY FINAL KPIs
# ------------------------------------------------------------

print("\nSALES")
print("-" * 70)
print(f"Total Orders              : {total_orders:,}")
print(f"Total Items Sold          : {total_items:,}")
print(f"Product Revenue           : {product_revenue:,.2f}")
print(f"Total Freight             : {total_freight:,.2f}")
print(f"Total Revenue             : {total_revenue:,.2f}")
print(f"Average Order Value       : {average_order_value:,.2f}")
print(f"Average Item Price        : {average_item_price:,.2f}")

print("\nCUSTOMERS")
print("-" * 70)
print(f"Unique Customers          : {unique_customers:,}")
print(f"Repeat Customers          : {repeat_customers:,}")
print(f"Repeat Customer %         : {repeat_customer_percentage:.2f}%")

print("\nDELIVERY")
print("-" * 70)
print(f"Delivered Orders          : {delivered_orders:,}")
print(f"On-Time Delivery %        : {on_time_percentage:.2f}%")
print(f"Average Delivery Time     : {average_delivery_days:.2f} days")

print("\nREVIEWS")
print("-" * 70)
print(f"Total Reviews             : {total_reviews:,}")
print(f"Average Review Score      : {average_review_score:.2f}")
print(f"High Rating % (4-5)       : {high_rating_percentage:.2f}%")

print("\nSELLERS")
print("-" * 70)
print(f"Total Sellers             : {total_sellers:,}")

print("\nTOP PERFORMERS")
print("-" * 70)
print(f"Top Revenue Category      : {top_category}")
print(f"Category Revenue          : {top_category_revenue:,.2f}")
print(f"Top Revenue State         : {top_state}")
print(f"State Revenue             : {top_state_revenue:,.2f}")
print(f"Top Payment Method        : {top_payment_method}")

print("\n" + "=" * 70)
print("             FINAL KPI SUMMARY COMPLETED")
print("=" * 70)

print("\nMySQL connection closed.")
