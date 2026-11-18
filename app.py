
import streamlit as st
import pandas as pd
import sqlite3
import time
from datetime import datetime
from sql_engine import generate_sql, execute_sql

# --------------------------------------------------
# PAGE CONFIGURATION
# --------------------------------------------------

st.set_page_config(
    page_title="NEXUS | SQL Genius",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="expanded"
)

DB_PATH = "sales.db"

# --------------------------------------------------
# CUSTOM DESIGN SYSTEM
# --------------------------------------------------

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@400;500;600;700;800&family=Space+Grotesk:wght@500;600;700&display=swap');

:root {
    --bg: #080D19;
    --panel: #111A2B;
    --panel-light: #172238;
    --border: rgba(148, 163, 184, 0.15);
    --blue: #60A5FA;
    --purple: #A78BFA;
    --text: #F1F5F9;
    --muted: #94A3B8;
    --green: #4ADE80;
}

html, body, [class*="css"] {
    font-family: 'DM Sans', sans-serif;
}

.stApp {
    background:
        radial-gradient(ellipse at 15% 0%, rgba(37, 99, 235, .12), transparent 35%),
        radial-gradient(ellipse at 90% 15%, rgba(124, 58, 237, .10), transparent 30%),
        var(--bg);
    color: var(--text);
}

[data-testid="stHeader"] {
    background: transparent;
}

[data-testid="stSidebar"] {
    background: #0D1525;
    border-right: 1px solid var(--border);
}

[data-testid="stSidebar"] * {
    color: #DCE6F5;
}

.block-container {
    padding-top: 2rem;
    padding-bottom: 3rem;
    max-width: 1500px;
}

h1, h2, h3 {
    font-family: 'Space Grotesk', sans-serif !important;
    color: var(--text) !important;
}

p, label, span {
    color: inherit;
}

.nexus-brand {
    font-family: 'Space Grotesk', sans-serif;
    font-size: 25px;
    font-weight: 700;
    letter-spacing: 2px;
    color: white;
}

.nexus-sub {
    color: #8FA5C4;
    font-size: 11px;
    letter-spacing: 2px;
    margin-top: -5px;
}

.hero {
    background: linear-gradient(120deg, #152744 0%, #171D3C 55%, #24204A 100%);
    border: 1px solid rgba(125, 150, 255, .25);
    border-radius: 22px;
    padding: 30px;
    margin-bottom: 25px;
    position: relative;
    overflow: hidden;
}

.hero-tag {
    color: #93C5FD;
    font-size: 11px;
    font-weight: 700;
    letter-spacing: 2px;
    margin-bottom: 12px;
}

.hero-title {
    color: white;
    font-family: 'Space Grotesk', sans-serif;
    font-size: clamp(27px, 4vw, 42px);
    font-weight: 700;
    line-height: 1.2;
}

.hero-description {
    color: #B8C7DF;
    font-size: 14px;
    margin-top: 12px;
    max-width: 650px;
    line-height: 1.7;
}

.panel {
    background: linear-gradient(145deg, #121D30, #101827);
    border: 1px solid var(--border);
    border-radius: 17px;
    padding: 21px;
    margin-bottom: 17px;
}

.panel-title {
    font-family: 'Space Grotesk', sans-serif;
    color: #E8F0FC;
    font-weight: 600;
    font-size: 16px;
}

.panel-caption {
    color: var(--muted);
    font-size: 12px;
    margin-top: 5px;
}

.metric {
    background: linear-gradient(145deg, #14233B, #111A2C);
    border: 1px solid var(--border);
    border-radius: 15px;
    padding: 17px;
    min-height: 112px;
}

.metric-label {
    color: #91A4BF;
    font-size: 12px;
}

.metric-value {
    font-family: 'Space Grotesk', sans-serif;
    font-size: 27px;
    font-weight: 700;
    color: white;
    margin-top: 8px;
}

.metric-icon {
    font-size: 19px;
}

div.stButton > button {
    border-radius: 10px;
    border: 1px solid rgba(96, 165, 250, .3);
    background: #172A48;
    color: #DBEAFE;
    font-weight: 600;
    transition: .2s ease;
}

div.stButton > button:hover {
    border-color: #60A5FA;
    background: #203A60;
    color: white;
}

div.stButton > button[kind="primary"] {
    background: linear-gradient(100deg, #2563EB, #7045D9);
    border: none;
    color: white;
    min-height: 46px;
}

div.stButton > button[kind="primary"]:hover {
    background: linear-gradient(100deg, #3478F6, #8258EB);
}

.stTextArea textarea {
    background: #0C1423 !important;
    border: 1px solid #34445E !important;
    border-radius: 12px !important;
    color: #F1F5F9 !important;
    font-size: 15px !important;
}

.stTextArea textarea:focus {
    border-color: #60A5FA !important;
    box-shadow: 0 0 0 1px #60A5FA !important;
}

[data-testid="stDataFrame"] {
    border: 1px solid var(--border);
    border-radius: 12px;
}

.stCodeBlock {
    border: 1px solid var(--border);
    border-radius: 12px;
}

div[data-testid="stExpander"] {
    background: #111A2B;
    border: 1px solid var(--border);
    border-radius: 12px;
}

hr {
    border-color: var(--border);
}

.small-muted {
    color: #8FA5C4;
    font-size: 12px;
}

.status-pill {
    display: inline-block;
    padding: 5px 10px;
    border-radius: 20px;
    background: rgba(74, 222, 128, .1);
    border: 1px solid rgba(74, 222, 128, .25);
    color: #86EFAC;
    font-size: 11px;
    font-weight: 700;
}
</style>
""", unsafe_allow_html=True)


# --------------------------------------------------
# DATABASE INFORMATION
# --------------------------------------------------

def get_database_stats():
    stats = {}

    with sqlite3.connect(DB_PATH) as conn:
        tables = ["orders", "customers", "products", "payments"]
        total_records = 0

        for table in tables:
            count = conn.execute(
                f"SELECT COUNT(*) FROM {table}"
            ).fetchone()[0]

            stats[table] = count
            total_records += count

    stats["total_tables"] = len(tables)
    stats["total_records"] = total_records

    return stats


def get_database_schema():
    schema = {}

    with sqlite3.connect(DB_PATH) as conn:
        tables = conn.execute("""
            SELECT name
            FROM sqlite_master
            WHERE type='table'
            AND name NOT LIKE 'sqlite_%'
            ORDER BY name
        """).fetchall()

        for (table,) in tables:
            columns = conn.execute(
                f"PRAGMA table_info({table})"
            ).fetchall()

            schema[table] = [
                {
                    "column": column[1],
                    "type": column[2]
                }
                for column in columns
            ]

    return schema


# --------------------------------------------------
# SESSION STATE
# --------------------------------------------------

if "query_history" not in st.session_state:
    st.session_state.query_history = []

if "question" not in st.session_state:
    st.session_state.question = ""

if "last_result" not in st.session_state:
    st.session_state.last_result = None


# --------------------------------------------------
# SIDEBAR
# --------------------------------------------------

with st.sidebar:

    st.markdown("""
        <div style="padding: 10px 0 25px 0;">
            <div class="nexus-brand">⚡ NEXUS</div>
            <div class="nexus-sub">SQL GENIUS INTELLIGENCE</div>
        </div>
    """, unsafe_allow_html=True)

    st.markdown("### WORKSPACE")

    page = st.radio(
        "Navigation",
        [
            "Query Studio",
            "Query History",
            "Database Explorer"
        ],
        label_visibility="collapsed"
    )

    st.markdown("---")

    st.markdown("### SYSTEM STATUS")

    st.markdown(
        '<span class="status-pill">● APPLICATION ACTIVE</span>',
        unsafe_allow_html=True
    )

    st.markdown("<br>", unsafe_allow_html=True)

    st.markdown("**AI ENGINE**")
    st.caption("Ollama · Qwen 2.5 Coder 3B")

    st.markdown("**DATABASE**")
    st.caption("SQLite · sales.db")

    st.markdown("**EXECUTION**")
    st.caption("Python SQL Engine")

    st.markdown("---")
    st.caption("NEXUS | SQL Genius")
    st.caption("Natural Language to SQL")


# --------------------------------------------------
# HEADER
# --------------------------------------------------

st.markdown("""
<div style="display:flex; justify-content:space-between;
align-items:center; margin-bottom:22px;">
    <div>
        <div style="color:#8FA5C4; font-size:11px;
        letter-spacing:2px; font-weight:700;">
            INTELLIGENCE WORKSPACE
        </div>
    </div>
    <div class="status-pill">● SYSTEM ONLINE</div>
</div>
""", unsafe_allow_html=True)


# --------------------------------------------------
# QUERY STUDIO
# --------------------------------------------------

if page == "Query Studio":

    st.markdown("""
    <div class="hero">
        <div class="hero-tag">✦ NATURAL LANGUAGE DATABASE INTELLIGENCE</div>
        <div class="hero-title">
            Your questions.<br>
            Transformed into SQL.
        </div>
        <div class="hero-description">
            Explore your database using simple English.
            Let local AI translate your questions into SQL,
            validate the query and retrieve meaningful results.
        </div>
    </div>
    """, unsafe_allow_html=True)

    # Database metrics

    try:
        stats = get_database_stats()

        c1, c2, c3, c4 = st.columns(4)

        metrics = [
            (c1, "DATABASE TABLES", stats["total_tables"], "▦"),
            (c2, "TOTAL RECORDS", f'{stats["total_records"]:,}', "◫"),
            (c3, "ORDERS", f'{stats["orders"]:,}', "↗"),
            (c4, "PRODUCTS", f'{stats["products"]:,}', "◇")
        ]

        for col, label, value, icon in metrics:
            with col:
                st.markdown(f"""
                <div class="metric">
                    <div class="metric-label">
                        <span class="metric-icon">{icon}</span>
                        &nbsp; {label}
                    </div>
                    <div class="metric-value">{value}</div>
                </div>
                """, unsafe_allow_html=True)

    except Exception as error:
        st.warning(f"Database overview unavailable: {error}")

    st.markdown("<br>", unsafe_allow_html=True)

    # Main query interface

    left, right = st.columns([1.65, 1], gap="large")

    with left:

        st.markdown("""
        <div class="panel">
            <div class="panel-title">✦ Ask Your Database</div>
            <div class="panel-caption">
                Describe what you want to find in simple English.
            </div>
        </div>
        """, unsafe_allow_html=True)

        with st.form("query_form"):

            question = st.text_area(
                "Natural language question",
                value=st.session_state.question,
                height=125,
                placeholder=(
                    "Example: What is the total profit?\n"
                    "Example: Which product generated the highest sales?"
                ),
                label_visibility="collapsed"
            )

            submitted = st.form_submit_button(
                "⚡  GENERATE SQL & EXECUTE QUERY",
                type="primary",
                use_container_width=True
            )

        if submitted:

            if not question.strip():
                st.warning("Please enter a question first.")

            else:
                try:
                    total_start = time.perf_counter()

                    with st.status(
                        "Processing your database question...",
                        expanded=True
                    ) as status:

                        st.write("01 · Sending question and schema to local AI")
                        sql = generate_sql(question)

                        st.write("02 · Validating and executing SQL query")
                        columns, rows = execute_sql(sql)

                        elapsed = time.perf_counter() - total_start

                        status.update(
                            label="Query executed successfully",
                            state="complete",
                            expanded=False
                        )

                    result = {
                        "question": question,
                        "sql": sql,
                        "columns": columns,
                        "rows": rows,
                        "time": elapsed,
                        "timestamp": datetime.now().strftime(
                            "%d %b %Y, %I:%M:%S %p"
                        )
                    }

                    st.session_state.last_result = result
                    st.session_state.query_history.insert(0, result)
                    st.session_state.question = ""

                except Exception as error:
                    st.error(f"Query execution failed: {error}")

    with right:

        st.markdown("""
        <div class="panel">
            <div class="panel-title">✧ Quick Intelligence</div>
            <div class="panel-caption">
                Explore your database with suggested questions.
            </div>
        </div>
        """, unsafe_allow_html=True)

        suggestions = [
            "What is the total profit?",
            "How many orders are there?",
            "What are the total sales for each region?",
            "Which product generated the highest total sales?",
            "Which payment method is used most frequently?",
            "Which customers have placed more than 5 orders?"
        ]

        for index, suggestion in enumerate(suggestions):

            if st.button(
                f"↗  {suggestion}",
                key=f"suggestion_{index}",
                use_container_width=True
            ):
                st.session_state.question = suggestion
                st.rerun()

        st.markdown("<br>", unsafe_allow_html=True)

        st.markdown("""
        <div class="panel">
            <div class="panel-title">AI ENGINE</div>
            <div style="color:#60A5FA; font-size:24px;
            font-weight:700; margin-top:10px;">
                Qwen 2.5 Coder
            </div>
            <div class="panel-caption">
                Running locally through Ollama
            </div>
        </div>
        """, unsafe_allow_html=True)

    # --------------------------------------------------
    # RESULTS SECTION
    # --------------------------------------------------

    result = st.session_state.last_result

    if result:

        st.markdown("---")

        st.markdown("""
        <div style="margin:20px 0;">
            <div style="color:#60A5FA; font-size:11px;
            letter-spacing:2px; font-weight:700;">
                QUERY OUTPUT
            </div>
            <h2>Intelligence Results</h2>
        </div>
        """, unsafe_allow_html=True)

        st.markdown(
            f"**Question:** {result['question']}"
        )

        st.markdown("""
        <div class="panel-title">01 / GENERATED SQL</div>
        """, unsafe_allow_html=True)

        st.code(result["sql"], language="sql")

        st.markdown("""
        <div class="panel-title">02 / EXECUTION SUMMARY</div>
        """, unsafe_allow_html=True)

        a, b, c = st.columns(3)

        with a:
            st.metric("Execution Status", "Success")

        with b:
            st.metric("Rows Returned", len(result["rows"]))

        with c:
            st.metric("Execution Time", f"{result['time']:.2f} sec")

        st.markdown("""
        <div class="panel-title">03 / RESULTS EXPLORER</div>
        """, unsafe_allow_html=True)

        if result["rows"]:

            df = pd.DataFrame(
                result["rows"],
                columns=result["columns"]
            )

            st.dataframe(
                df,
                use_container_width=True,
                hide_index=True
            )

            csv = df.to_csv(index=False).encode("utf-8")

            st.download_button(
                "⬇ Download Results as CSV",
                data=csv,
                file_name="sql_genius_results.csv",
                mime="text/csv"
            )

        else:
            st.info("The query executed successfully, but no matching records were found.")

        st.caption(
            f"Last executed: {result['timestamp']}"
        )


# --------------------------------------------------
# QUERY HISTORY
# --------------------------------------------------

elif page == "Query History":

    st.title("Query History")
    st.caption("Review your previous questions and generated SQL.")

    history = st.session_state.query_history

    if not history:
        st.info("No queries have been executed in this session yet.")

    else:
        st.write(f"**{len(history)} queries in this session**")

        for index, item in enumerate(history):

            with st.expander(
                f"{index + 1}. {item['question']}  ·  {item['timestamp']}"
            ):

                st.markdown("**Generated SQL**")
                st.code(item["sql"], language="sql")

                st.markdown("**Execution details**")
                st.write(f"Rows returned: {len(item['rows'])}")
                st.write(f"Execution time: {item['time']:.2f} seconds")

                if item["rows"]:
                    df = pd.DataFrame(
                        item["rows"],
                        columns=item["columns"]
                    )
                    st.dataframe(
                        df,
                        use_container_width=True,
                        hide_index=True
                    )

        if st.button("Clear Query History"):
            st.session_state.query_history = []
            st.session_state.last_result = None
            st.rerun()


# --------------------------------------------------
# DATABASE EXPLORER
# --------------------------------------------------

elif page == "Database Explorer":

    st.title("Database Explorer")
    st.caption("Explore the tables and column structures in your SQLite database.")

    try:
        schema = get_database_schema()

        st.markdown(f"**{len(schema)} database tables detected**")

        for table, columns in schema.items():

            with st.expander(f"▦  {table.upper()}  ·  {len(columns)} columns"):

                schema_df = pd.DataFrame(columns)

                st.dataframe(
                    schema_df,
                    use_container_width=True,
                    hide_index=True
                )

        st.markdown("---")
        st.subheader("Database Relationships")

        relationships = [
            "orders.customer_id → customers.customer_id",
            "payments.order_id → orders.order_id",
            "orders.product_name → products.product_name"
        ]

        for relationship in relationships:
            st.markdown(f"↳ `{relationship}`")

    except Exception as error:
        st.error(f"Could not load database schema: {error}")


# --------------------------------------------------
# FOOTER
# --------------------------------------------------

st.markdown("---")

st.markdown("""
<div style="text-align:center; padding:12px;">
    <div style="font-family:'Space Grotesk';
    color:#A5B4FC; font-weight:700; letter-spacing:2px;">
        NEXUS · SQL GENIUS
    </div>
    <div style="color:#64748B; font-size:11px; margin-top:6px;">
        Natural Language to SQL Intelligence · Powered by Local AI
    </div>
</div>
""", unsafe_allow_html=True)
