
import time
import csv
import requests

from sql_engine import (
    get_schema,
    execute_sql,
    MODEL,
    OLLAMA_URL
)


# Same questions and expected results for both methods.
TEST_CASES = [
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
        "question": "How many distinct products are there?",
        "expected": [(5,)]
    }
]


def generate_experiment_sql(question, method, schema):
    """Generate SQL using basic or schema-aware prompting."""

    if method == "basic":
        prompt = f"""
Convert the user's question into one SQLite SELECT query
for a sales database.

Return only SQL. Do not include markdown or explanations.
Do not generate INSERT, UPDATE, DELETE, DROP, or other
data-modifying statements.

Question: {question}

SQL:
"""
    else:
        prompt = f"""
You are an expert SQLite SQL assistant.

Generate one read-only SELECT query that answers the
user's question accurately.

Database schema:
{schema}

Rules:
- Use only the tables and columns in the schema.
- Use exact table and column names.
- Use SQLite-compatible SQL.
- Use GROUP BY for aggregations when required.
- Use ORDER BY and LIMIT to find the highest or lowest
  result when appropriate.
- Return one SQL query only.
- Do not include markdown or explanations.
- Do not generate INSERT, UPDATE, DELETE, DROP, or
  other data-modifying statements.

Question: {question}

SQL:
"""

    response = requests.post(
        OLLAMA_URL,
        json={
            "model": MODEL,
            "prompt": prompt,
            "stream": False,
            "options": {"temperature": 0}
        },
        timeout=120
    )

    response.raise_for_status()

    sql = response.json()["response"].strip()

    # Remove markdown fences if the model returns them.
    if sql.startswith("```"):
        lines = sql.splitlines()

        if lines and lines[0].startswith("```"):
            lines = lines[1:]

        if lines and lines[-1].strip() == "```":
            lines = lines[:-1]

        sql = "\n".join(lines).strip()

    return sql


def normalize(rows):
    """Compare rows without depending on their order."""

    return sorted(
        [tuple(row) for row in rows],
        key=lambda row: str(row)
    )


def run_experiment(method, schema):
    """Run all test questions for one prompting method."""

    results = []

    print("\n" + "=" * 75)
    print(f"METHOD: {method.upper()}")
    print("=" * 75)

    for index, test in enumerate(TEST_CASES, start=1):
        start = time.perf_counter()

        sql = ""
        actual = ""
        error_message = ""
        status = "ERROR"

        print(f"\nTest {index}: {test['question']}")

        try:
            sql = generate_experiment_sql(
                test["question"],
                method,
                schema
            )

            # Print SQL before execution so it remains visible
            # even if validation or execution fails.
            print("Generated SQL:")
            print(sql)

            columns, rows = execute_sql(sql)
            actual = repr(normalize(rows))

            success = (
                normalize(rows) == normalize(test["expected"])
            )

            if success:
                status = "PASS"
            else:
                status = "FAIL"

            print("Expected:", normalize(test["expected"]))
            print("Actual:", actual)
            print("Status:", status)

        except requests.RequestException as error:
            error_message = (
                f"Ollama request failed: {error}"
            )
            print("Status: ERROR")
            print("Details:", error_message)

        except Exception as error:
            error_message = str(error)
            print("Status: ERROR")
            print("Details:", error_message)

        elapsed = time.perf_counter() - start
        print(f"Total time: {elapsed:.2f} seconds")

        results.append({
            "method": method,
            "question": test["question"],
            "generated_sql": sql,
            "expected": repr(normalize(test["expected"])),
            "actual": actual,
            "status": status,
            "error": error_message,
            "time_seconds": round(elapsed, 2)
        })

    return results


def summarize(results, method):
    """Calculate summary metrics for one method."""

    total = len(results)
    passed = sum(
        result["status"] == "PASS"
        for result in results
    )
    failed = sum(
        result["status"] == "FAIL"
        for result in results
    )
    errors = sum(
        result["status"] == "ERROR"
        for result in results
    )

    total_time = sum(
        result["time_seconds"]
        for result in results
    )

    return {
        "method": method,
        "total": total,
        "passed": passed,
        "failed": failed,
        "errors": errors,
        "accuracy": passed / total * 100 if total else 0,
        "average_time": total_time / total if total else 0
    }


def save_csv(results):
    """Save individual test results for the project report."""

    filename = "prompt_experiment_results.csv"

    fieldnames = [
        "method",
        "question",
        "generated_sql",
        "expected",
        "actual",
        "status",
        "error",
        "time_seconds"
    ]

    with open(
        filename,
        "w",
        newline="",
        encoding="utf-8"
    ) as file:
        writer = csv.DictWriter(
            file,
            fieldnames=fieldnames
        )

        writer.writeheader()
        writer.writerows(results)

    print(f"\nDetailed results saved to: {filename}")


def main():
    print("=" * 75)
    print("SQL GENIUS - PROMPTING EXPERIMENT")
    print("=" * 75)

    print("Model:", MODEL)
    print("Database: sales.db")
    print("Questions per method:", len(TEST_CASES))

    try:
        schema = get_schema()

        basic_results = run_experiment("basic", schema)
        aware_results = run_experiment("schema", schema)

        all_results = basic_results + aware_results

        basic_summary = summarize(basic_results, "Basic")
        aware_summary = summarize(aware_results, "Schema-aware")

        print("\n" + "=" * 75)
        print("FINAL COMPARISON")
        print("=" * 75)

        print(
            f"{'Metric':<28}"
            f"{'Basic':<18}"
            f"{'Schema-aware':<18}"
        )

        print("-" * 64)

        print(
            f"{'Exact-result accuracy':<28}"
            f"{basic_summary['accuracy']:.1f}%"
            f"{aware_summary['accuracy']:.1f}%"
        )

        print(
            f"{'Passed tests':<28}"
            f"{basic_summary['passed']}/{basic_summary['total']}"
            f"{aware_summary['passed']}/{aware_summary['total']}"
        )

        print(
            f"{'Failed tests':<28}"
            f"{basic_summary['failed']}"
            f"{aware_summary['failed']}"
        )

        print(
            f"{'Execution errors':<28}"
            f"{basic_summary['errors']}"
            f"{aware_summary['errors']}"
        )

        print(
            f"{'Average time (seconds)':<28}"
            f"{basic_summary['average_time']:.2f}"
            f"{aware_summary['average_time']:.2f}"
        )

        print("\n" + "=" * 75)
        print("EXPERIMENT CONCLUSION")
        print("=" * 75)

        difference = (
            aware_summary["accuracy"]
            - basic_summary["accuracy"]
        )

        print(
            f"Accuracy difference: {difference:+.1f} "
            "percentage points"
        )

        if difference > 0:
            print(
                "Schema-aware prompting performed better "
                "on this test set."
            )
        elif difference < 0:
            print(
                "Basic prompting performed better "
                "on this test set."
            )
        else:
            print(
                "Both methods achieved the same accuracy "
                "on this test set."
            )

        save_csv(all_results)

        print("\nExperiment completed successfully.")

    except requests.RequestException as error:
        print("\nCould not connect to Ollama:", error)

    except Exception as error:
        print("\nExperiment failed:", error)


if __name__ == "__main__":
    main()
