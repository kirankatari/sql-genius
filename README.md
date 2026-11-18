# SQL Genius

SQL Genius is a local app that turns an English question into one SQLite query, checks that the query is safe, and runs it on a sample sales database.

The database is already filled. `sales.db` has 100 customers, 10 products, 500 orders, and 500 payments, dated 1 January 2026 through 31 October 2026.

## What each file does

| File | Purpose |
| --- | --- |
| `app.py` | Streamlit app with Query Studio, query history, and a database explorer |
| `sql_engine.py` | Sends the question and schema to Ollama, then runs only a single read-only `SELECT` |
| `setup_db.py` | Creates the four tables and fills `sales.db` |
| `sales.db` | The database the app queries |
| `sales_backup.db` | The original 10-order table used when the evaluation numbers were written |
| `evaluate.py` | Five question tests and seven safety tests |
| `evaluate_extended.py` | Fifteen question tests |
| `prompt_experiment.py` | Compares a basic prompt with a schema-aware prompt |
| `prompt_experiment_results.csv` | Saved result of that comparison |
| `verify_safety.py` | Ten queries that must be rejected |
| `data/` | Readable copies of the main totals in `sales.db` |

The prompts are explained in [docs/prompts.md](docs/prompts.md). The tables, totals, and example answers are explained in [docs/data.md](docs/data.md).

## Run the app

Install [Ollama](https://ollama.com), then pull the model the app expects:

```bash
ollama pull qwen2.5-coder:3b
```

From this folder:

```bash
pip install -r requirements.txt
streamlit run app.py
```

`sql_engine.py` calls `http://localhost:11434` and asks for `qwen2.5-coder:3b`. The page can open without Ollama, but **Generate SQL** fails until that model is running.

## Questions to try

These six questions are the buttons in Query Studio. The answers below were calculated directly from `sales.db`.

| Question | Result |
| --- | --- |
| What is the total profit? | $103,698.22 |
| How many orders are there? | 500 |
| What are the total sales for each region? | South $217,370, East $123,595, North $96,345, West $94,085 |
| Which product generated the highest total sales? | Laptop, $167,200 |
| Which payment method is used most frequently? | PayPal, 109 payments |
| Which customers have placed more than 5 orders? | 39 customers |

## How a question is answered

1. The app reads the table and column names from `sales.db`. It does not send any customer or order rows to the model.
2. It builds one prompt that contains the rules, the schema, and the question.
3. Ollama returns one SQLite statement.
4. SQLGlot checks that the statement is a single `SELECT` and that it only uses `orders`, `customers`, `products`, and `payments`.
5. SQLite runs it in read-only mode and the app shows at most 100 rows.

## Rebuild the database

`setup_db.py` is safe to run again. Customers and products use `INSERT OR IGNORE`, and new orders stop at 500, so a second run does not add more rows.

```bash
python setup_db.py
```
