CREATE DATABASE retail_bi;

USE retail_bi;

SHOW TABLES;

CREATE TABLE customers (
    customer_id VARCHAR(50) PRIMARY KEY,
    customer_unique_id VARCHAR(50) NOT NULL,
    customer_zip_code_prefix INT,
    customer_city VARCHAR(100),
    customer_state CHAR(2)
);

CREATE TABLE products (
    product_id VARCHAR(50) PRIMARY KEY,
    product_category_name VARCHAR(100),
    product_name_length INT,
    product_description_length INT,
    product_photos_qty INT,
    product_weight_g DECIMAL(10,2),
    product_length_cm DECIMAL(10,2),
    product_height_cm DECIMAL(10,2),
    product_width_cm DECIMAL(10,2)
);

CREATE TABLE sellers (
    seller_id VARCHAR(50) PRIMARY KEY,
    seller_zip_code_prefix INT,
    seller_city VARCHAR(100),
    seller_state CHAR(2)
);

CREATE TABLE orders (
    order_id VARCHAR(50) PRIMARY KEY,
    customer_id VARCHAR(50) NOT NULL,
    order_status VARCHAR(30),
    order_purchase_timestamp DATETIME,
    order_approved_at DATETIME,
    order_delivered_carrier_date DATETIME,
    order_delivered_customer_date DATETIME,
    order_estimated_delivery_date DATETIME,
    CONSTRAINT fk_orders_customer
        FOREIGN KEY (customer_id)
        REFERENCES customers(customer_id)
);

CREATE TABLE order_items (
    order_id VARCHAR(50) NOT NULL,
    order_item_id INT NOT NULL,
    product_id VARCHAR(50) NOT NULL,
    seller_id VARCHAR(50) NOT NULL,
    shipping_limit_date DATETIME,
    price DECIMAL(10,2),
    freight_value DECIMAL(10,2),

    PRIMARY KEY (order_id, order_item_id),

    CONSTRAINT fk_items_order
        FOREIGN KEY (order_id)
        REFERENCES orders(order_id),

    CONSTRAINT fk_items_product
        FOREIGN KEY (product_id)
        REFERENCES products(product_id),

    CONSTRAINT fk_items_seller
        FOREIGN KEY (seller_id)
        REFERENCES sellers(seller_id)
);

CREATE TABLE payments (
    order_id VARCHAR(50) NOT NULL,
    payment_sequential INT NOT NULL,
    payment_type VARCHAR(30),
    payment_installments INT,
    payment_value DECIMAL(10,2),

    PRIMARY KEY (order_id, payment_sequential),

    CONSTRAINT fk_payments_order
        FOREIGN KEY (order_id)
        REFERENCES orders(order_id)
);

CREATE TABLE reviews (
    review_id VARCHAR(50) NOT NULL,
    order_id VARCHAR(50) NOT NULL,
    review_score INT,
    review_comment_title TEXT,
    review_comment_message TEXT,
    review_creation_date DATETIME,
    review_answer_timestamp DATETIME,

    PRIMARY KEY (review_id),

    CONSTRAINT fk_reviews_order
        FOREIGN KEY (order_id)
        REFERENCES orders(order_id)
);

## previously we assumed only reviewid as primary key but later got to know that it has dublicates so need to alter the table. 
USE retail_bi;

ALTER TABLE reviews
DROP PRIMARY KEY,
ADD PRIMARY KEY (review_id, order_id);

CREATE TABLE category_translation (
    product_category_name VARCHAR(100) PRIMARY KEY,
    product_category_name_english VARCHAR(100)
);


## getting error while loading
SHOW VARIABLES LIKE 'local_infile';
SET GLOBAL local_infile = 1;

##
USE retail_bi;

LOAD DATA LOCAL INFILE
'C:/Users/karan/Desktop/Retail-Business-Intelligance/Dataset/olist_customers_dataset.csv'
INTO TABLE customers
FIELDS TERMINATED BY ','
ENCLOSED BY '"'
LINES TERMINATED BY '\n'
IGNORE 1 ROWS
(customer_id,
 customer_unique_id,
 customer_zip_code_prefix,
 customer_city,
 customer_state);
 
 SELECT COUNT(*) AS customer_count
FROM customers;

SELECT DATABASE();

SHOW TABLES;

SELECT COUNT(*) AS customer_count FROM customers;

SELECT COUNT(*) AS total_rows,
       COUNT(DISTINCT customer_id) AS unique_customers
FROM customers;


TRUNCATE TABLE customers;  
## this did not work becouse our foriegn keys are assosiated with otehr tables also so we used delete method to just clear the partial data which was loaded

SELECT COUNT(*) AS order_count
FROM orders;

DELETE FROM customers;

USE retail_bi;
SELECT COUNT(*) AS customer_count
FROM customers;

SELECT USER(), CURRENT_USER();
SELECT user, host, plugin
FROM mysql.user
WHERE user = 'root';


USE retail_bi;

SELECT COUNT(*) AS product_count
FROM products;

SELECT COUNT(*) AS seller_count
FROM retail_bi.sellers;

USE retail_bi;
SELECT COUNT(*) AS order_count
FROM orders;

SELECT COUNT(*) AS order_item_count
FROM retail_bi.order_items;

SELECT COUNT(*) AS payment_count
FROM retail_bi.payments;

SELECT COUNT(*) AS review_count
FROM retail_bi.reviews;

USE retail_bi;
DELETE FROM orders;

SHOW CREATE TABLE reviews;  ## to check whether the table is craeted or not

SELECT COUNT(*) AS review_count
FROM retail_bi.reviews;

SELECT COUNT(*) AS category_count
FROM retail_bi.category_translation;

## to verify that imported data matches the source data exactly.
USE retail_bi;
SELECT 'customers' AS table_name, COUNT(*) AS row_count FROM customers
UNION ALL
SELECT 'orders', COUNT(*) FROM orders
UNION ALL
SELECT 'order_items', COUNT(*) FROM order_items
UNION ALL
SELECT 'payments', COUNT(*) FROM payments
UNION ALL
SELECT 'reviews', COUNT(*) FROM reviews
UNION ALL
SELECT 'products', COUNT(*) FROM products
UNION ALL
SELECT 'sellers', COUNT(*) FROM sellers
UNION ALL
SELECT 'category_translation', COUNT(*) FROM category_translation;

## to check the reliability of data---Does every transaction actually point to a valid customer/product/seller/order?
## referential-integrity checks
##Orders without customers
SELECT COUNT(*) AS orphan_orders
FROM orders o
LEFT JOIN customers c
    ON o.customer_id = c.customer_id
WHERE c.customer_id IS NULL;

#Order items without products
SELECT COUNT(*) AS orphan_order_items
FROM order_items oi
LEFT JOIN products p
    ON oi.product_id = p.product_id
WHERE p.product_id IS NULL;

#Order items without sellers
SELECT COUNT(*) AS orphan_order_items
FROM order_items oi
LEFT JOIN sellers s
    ON oi.seller_id = s.seller_id
WHERE s.seller_id IS NULL;

#Reviews without orders
SELECT COUNT(*) AS orphan_reviews
FROM reviews r
LEFT JOIN orders o
    ON r.order_id = o.order_id
WHERE o.order_id IS NULL;


##Calculate KPIs: Revenue
SELECT
    ROUND(SUM(payment_value), 2) AS total_revenue
FROM payments;

SELECT
    ROUND(AVG(payment_value), 2) AS average_payment_value
FROM payments;

SELECT
    COUNT(DISTINCT order_id) AS paid_orders
FROM payments;


## start fron step 42
SELECT
    DATE_FORMAT(o.order_purchase_timestamp, '%Y-%m') AS month,
    ROUND(SUM(oi.price), 2) AS sales_value,
    COUNT(DISTINCT o.order_id) AS orders
FROM orders o
JOIN order_items oi
    ON o.order_id = oi.order_id
WHERE o.order_status = 'delivered'
GROUP BY DATE_FORMAT(o.order_purchase_timestamp, '%Y-%m')
ORDER BY month;

#Why did sales increase?
SELECT
    DATE_FORMAT(o.order_purchase_timestamp, '%Y-%m') AS month,
    COUNT(DISTINCT o.order_id) AS orders,
    ROUND(SUM(oi.price), 2) AS sales_value,
    ROUND(
        SUM(oi.price) / COUNT(DISTINCT o.order_id),
        2
    ) AS average_order_value
FROM orders o
JOIN order_items oi
    ON o.order_id = oi.order_id
WHERE o.order_status = 'delivered'
GROUP BY DATE_FORMAT(o.order_purchase_timestamp, '%Y-%m')
ORDER BY month;

SELECT
    DATE_FORMAT(o.order_purchase_timestamp, '%Y-%m') AS month,
    COUNT(DISTINCT o.order_id) AS orders,
    ROUND(SUM(oi.price), 2) AS sales_value,
    ROUND(
        SUM(oi.price) / COUNT(DISTINCT o.order_id),
        2
    ) AS average_order_value
FROM orders o
JOIN order_items oi
    ON o.order_id = oi.order_id
WHERE o.order_status = 'delivered'
GROUP BY DATE_FORMAT(o.order_purchase_timestamp, '%Y-%m')
ORDER BY month;

## top 10 product categories
SELECT
    COALESCE(
        ct.product_category_name_english,
        p.product_category_name,
        'Unknown'
    ) AS category,
    COUNT(DISTINCT oi.order_id) AS orders,
    ROUND(SUM(oi.price), 2) AS sales_value
FROM order_items oi
JOIN orders o
    ON oi.order_id = o.order_id
JOIN products p
    ON oi.product_id = p.product_id
LEFT JOIN category_translation ct
    ON p.product_category_name = ct.product_category_name
WHERE o.order_status = 'delivered'
GROUP BY
    COALESCE(
        ct.product_category_name_english,
        p.product_category_name,
        'Unknown'
    )
ORDER BY sales_value DESC
LIMIT 10;    ##the category with the most orders isn't the category generating the most sales.This tells us order volume alone doesn't explain category performance.


##Which categories generate high sales because of volume, and which generate high sales because customers spend more per order?
SELECT
    COALESCE(
        ct.product_category_name_english,
        p.product_category_name,
        'Unknown'
    ) AS category,
    COUNT(DISTINCT oi.order_id) AS orders,
    ROUND(SUM(oi.price), 2) AS sales_value,
    ROUND(
        SUM(oi.price) / COUNT(DISTINCT oi.order_id),
        2
    ) AS average_order_value
FROM order_items oi
JOIN orders o
    ON oi.order_id = o.order_id
JOIN products p
    ON oi.product_id = p.product_id
LEFT JOIN category_translation ct
    ON p.product_category_name = ct.product_category_name
WHERE o.order_status = 'delivered'
GROUP BY
    COALESCE(
        ct.product_category_name_english,
        p.product_category_name,
        'Unknown'
    )
ORDER BY sales_value DESC
LIMIT 10;  
##High-volume categories → Bed/Bath/Table, Health & Beauty, Sports & Leisure
##High-value-per-order categories→ Watches & Gifts, Cool Stuff, Auto

WITH category_sales AS (
    SELECT
        COALESCE(
            ct.product_category_name_english,
            p.product_category_name,
            'Unknown'
        ) AS category,
        SUM(oi.price) AS sales_value
    FROM order_items oi
    JOIN orders o
        ON oi.order_id = o.order_id
    JOIN products p
        ON oi.product_id = p.product_id
    LEFT JOIN category_translation ct
        ON p.product_category_name = ct.product_category_name
    WHERE o.order_status = 'delivered'
    GROUP BY
        COALESCE(
            ct.product_category_name_english,
            p.product_category_name,
            'Unknown'
        )
)

SELECT
    category,
    ROUND(sales_value, 2) AS sales_value,
    ROUND(
        sales_value / SUM(sales_value) OVER () * 100,
        2
    ) AS sales_contribution_pct
FROM category_sales
ORDER BY sales_value DESC;  ##Sales are fairly diversified across several major categories.

#Why do 1.29% of sales have no usable product category?
SELECT
    p.product_category_name,
    COUNT(*) AS item_count,
    ROUND(SUM(oi.price), 2) AS sales_value
FROM order_items oi
JOIN orders o
    ON oi.order_id = o.order_id
JOIN products p
    ON oi.product_id = p.product_id
LEFT JOIN category_translation ct
    ON p.product_category_name = ct.product_category_name
WHERE o.order_status = 'delivered'
  AND ct.product_category_name_english IS NULL
GROUP BY p.product_category_name
ORDER BY sales_value DESC;

## to check the custmor frequency
WITH customer_orders AS (
    SELECT
        c.customer_unique_id,
        COUNT(DISTINCT o.order_id) AS order_count
    FROM customers c
    JOIN orders o
        ON c.customer_id = o.customer_id
    WHERE o.order_status = 'delivered'
    GROUP BY c.customer_unique_id
)

SELECT
    CASE
        WHEN order_count = 1 THEN 'One-time'
        ELSE 'Repeat'
    END AS customer_type,
    COUNT(*) AS customers,
    ROUND(
        COUNT(*) * 100.0 / SUM(COUNT(*)) OVER (),
        2
    ) AS customer_percentage
FROM customer_orders
GROUP BY
    CASE
        WHEN order_count = 1 THEN 'One-time'
        ELSE 'Repeat'
    END
ORDER BY customers DESC;  ##97% purchased only once, while only 3% made repeat purchases.

WITH customer_orders AS (
    SELECT
        c.customer_unique_id,
        COUNT(DISTINCT o.order_id) AS order_count
    FROM customers c
    JOIN orders o
        ON c.customer_id = o.customer_id
    WHERE o.order_status = 'delivered'
    GROUP BY c.customer_unique_id
),

customer_type AS (
    SELECT
        customer_unique_id,
        CASE
            WHEN order_count = 1 THEN 'One-time'
            ELSE 'Repeat'
        END AS customer_type
    FROM customer_orders
),

customer_sales AS (
    SELECT
        c.customer_unique_id,
        SUM(oi.price) AS sales_value
    FROM customers c
    JOIN orders o
        ON c.customer_id = o.customer_id
    JOIN order_items oi
        ON o.order_id = oi.order_id
    WHERE o.order_status = 'delivered'
    GROUP BY c.customer_unique_id
)

SELECT
    ct.customer_type,
    COUNT(*) AS customers,
    ROUND(SUM(cs.sales_value), 2) AS total_sales,
    ROUND(
        SUM(cs.sales_value) / COUNT(*),
        2
    ) AS sales_per_customer
FROM customer_type ct
JOIN customer_sales cs
    ON ct.customer_unique_id = cs.customer_unique_id
GROUP BY ct.customer_type
ORDER BY total_sales DESC;  ##The repeat-customer segment is small but significantly more valuable on a per-customer basis.

##"Increasing repeat-purchase penetration could potentially create meaningful incremental revenue because repeat customers have substantially higher customer value."

##Does delivery performance relate to customer satisfaction?
SELECT
    ROUND(
        AVG(
            DATEDIFF(
                DATE(o.order_delivered_customer_date),
                DATE(o.order_purchase_timestamp)
            )
        ),
        2
    ) AS avg_delivery_days,

    MIN(
        DATEDIFF(
            DATE(o.order_delivered_customer_date),
            DATE(o.order_purchase_timestamp)
        )
    ) AS min_delivery_days,

    MAX(
        DATEDIFF(
            DATE(o.order_delivered_customer_date),
            DATE(o.order_purchase_timestamp)
        )
    ) AS max_delivery_days
FROM orders o
WHERE o.order_status = 'delivered'
  AND o.order_delivered_customer_date IS NOT NULL;
  
  ##Do longer delivery times correspond to lower customer review scores?
  SELECT
    CASE
        WHEN DATEDIFF(
            DATE(o.order_delivered_customer_date),
            DATE(o.order_purchase_timestamp)
        ) <= 7 THEN '0-7 days'

        WHEN DATEDIFF(
            DATE(o.order_delivered_customer_date),
            DATE(o.order_purchase_timestamp)
        ) <= 14 THEN '8-14 days'

        WHEN DATEDIFF(
            DATE(o.order_delivered_customer_date),
            DATE(o.order_purchase_timestamp)
        ) <= 30 THEN '15-30 days'

        ELSE '31+ days'
    END AS delivery_band,

    COUNT(DISTINCT o.order_id) AS orders,

    ROUND(AVG(r.review_score), 2) AS average_review_score

FROM orders o

JOIN reviews r
    ON o.order_id = r.order_id

WHERE o.order_status = 'delivered'
  AND o.order_delivered_customer_date IS NOT NULL

GROUP BY
    CASE
        WHEN DATEDIFF(
            DATE(o.order_delivered_customer_date),
            DATE(o.order_purchase_timestamp)
        ) <= 7 THEN '0-7 days'

        WHEN DATEDIFF(
            DATE(o.order_delivered_customer_date),
            DATE(o.order_purchase_timestamp)
        ) <= 14 THEN '8-14 days'

        WHEN DATEDIFF(
            DATE(o.order_delivered_customer_date),
            DATE(o.order_purchase_timestamp)
        ) <= 30 THEN '15-30 days'

        ELSE '31+ days'
    END

ORDER BY
    MIN(
        DATEDIFF(
            DATE(o.order_delivered_customer_date),
            DATE(o.order_purchase_timestamp)
        )
    );  ##Very long delivery times affect a relatively small share of orders, but those orders are associated with dramatically lower customer satisfaction.
    
    ##Which sellers are responsible for the longest delivery times?
    SELECT
    s.seller_id,
    s.seller_city,
    s.seller_state,

    COUNT(DISTINCT o.order_id) AS delivered_orders,

    ROUND(
        AVG(
            DATEDIFF(
                DATE(o.order_delivered_customer_date),
                DATE(o.order_purchase_timestamp)
            )
        ),
        2
    ) AS avg_delivery_days,

    ROUND(
        AVG(r.review_score),
        2
    ) AS avg_review_score

FROM sellers s

JOIN order_items oi
    ON s.seller_id = oi.seller_id

JOIN orders o
    ON oi.order_id = o.order_id

LEFT JOIN reviews r
    ON o.order_id = r.order_id

WHERE o.order_status = 'delivered'
  AND o.order_delivered_customer_date IS NOT NULL

GROUP BY
    s.seller_id,
    s.seller_city,
    s.seller_state

HAVING COUNT(DISTINCT o.order_id) >= 50

ORDER BY avg_delivery_days DESC

LIMIT 10; ##Slow delivery does not automatically mean poor reviews for every seller.

##Which sellers are commercially important but operationally underperforming?
SELECT
    s.seller_id,
    s.seller_city,
    s.seller_state,

    COUNT(DISTINCT o.order_id) AS delivered_orders,

    ROUND(SUM(oi.price), 2) AS sales_value,

    ROUND(
        SUM(oi.price) / COUNT(DISTINCT o.order_id),
        2
    ) AS sales_per_order,

    ROUND(
        AVG(
            DATEDIFF(
                DATE(o.order_delivered_customer_date),
                DATE(o.order_purchase_timestamp)
            )
        ),
        2
    ) AS avg_delivery_days,

    ROUND(
        AVG(r.review_score),
        2
    ) AS avg_review_score

FROM sellers s

JOIN order_items oi
    ON s.seller_id = oi.seller_id

JOIN orders o
    ON oi.order_id = o.order_id

LEFT JOIN reviews r
    ON o.order_id = r.order_id

WHERE o.order_status = 'delivered'
  AND o.order_delivered_customer_date IS NOT NULL

GROUP BY
    s.seller_id,
    s.seller_city,
    s.seller_state

HAVING COUNT(DISTINCT o.order_id) >= 100

ORDER BY sales_value DESC

LIMIT 15;


## payment analysis
SELECT
    payment_type,
    COUNT(DISTINCT order_id) AS orders,
    ROUND(SUM(payment_value), 2) AS payment_value,
    ROUND(
        SUM(payment_value) * 100.0 /
        SUM(SUM(payment_value)) OVER (),
        2
    ) AS payment_share_pct
FROM payments
GROUP BY payment_type
ORDER BY payment_value DESC;

##How heavily do customers use credit-card installments, and does higher installment usage correspond to larger transaction values?
SELECT
    payment_installments,
    COUNT(DISTINCT order_id) AS orders,
    ROUND(SUM(payment_value), 2) AS payment_value,
    ROUND(AVG(payment_value), 2) AS avg_payment_value
FROM payments
WHERE payment_type = 'credit_card'
GROUP BY payment_installments
ORDER BY payment_installments;

##How does average transaction value change across installment groups?
SELECT
    CASE
        WHEN payment_installments = 1
            THEN '1 installment'

        WHEN payment_installments BETWEEN 2 AND 3
            THEN '2-3 installments'

        WHEN payment_installments BETWEEN 4 AND 6
            THEN '4-6 installments'

        WHEN payment_installments BETWEEN 7 AND 9
            THEN '7-9 installments'

        ELSE '10+ installments'
    END AS installment_band,

    COUNT(DISTINCT order_id) AS orders,

    ROUND(SUM(payment_value), 2) AS payment_value,

    ROUND(AVG(payment_value), 2) AS avg_payment_value

FROM payments

WHERE payment_type = 'credit_card'

GROUP BY
    CASE
        WHEN payment_installments = 1
            THEN '1 installment'

        WHEN payment_installments BETWEEN 2 AND 3
            THEN '2-3 installments'

        WHEN payment_installments BETWEEN 4 AND 6
            THEN '4-6 installments'

        WHEN payment_installments BETWEEN 7 AND 9
            THEN '7-9 installments'

        ELSE '10+ installments'
    END

ORDER BY
    MIN(payment_installments);  ##Higher installment counts are associated with substantially higher transaction values.
    
    ##How does installment behavior differ across payment methods?
    SELECT
    payment_type,
    COUNT(DISTINCT order_id) AS orders,
    ROUND(AVG(payment_installments), 2) AS avg_installments,
    ROUND(AVG(payment_value), 2) AS avg_payment_value,
    ROUND(SUM(payment_value), 2) AS total_payment_value
FROM payments
WHERE payment_type <> 'not_defined'
GROUP BY payment_type
ORDER BY total_payment_value DESC;


#How are customers actually rating their orders?
SELECT
    review_score,
    COUNT(*) AS review_count,
    ROUND(
        COUNT(*) * 100.0 /
        SUM(COUNT(*)) OVER (),
        2
    ) AS review_percentage
FROM reviews
GROUP BY review_score
ORDER BY review_score;

##What percentage of negative reviews come from long-delivery orders?
SELECT
    CASE
        WHEN DATEDIFF(
            DATE(o.order_delivered_customer_date),
            DATE(o.order_purchase_timestamp)
        ) <= 7 THEN '0-7 days'

        WHEN DATEDIFF(
            DATE(o.order_delivered_customer_date),
            DATE(o.order_purchase_timestamp)
        ) <= 14 THEN '8-14 days'

        WHEN DATEDIFF(
            DATE(o.order_delivered_customer_date),
            DATE(o.order_purchase_timestamp)
        ) <= 30 THEN '15-30 days'

        ELSE '31+ days'
    END AS delivery_band,

    COUNT(*) AS reviews,

    SUM(
        CASE
            WHEN r.review_score IN (1, 2) THEN 1
            ELSE 0
        END
    ) AS negative_reviews,

    ROUND(
        SUM(
            CASE
                WHEN r.review_score IN (1, 2) THEN 1
                ELSE 0
            END
        ) * 100.0 / COUNT(*),
        2
    ) AS negative_review_pct

FROM orders o

JOIN reviews r
    ON o.order_id = r.order_id

WHERE o.order_status = 'delivered'
  AND o.order_delivered_customer_date IS NOT NULL

GROUP BY
    CASE
        WHEN DATEDIFF(
            DATE(o.order_delivered_customer_date),
            DATE(o.order_purchase_timestamp)
        ) <= 7 THEN '0-7 days'

        WHEN DATEDIFF(
            DATE(o.order_delivered_customer_date),
            DATE(o.order_purchase_timestamp)
        ) <= 14 THEN '8-14 days'

        WHEN DATEDIFF(
            DATE(o.order_delivered_customer_date),
            DATE(o.order_purchase_timestamp)
        ) <= 30 THEN '15-30 days'

        ELSE '31+ days'
    END

ORDER BY
    MIN(
        DATEDIFF(
            DATE(o.order_delivered_customer_date),
            DATE(o.order_purchase_timestamp)
        )
    );
    
    ##Very long delivery times are strongly associated with negative customer reviews. Orders taking 31+ days have a 64.47% negative-review rate, compared with only 7.57% for orders delivered within 7 days.
    SELECT
    CASE
        WHEN DATE(o.order_delivered_customer_date)
             < DATE(o.order_estimated_delivery_date)
            THEN 'Early'

        WHEN DATE(o.order_delivered_customer_date)
             = DATE(o.order_estimated_delivery_date)
            THEN 'On time'

        ELSE 'Late'
    END AS delivery_status,

    COUNT(DISTINCT o.order_id) AS orders,

    ROUND(
        COUNT(DISTINCT o.order_id) * 100.0 /
        SUM(COUNT(DISTINCT o.order_id)) OVER (),
        2
    ) AS percentage

FROM orders o

WHERE o.order_status = 'delivered'
  AND o.order_delivered_customer_date IS NOT NULL
  AND o.order_estimated_delivery_date IS NOT NULL

GROUP BY
    CASE
        WHEN DATE(o.order_delivered_customer_date)
             < DATE(o.order_estimated_delivery_date)
            THEN 'Early'

        WHEN DATE(o.order_delivered_customer_date)
             = DATE(o.order_estimated_delivery_date)
            THEN 'On time'

        ELSE 'Late'
    END;  ##"Early vs late" and "fast vs slow" are different metrics.
    
    
    SELECT
    CASE
        WHEN DATE(o.order_delivered_customer_date)
             < DATE(o.order_estimated_delivery_date)
            THEN 'Early'

        WHEN DATE(o.order_delivered_customer_date)
             = DATE(o.order_estimated_delivery_date)
            THEN 'On time'

        ELSE 'Late'
    END AS delivery_status,

    COUNT(*) AS reviews,

    ROUND(AVG(r.review_score), 2) AS avg_review_score,

    SUM(
        CASE
            WHEN r.review_score IN (1, 2) THEN 1
            ELSE 0
        END
    ) AS negative_reviews,

    ROUND(
        SUM(
            CASE
                WHEN r.review_score IN (1, 2) THEN 1
                ELSE 0
            END
        ) * 100.0 / COUNT(*),
        2
    ) AS negative_review_pct

FROM orders o

JOIN reviews r
    ON o.order_id = r.order_id

WHERE o.order_status = 'delivered'
  AND o.order_delivered_customer_date IS NOT NULL
  AND o.order_estimated_delivery_date IS NOT NULL

GROUP BY
    CASE
        WHEN DATE(o.order_delivered_customer_date)
             < DATE(o.order_estimated_delivery_date)
            THEN 'Early'

        WHEN DATE(o.order_delivered_customer_date)
             = DATE(o.order_estimated_delivery_date)
            THEN 'On time'

        ELSE 'Late'
    END

ORDER BY
    MIN(
        CASE
            WHEN DATE(o.order_delivered_customer_date)
                 < DATE(o.order_estimated_delivery_date)
                THEN 1

            WHEN DATE(o.order_delivered_customer_date)
                 = DATE(o.order_estimated_delivery_date)
                THEN 2

            ELSE 3
        END
    );
    ##Only 6.77% of delivered orders were late, but 62.41% of reviews associated with late orders were negative, compared with 9.23% for early deliveries.
    
    ###Which Brazilian states generate the most sales, and how does customer experience vary geographically?
    SELECT
    c.customer_state,

    COUNT(DISTINCT o.order_id) AS orders,

    ROUND(SUM(oi.price), 2) AS sales_value,

    ROUND(
        SUM(oi.price) / COUNT(DISTINCT o.order_id),
        2
    ) AS average_order_value

FROM customers c

JOIN orders o
    ON c.customer_id = o.customer_id

JOIN order_items oi
    ON o.order_id = oi.order_id

WHERE o.order_status = 'delivered'

GROUP BY
    c.customer_state

ORDER BY
    sales_value DESC;
    
    ###Which high-demand states have the worst delivery performance?
    SELECT
    c.customer_state,

    COUNT(DISTINCT o.order_id) AS orders,

    ROUND(SUM(oi.price), 2) AS sales_value,

    ROUND(
        AVG(
            DATEDIFF(
                DATE(o.order_delivered_customer_date),
                DATE(o.order_purchase_timestamp)
            )
        ),
        2
    ) AS avg_delivery_days,

    ROUND(
        AVG(r.review_score),
        2
    ) AS avg_review_score

FROM customers c

JOIN orders o
    ON c.customer_id = o.customer_id

JOIN order_items oi
    ON o.order_id = oi.order_id

LEFT JOIN reviews r
    ON o.order_id = r.order_id

WHERE o.order_status = 'delivered'
  AND o.order_delivered_customer_date IS NOT NULL

GROUP BY
    c.customer_state

HAVING COUNT(DISTINCT o.order_id) >= 500

ORDER BY
    avg_delivery_days DESC;
    
##Northern and northeastern markets tend to experience longer delivery times and somewhat lower review scores, while the high-volume Southeast markets—particularly São Paulo—show faster delivery and stronger satisfaction.
  
WITH customer_orders AS (
    SELECT
        c.customer_unique_id,
        o.order_id,
        DATE(o.order_purchase_timestamp) AS order_date
    FROM customers c
    JOIN orders o
        ON c.customer_id = o.customer_id
    WHERE o.order_status = 'delivered'
),

first_purchase AS (
    SELECT
        customer_unique_id,
        MIN(order_date) AS first_order_date
    FROM customer_orders
    GROUP BY customer_unique_id
),

cohort_data AS (
    SELECT
        co.customer_unique_id,

        DATE_FORMAT(
            fp.first_order_date,
            '%Y-%m'
        ) AS cohort_month,

        (
            YEAR(co.order_date) * 12
            + MONTH(co.order_date)
        )
        -
        (
            YEAR(fp.first_order_date) * 12
            + MONTH(fp.first_order_date)
        ) AS months_since_first_purchase

    FROM customer_orders co

    JOIN first_purchase fp
        ON co.customer_unique_id = fp.customer_unique_id
),

cohort_size AS (
    SELECT
        cohort_month,
        COUNT(DISTINCT customer_unique_id) AS cohort_customers
    FROM cohort_data
    WHERE months_since_first_purchase = 0
    GROUP BY cohort_month
)

SELECT
    cd.cohort_month,
    cd.months_since_first_purchase,
    COUNT(DISTINCT cd.customer_unique_id) AS returning_customers,
    cs.cohort_customers,

    ROUND(
        COUNT(DISTINCT cd.customer_unique_id) * 100.0
        / cs.cohort_customers,
        2
    ) AS retention_percentage

FROM cohort_data cd

JOIN cohort_size cs
    ON cd.cohort_month = cs.cohort_month

GROUP BY
    cd.cohort_month,
    cd.months_since_first_purchase,
    cs.cohort_customers

ORDER BY
    cd.cohort_month,
    cd.months_since_first_purchase;
    
    
##
SELECT
    oi.product_id,

    COUNT(DISTINCT oi.order_id) AS orders,

    ROUND(SUM(oi.price), 2) AS revenue,

    ROUND(AVG(oi.price), 2) AS avg_price,

    ROUND(AVG(r.review_score), 2) AS avg_review_score

FROM order_items oi

JOIN orders o
    ON oi.order_id = o.order_id

LEFT JOIN reviews r
    ON o.order_id = r.order_id

WHERE o.order_status = 'delivered'

GROUP BY
    oi.product_id

HAVING COUNT(DISTINCT oi.order_id) >= 20

ORDER BY
    revenue DESC

LIMIT 20;


##
SELECT
    p.product_id,
    p.product_category_name,

    COUNT(DISTINCT oi.order_id) AS orders,

    ROUND(SUM(oi.price), 2) AS revenue,

    ROUND(AVG(oi.price), 2) AS avg_price,

    ROUND(AVG(r.review_score), 2) AS avg_review_score

FROM products p

JOIN order_items oi
    ON p.product_id = oi.product_id

JOIN orders o
    ON oi.order_id = o.order_id

LEFT JOIN reviews r
    ON o.order_id = r.order_id

WHERE o.order_status = 'delivered'

GROUP BY
    p.product_id,
    p.product_category_name

HAVING COUNT(DISTINCT oi.order_id) >= 20

ORDER BY
    revenue DESC

LIMIT 20;

##
SELECT
    COUNT(DISTINCT p.product_id) AS products_missing_category,

    COUNT(DISTINCT oi.order_id) AS orders,

    ROUND(SUM(oi.price), 2) AS revenue

FROM products p

JOIN order_items oi
    ON p.product_id = oi.product_id

JOIN orders o
    ON oi.order_id = o.order_id

WHERE o.order_status = 'delivered'
  AND (
        p.product_category_name IS NULL
        OR TRIM(p.product_category_name) = ''
      );
      
      ## dealing with unknown categories
      SHOW TABLES;
      DESCRIBE category_translation;
      
      SELECT
    COUNT(*) AS missing_category_products,

    SUM(
        CASE
            WHEN product_category_name IS NULL THEN 1
            ELSE 0
        END
    ) AS null_categories,

    SUM(
        CASE
            WHEN TRIM(product_category_name) = '' THEN 1
            ELSE 0
        END
    ) AS blank_categories

FROM products
WHERE
    product_category_name IS NULL
    OR TRIM(product_category_name) = '';
    
    ##
    SELECT
    COUNT(*) AS total_categories,

    SUM(
        CASE
            WHEN product_category_name_english IS NULL
            THEN 1
            ELSE 0
        END
    ) AS missing_translations

FROM category_translation;

##Which sellers generate high revenue while maintaining good delivery and customer satisfaction?
SELECT
    oi.seller_id,

    COUNT(DISTINCT oi.order_id) AS orders,

    ROUND(
        SUM(oi.price),
        2
    ) AS revenue,

    ROUND(
        AVG(oi.price),
        2
    ) AS avg_order_value,

    ROUND(
        AVG(
            DATEDIFF(
                DATE(o.order_delivered_customer_date),
                DATE(o.order_purchase_timestamp)
            )
        ),
        2
    ) AS avg_delivery_days,

    ROUND(
        AVG(r.review_score),
        2
    ) AS avg_review_score

FROM order_items oi

JOIN orders o
    ON oi.order_id = o.order_id

LEFT JOIN reviews r
    ON o.order_id = r.order_id

WHERE
    o.order_status = 'delivered'
    AND o.order_delivered_customer_date IS NOT NULL

GROUP BY
    oi.seller_id

HAVING
    COUNT(DISTINCT oi.order_id) >= 50

ORDER BY
    revenue DESC;
    
    
##
WITH seller_performance AS (
    SELECT
        oi.seller_id,

        COUNT(DISTINCT oi.order_id) AS orders,

        ROUND(SUM(oi.price), 2) AS revenue,

        ROUND(AVG(oi.price), 2) AS avg_order_value,

        ROUND(
            AVG(
                DATEDIFF(
                    DATE(o.order_delivered_customer_date),
                    DATE(o.order_purchase_timestamp)
                )
            ),
            2
        ) AS avg_delivery_days,

        ROUND(
            AVG(r.review_score),
            2
        ) AS avg_review_score

    FROM order_items oi

    JOIN orders o
        ON oi.order_id = o.order_id

    LEFT JOIN reviews r
        ON o.order_id = r.order_id

    WHERE
        o.order_status = 'delivered'
        AND o.order_delivered_customer_date IS NOT NULL

    GROUP BY oi.seller_id

    HAVING COUNT(DISTINCT oi.order_id) >= 50
)

SELECT
    seller_id,
    orders,
    revenue,
    avg_order_value,
    avg_delivery_days,
    avg_review_score,

    CASE
        WHEN revenue >= 100000
             AND avg_delivery_days < 15
             AND avg_review_score >= 4.0
            THEN 'Strong'

        WHEN revenue >= 100000
             AND (
                    avg_delivery_days >= 20
                    OR avg_review_score < 3.8
                 )
            THEN 'At Risk'

        ELSE 'Monitor'
    END AS seller_segment

FROM seller_performance

ORDER BY
    revenue DESC;
    
    
##
WITH seller_performance AS (
    SELECT
        oi.seller_id,

        COUNT(DISTINCT oi.order_id) AS orders,

        ROUND(SUM(oi.price), 2) AS revenue,

        ROUND(AVG(oi.price), 2) AS avg_order_value,

        ROUND(
            AVG(
                DATEDIFF(
                    DATE(o.order_delivered_customer_date),
                    DATE(o.order_purchase_timestamp)
                )
            ),
            2
        ) AS avg_delivery_days,

        ROUND(AVG(r.review_score), 2) AS avg_review_score

    FROM order_items oi

    JOIN orders o
        ON oi.order_id = o.order_id

    LEFT JOIN reviews r
        ON o.order_id = r.order_id

    WHERE o.order_status = 'delivered'
      AND o.order_delivered_customer_date IS NOT NULL

    GROUP BY oi.seller_id

    HAVING COUNT(DISTINCT oi.order_id) >= 50
)

SELECT
    seller_id,
    orders,
    revenue,
    avg_order_value,
    avg_delivery_days,
    avg_review_score,

    CASE
        WHEN avg_delivery_days >= 20
             OR avg_review_score < 3.5
            THEN 'At Risk'

        WHEN revenue >= 100000
             AND avg_delivery_days < 15
             AND avg_review_score >= 4.0
            THEN 'Strong'

        ELSE 'Monitor'
    END AS performance_segment,

    CASE
        WHEN revenue >= 100000 THEN 'High'
        WHEN revenue >= 50000 THEN 'Medium'
        ELSE 'Low'
    END AS revenue_segment

FROM seller_performance

ORDER BY
    performance_segment,
    revenue DESC;
    
    
    
## final 
SELECT
    COUNT(DISTINCT o.order_id) AS total_orders,

    COUNT(DISTINCT o.customer_id) AS total_customers,

    COUNT(DISTINCT oi.seller_id) AS total_sellers,

    ROUND(SUM(oi.price), 2) AS total_revenue,

    ROUND(
        SUM(oi.price) / COUNT(DISTINCT o.order_id),
        2
    ) AS average_order_value

FROM orders o

JOIN order_items oi
    ON o.order_id = oi.order_id

WHERE o.order_status = 'delivered';

##
SELECT
    ROUND(
        SUM(order_revenue),
        2
    ) AS total_revenue,

    COUNT(*) AS delivered_orders,

    ROUND(
        SUM(order_revenue) / COUNT(*),
        2
    ) AS average_order_value

FROM (
    SELECT
        o.order_id,
        SUM(oi.price) AS order_revenue

    FROM orders o

    JOIN order_items oi
        ON o.order_id = oi.order_id

    WHERE o.order_status = 'delivered'

    GROUP BY o.order_id
) AS order_level_revenue;