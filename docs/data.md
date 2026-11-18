# Sales data

`setup_db.py` builds `sales.db` with a fixed random seed (`random.Random(42)`), so the same script produces the same rows. The database shipped in this repository is that result. Running the script again does not add orders, because it stops at order 500.

Readable copies of the totals are in `data/`.

| File | What it contains |
| --- | --- |
| `data/products.csv` | All 10 products and their list prices |
| `data/sales_by_region.csv` | Orders, sales, and profit for East, North, South, and West |
| `data/sales_by_product.csv` | Orders, units, sales, and profit for each product |
| `data/sales_by_month.csv` | Orders, sales, and profit for January through October 2026 |
| `data/payment_methods.csv` | How many payments used each method |

## Tables

`customers` has 100 people. Ages run from 18 to 65, and the average age is 38.9. Each person has one city, one state, and one region. There are 29 customers in the East, 18 in the North, 33 in the South, and 20 in the West.

`products` has 10 rows. The price on an order always matches `unit_price`.

| Product | Category | Unit price |
| --- | --- | --- |
| Laptop | Electronics | 800 |
| Printer | Electronics | 250 |
| Office Table | Furniture | 220 |
| Monitor | Electronics | 200 |
| Bookshelf | Furniture | 180 |
| Desk | Furniture | 150 |
| Chair | Furniture | 100 |
| Headphones | Electronics | 75 |
| Keyboard | Electronics | 50 |
| Mouse | Electronics | 20 |

`orders` has 500 rows. `sales` is `quantity * price`. `profit` is a random 10% to 30% of that sale, rounded to cents. Order dates run from 1 January 2026 through 31 October 2026.

`payments` has one row per order. The method is chosen from Credit Card, Debit Card, PayPal, Bank Transfer, and Cash. The status list is Completed three times, Pending once, and Failed once, so about 60% of payments are completed. The actual split is 303 completed, 108 pending, and 89 failed.

Joins used by the prompt:

- `orders.customer_id = customers.customer_id`
- `payments.order_id = orders.order_id`
- `orders.product_name = products.product_name`

Every order has a real customer, a real product, and a payment. No key is missing.

## Totals

| Measure | Value |
| --- | --- |
| Orders | 500 |
| Units sold | 2,816 |
| Sales | $531,395.00 |
| Profit | $103,698.22 |
| Profit margin | 19.5% |
| Average sale | $1,062.79 |

Sales by region:

| Region | Orders | Sales | Profit |
| --- | --- | --- | --- |
| South | 192 | $217,370.00 | $43,413.56 |
| East | 140 | $123,595.00 | $23,592.25 |
| North | 90 | $96,345.00 | $18,265.49 |
| West | 78 | $94,085.00 | $18,426.92 |

Laptop is the largest product by revenue, at $167,200. Electronics accounts for $335,865 of sales across 287 orders. Furniture accounts for $195,530 across 213 orders.

Monthly sales peak in February at $78,005 and are lowest in September at $29,550.

PayPal is the most used method, with 109 payments. Credit Card has 100, Debit Card 99, Cash 98, and Bank Transfer 94.

## Example questions and the SQL that answers them

These were run against `sales.db`.

Total profit is $103,698.22.

```sql
SELECT ROUND(SUM(profit), 2) AS total_profit
FROM orders;
```

There are 500 orders.

```sql
SELECT COUNT(*) AS order_count
FROM orders;
```

Sales by region, highest first:

```sql
SELECT region, ROUND(SUM(sales), 2) AS total_sales
FROM orders
GROUP BY region
ORDER BY total_sales DESC;
```

The product with the highest sales is Laptop, at $167,200.

```sql
SELECT product_name, ROUND(SUM(sales), 2) AS total_sales
FROM orders
GROUP BY product_name
ORDER BY total_sales DESC
LIMIT 1;
```

The most common payment method is PayPal, used 109 times.

```sql
SELECT payment_method, COUNT(*) AS uses
FROM payments
GROUP BY payment_method
ORDER BY uses DESC
LIMIT 1;
```

39 customers have more than 5 orders. The busiest is Sophia Thomas of Dallas, with 11 orders. James Smith of Dallas has the highest sales among customers with more than 5 orders, at $24,040.

```sql
SELECT
    customers.customer_name,
    customers.city,
    customers.region,
    COUNT(*) AS orders,
    ROUND(SUM(orders.sales), 2) AS sales
FROM orders
JOIN customers ON orders.customer_id = customers.customer_id
GROUP BY customers.customer_id
HAVING COUNT(*) > 5
ORDER BY orders DESC, customers.customer_name;
```

## Two details that affect the numbers

Eight of the original orders keep the region they were given before a customer was attached. `setup_db.py` sets `customer_id` on orders 1 through 10, and it does not rewrite `orders.region`. Orders 2, 3, 4, 5, 6, 7, 9, and 10 disagree with that customer's region. The other 492 orders copy the customer region when they are created.

`evaluate.py` and `evaluate_extended.py` still expect the original 10-order database: 10 orders, $7,750 sales, $1,350 profit, and 5 products. Those figures are in `sales_backup.db`, which has only the `orders` table. The tests compare against `sales.db`, so exact-match checks fail on the current 500-order data even when the SQL is right.
