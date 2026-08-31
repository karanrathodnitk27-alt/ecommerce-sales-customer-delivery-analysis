print("Orders with missing customer_id:", orders['customer_id'].isna().sum())
print("Order items with missing product_id:", order_items['product_id'].isna().sum())
print("Order items with missing seller_id:", order_items['seller_id'].isna().sum())
print("Payments with missing order_id:", payments['order_id'].isna().sum())
