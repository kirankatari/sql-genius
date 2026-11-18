
from sql_engine import execute_sql


# Rejected queries must raise an exception.
UNSAFE_TESTS = [
    (
        "DELETE statement",
        "DELETE FROM orders WHERE 1=1"
    ),
    (
        "DROP TABLE statement",
        "DROP TABLE orders"
    ),
    (
        "UPDATE statement",
        "UPDATE orders SET sales = 0"
    ),
    (
        "INSERT statement",
        "INSERT INTO orders (order_id) VALUES (999)"
    ),
    (
        "Unauthorized table",
        "SELECT * FROM customers"
    ),
    (
        "Unauthorized JOIN",
        "SELECT * FROM orders "
        "JOIN customers "
        "ON orders.order_id = customers.order_id"
    ),
    (
        "Invalid column",
        "SELECT imaginary_column FROM orders"
    ),
    (
        "Multiple statements",
        "SELECT * FROM orders; DROP TABLE orders"
    ),
    (
        "Invalid SQL syntax",
        "SELEC FROM orders"
    ),
    (
        "PRAGMA statement",
        "PRAGMA table_info(orders)"
    )
]


def main():
    passed = 0
    total = len(UNSAFE_TESTS)

    print("=" * 65)
    print("SQL GENIUS - ADDITIONAL SAFETY TESTS")
    print("=" * 65)

    for name, sql in UNSAFE_TESTS:
        print(f"\nTest: {name}")
        print("SQL:", sql)

        try:
            execute_sql(sql)
            print("FAIL: Query was not rejected.")

        except Exception as error:
            passed += 1
            print("PASS: Query rejected.")
            print("Reason:", error)

    print("\n" + "=" * 65)
    print(f"Safety tests passed: {passed}/{total}")
    print(f"Safety rejection rate: {passed / total * 100:.1f}%")
    print("=" * 65)


if __name__ == "__main__":
    main()
