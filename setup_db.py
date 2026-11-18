
import sqlite3
import random
from datetime import date, timedelta

# Reproducible sample data
rng = random.Random(42)

conn = sqlite3.connect("sales.db")
cursor = conn.cursor()

# 1. Create customers table
cursor.execute("""
CREATE TABLE IF NOT EXISTS customers (
    customer_id INTEGER PRIMARY KEY,
    customer_name TEXT,
    age INTEGER,
    city TEXT,
    state TEXT,
    region TEXT
)
""")

# 2. Create products table
cursor.execute("""
CREATE TABLE IF NOT EXISTS products (
    product_id INTEGER PRIMARY KEY,
    product_name TEXT UNIQUE,
    category TEXT,
    unit_price REAL
)
""")

# 3. Keep the existing orders table structure
cursor.execute("""
CREATE TABLE IF NOT EXISTS orders (
    order_id INTEGER PRIMARY KEY,
    order_date TEXT,
    product_name TEXT,
    category TEXT,
    quantity INTEGER,
    price REAL,
    sales REAL,
    profit REAL,
    region TEXT
)
""")

# Add customer_id to an existing orders table if needed
columns = [
    row[1] for row in cursor.execute(
        "PRAGMA table_info(orders)"
    ).fetchall()
]

if "customer_id" not in columns:
    cursor.execute(
        "ALTER TABLE orders ADD COLUMN customer_id INTEGER"
    )

# 4. Create payments table
cursor.execute("""
CREATE TABLE IF NOT EXISTS payments (
    payment_id INTEGER PRIMARY KEY,
    order_id INTEGER UNIQUE,
    payment_method TEXT,
    payment_status TEXT
)
""")

# 5. Insert customers
cities = [
    ("New York", "New York", "East"),
    ("Boston", "Massachusetts", "East"),
    ("Chicago", "Illinois", "North"),
    ("Detroit", "Michigan", "North"),
    ("Dallas", "Texas", "South"),
    ("Houston", "Texas", "South"),
    ("Los Angeles", "California", "West"),
    ("Seattle", "Washington", "West"),
    ("Miami", "Florida", "South"),
    ("Philadelphia", "Pennsylvania", "East")
]

first_names = [
    "John", "Sarah", "David", "Emily", "Michael",
    "Emma", "Daniel", "Olivia", "James", "Sophia",
    "Robert", "Ava", "William", "Mia", "Joseph"
]

last_names = [
    "Smith", "Johnson", "Brown", "Davis", "Wilson",
    "Miller", "Taylor", "Anderson", "Thomas", "Moore"
]

for customer_id in range(1, 101):
    city, state, region = rng.choice(cities)
    name = (
        f"{rng.choice(first_names)} "
        f"{rng.choice(last_names)}"
    )

    cursor.execute("""
    INSERT OR IGNORE INTO customers
    VALUES (?, ?, ?, ?, ?, ?)
    """, (
        customer_id,
        name,
        rng.randint(18, 65),
        city,
        state,
        region
    ))

# 6. Insert products
product_data = [
    (1, "Laptop", "Electronics", 800),
    (2, "Mouse", "Electronics", 20),
    (3, "Desk", "Furniture", 150),
    (4, "Chair", "Furniture", 100),
    (5, "Monitor", "Electronics", 200),
    (6, "Keyboard", "Electronics", 50),
    (7, "Printer", "Electronics", 250),
    (8, "Bookshelf", "Furniture", 180),
    (9, "Headphones", "Electronics", 75),
    (10, "Office Table", "Furniture", 220)
]

cursor.executemany("""
INSERT OR IGNORE INTO products
(product_id, product_name, category, unit_price)
VALUES (?, ?, ?, ?)
""", product_data)

# 7. Assign customers to the original 10 orders
cursor.execute("""
UPDATE orders
SET customer_id = ((order_id - 1) % 100) + 1
WHERE customer_id IS NULL
""")

# 8. Generate orders until the database has 500 orders
existing_count = cursor.execute(
    "SELECT COUNT(*) FROM orders"
).fetchone()[0]

next_order_id = cursor.execute(
    "SELECT COALESCE(MAX(order_id), 0) + 1 FROM orders"
).fetchone()[0]

start_date = date(2026, 1, 1)

for order_id in range(next_order_id, 501):

    product_id, product_name, category, price = rng.choice(
        product_data
    )

    customer_id = rng.randint(1, 100)

    customer_region = cursor.execute("""
        SELECT region FROM customers
        WHERE customer_id = ?
    """, (customer_id,)).fetchone()[0]

    quantity = rng.randint(1, 10)
    sales = quantity * price
    profit = round(sales * rng.uniform(0.10, 0.30), 2)

    order_date = start_date + timedelta(
        days=rng.randint(0, 303)
    )

    cursor.execute("""
    INSERT INTO orders (
        order_id, order_date, product_name, category,
        quantity, price, sales, profit, region, customer_id
    )
    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        order_id,
        order_date.isoformat(),
        product_name,
        category,
        quantity,
        price,
        sales,
        profit,
        customer_region,
        customer_id
    ))

# 9. Add payment information for all orders
payment_methods = [
    "Credit Card", "Debit Card", "PayPal",
    "Bank Transfer", "Cash"
]

payment_statuses = [
    "Completed", "Completed", "Completed",
    "Pending", "Failed"
]

orders = cursor.execute("""
SELECT order_id FROM orders
""").fetchall()

for (order_id,) in orders:
    cursor.execute("""
    INSERT OR IGNORE INTO payments
    (payment_id, order_id, payment_method, payment_status)
    VALUES (?, ?, ?, ?)
    """, (
        order_id,
        order_id,
        rng.choice(payment_methods),
        rng.choice(payment_statuses)
    ))

conn.commit()

# 10. Display database summary
print("\nDatabase expanded successfully!")

for table in ["customers", "products", "orders", "payments"]:
    count = cursor.execute(
        f"SELECT COUNT(*) FROM {table}"
    ).fetchone()[0]

    print(f"Total {table}: {count}")

conn.close()
