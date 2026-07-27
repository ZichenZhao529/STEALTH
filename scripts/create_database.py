import os
import sqlite3

import pandas as pd


# --------------------------------------------------
# 1. Define project paths
# --------------------------------------------------

BASE_DIR = os.path.dirname(
    os.path.dirname(os.path.abspath(__file__))
)

DATA_DIR = os.path.join(BASE_DIR, "data")
DATABASE_DIR = os.path.join(BASE_DIR, "database")
SQL_DIR = os.path.join(BASE_DIR, "sql")

DATABASE_PATH = os.path.join(
    DATABASE_DIR,
    "sustainability.db",
)

SCHEMA_PATH = os.path.join(
    SQL_DIR,
    "create_tables.sql",
)


# --------------------------------------------------
# 2. Create database directory
# --------------------------------------------------

os.makedirs(
    DATABASE_DIR,
    exist_ok=True,
)


# --------------------------------------------------
# 3. Connect to SQLite database
# --------------------------------------------------

connection = sqlite3.connect(DATABASE_PATH)

connection.execute("PRAGMA foreign_keys = ON;")


# --------------------------------------------------
# 4. Create database tables
# --------------------------------------------------

with open(
    SCHEMA_PATH,
    "r",
    encoding="utf-8",
) as sql_file:

    schema_sql = sql_file.read()

connection.executescript(schema_sql)


# --------------------------------------------------
# 5. Load CSV data
# --------------------------------------------------

companies = pd.read_csv(
    os.path.join(
        DATA_DIR,
        "companies.csv",
    )
)

sustainability_metrics = pd.read_csv(
    os.path.join(
        DATA_DIR,
        "sustainability_metrics.csv",
    )
)

industry_benchmarks = pd.read_csv(
    os.path.join(
        DATA_DIR,
        "industry_benchmarks.csv",
    )
)


# --------------------------------------------------
# 6. Insert company data
# --------------------------------------------------

companies.to_sql(
    "companies",
    connection,
    if_exists="append",
    index=False,
)


# --------------------------------------------------
# 7. Insert industry benchmark data
# --------------------------------------------------

industry_benchmarks.to_sql(
    "industry_benchmarks",
    connection,
    if_exists="append",
    index=False,
)


# --------------------------------------------------
# 8. Insert sustainability metrics
# --------------------------------------------------

sustainability_metrics.to_sql(
    "sustainability_metrics",
    connection,
    if_exists="append",
    index=False,
)


# --------------------------------------------------
# 9. Commit changes
# --------------------------------------------------

connection.commit()


# --------------------------------------------------
# 10. Validate database tables
# --------------------------------------------------

tables = pd.read_sql_query(
    """
    SELECT name
    FROM sqlite_master
    WHERE type = 'table'
    ORDER BY name;
    """,
    connection,
)

print("\nDatabase tables:")
print(tables)


company_count = pd.read_sql_query(
    """
    SELECT COUNT(*) AS row_count
    FROM companies;
    """,
    connection,
)

metrics_count = pd.read_sql_query(
    """
    SELECT COUNT(*) AS row_count
    FROM sustainability_metrics;
    """,
    connection,
)

benchmark_count = pd.read_sql_query(
    """
    SELECT COUNT(*) AS row_count
    FROM industry_benchmarks;
    """,
    connection,
)


print("\nRow counts:")

print(
    "Companies:",
    company_count.iloc[0]["row_count"],
)

print(
    "Sustainability metrics:",
    metrics_count.iloc[0]["row_count"],
)

print(
    "Industry benchmarks:",
    benchmark_count.iloc[0]["row_count"],
)


# --------------------------------------------------
# 11. Close database connection
# --------------------------------------------------

connection.close()


print(
    "\nSQLite database created successfully:"
)

print(DATABASE_PATH)