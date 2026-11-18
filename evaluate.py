
import time

from sql_engine import generate_sql, execute_sql


# --------------------------------------------------
# TEST 1: NORMAL NATURAL-LANGUAGE QUESTIONS
# --------------------------------------------------

VALID_TEST_CASES = [
    {
        "question": "How many orders are there?",
        "expected": [(10,)]
    },
    {
        "question": "What are the total sales for each region?",
        "expected": [
            ("East", 2450.0),
            ("North", 1100.0),
            ("South", 1100.0),
            ("West", 3100.0)
        ]
    },
    {
        "question": "Which product generated the highest total sales?",
        "expected": [("Laptop", 4800.0)]
    },
    {
        "question": "What is the total profit?",
        "expected": [(1350.0,)]
    },
    {
        "question": "How many distinct products are in the orders table?",
        "expected": [(5,)]
    }
]


# --------------------------------------------------
# TEST 2: SQL SAFETY AND ERROR HANDLING
# --------------------------------------------------

SAFETY_TEST_CASES = [
    {
        "name": "Hallucinated column",
        "sql": "SELECT imaginary_column FROM orders"
    },
    {
        "name": "Unauthorized table",
        "sql": "SELECT * FROM customers"
    },
    {
        "name": "DELETE statement",
        "sql": "DELETE FROM orders WHERE 1=1"
    },
    {
        "name": "DROP TABLE statement",
        "sql": "DROP TABLE orders"
    },
    {
        "name": "Multiple SQL statements",
        "sql": "SELECT COUNT(*) FROM orders; DROP TABLE orders"
    },
    {
        "name": "Invalid SQL syntax",
        "sql": "SELEC FROM orders"
    },
    {
        "name": "Unauthorized table in JOIN",
        "sql": (
            "SELECT * FROM orders "
            "JOIN customers ON orders.order_id = customers.order_id"
        )
    }
]


def normalize(rows):
    """Normalize query results for order-independent comparison."""
    return sorted(
        [tuple(row) for row in rows],
        key=lambda row: str(row)
    )


def run_valid_tests():
    passed = 0
    response_times = []

    print("\n" + "=" * 65)
    print("NATURAL-LANGUAGE-TO-SQL EVALUATION")
    print("=" * 65)

    for index, test in enumerate(VALID_TEST_CASES, start=1):
        start = time.perf_counter()

        print(f"\nTest {index}: {test['question']}")

        try:
            sql = generate_sql(test["question"])
            columns, rows = execute_sql(sql)

            elapsed = time.perf_counter() - start
            response_times.append(elapsed)

            expected = normalize(test["expected"])
            actual = normalize(rows)

            success = actual == expected

            if success:
                passed += 1

            print("Generated SQL:", sql)
            print("Expected:", expected)
            print("Actual:", actual)
            print("Status:", "PASS" if success else "FAIL")
            print(f"Response time: {elapsed:.2f} seconds")

        except Exception as error:
            print("Status: ERROR")
            print("Details:", error)

    total = len(VALID_TEST_CASES)

    print("\nValid-query results:")
    print(f"Passed: {passed}/{total}")
    print(f"Exact-result accuracy: {passed / total * 100:.1f}%")

    if response_times:
        average = sum(response_times) / len(response_times)
        print(f"Average response time: {average:.2f} seconds")

    return passed, total


def run_safety_tests():
    passed = 0

    print("\n" + "=" * 65)
    print("SQL SAFETY AND ERROR-HANDLING TESTS")
    print("=" * 65)

    for index, test in enumerate(SAFETY_TEST_CASES, start=1):
        print(f"\nSafety test {index}: {test['name']}")
        print("SQL:", test["sql"])

        try:
            columns, rows = execute_sql(test["sql"])

            # These tests should all be rejected.
            print("Status: FAIL")
            print("Reason: The query was not rejected.")

        except Exception as error:
            # An exception is expected for these invalid or
            # unauthorized SQL statements.
            passed += 1
            print("Status: PASS - Query rejected")
            print("Rejection reason:", str(error))

    total = len(SAFETY_TEST_CASES)

    print("\nSafety-test results:")
    print(f"Rejected as expected: {passed}/{total}")
    print(f"Safety rejection rate: {passed / total * 100:.1f}%")

    return passed, total


def main():
    valid_passed, valid_total = run_valid_tests()
    safety_passed, safety_total = run_safety_tests()

    print("\n" + "=" * 65)
    print("OVERALL EVALUATION SUMMARY")
    print("=" * 65)

    print(
        f"Valid-query accuracy: "
        f"{valid_passed}/{valid_total} "
        f"({valid_passed / valid_total * 100:.1f}%)"
    )

    print(
        f"Safety tests passed: "
        f"{safety_passed}/{safety_total} "
        f"({safety_passed / safety_total * 100:.1f}%)"
    )

    print(
        f"Total test cases passed: "
        f"{valid_passed + safety_passed}/"
        f"{valid_total + safety_total}"
    )

    print("\nEvaluation completed.")


if __name__ == "__main__":
    main()
