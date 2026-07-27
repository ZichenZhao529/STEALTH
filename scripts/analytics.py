import os
import sqlite3

import numpy as np
import pandas as pd


# --------------------------------------------------
# 1. Define project paths
# --------------------------------------------------

BASE_DIR = os.path.dirname(
    os.path.dirname(os.path.abspath(__file__))
)

DATABASE_PATH = os.path.join(
    BASE_DIR,
    "database",
    "sustainability.db",
)

OUTPUT_PATH = os.path.join(
    BASE_DIR,
    "data",
    "company_analytics.csv",
)


# --------------------------------------------------
# 2. Connect to database
# --------------------------------------------------

connection = sqlite3.connect(DATABASE_PATH)


# --------------------------------------------------
# 3. Load company sustainability summary
# --------------------------------------------------

summary_query = """
SELECT
    c.company_id,
    c.company_name,
    c.industry,
    c.employees,
    c.annual_revenue_million,

    SUM(sm.carbon_emissions_tons) AS total_emissions,

    SUM(sm.energy_consumption_mwh) AS total_energy,

    SUM(sm.water_usage_cubic_m) AS total_water_usage,

    SUM(sm.waste_output_tons) AS total_waste_output,

    AVG(sm.renewable_energy_pct)
        AS avg_renewable_energy_pct

FROM companies AS c

JOIN sustainability_metrics AS sm
    ON c.company_id = sm.company_id

GROUP BY
    c.company_id,
    c.company_name,
    c.industry,
    c.employees,
    c.annual_revenue_million;
"""


analytics = pd.read_sql_query(
    summary_query,
    connection,
)


print("Company summary loaded successfully.")


# --------------------------------------------------
# 4. Calculate intensity metrics
# --------------------------------------------------

analytics["emissions_intensity"] = (
    analytics["total_emissions"]
    / analytics["annual_revenue_million"]
)

analytics["energy_intensity"] = (
    analytics["total_energy"]
    / analytics["annual_revenue_million"]
)

analytics["water_intensity"] = (
    analytics["total_water_usage"]
    / analytics["annual_revenue_million"]
)


# --------------------------------------------------
# 5. Calculate carbon change over time
# --------------------------------------------------

trend_query = """
SELECT
    company_id,
    period,
    carbon_emissions_tons

FROM sustainability_metrics

ORDER BY
    company_id,
    period;
"""


trend_data = pd.read_sql_query(
    trend_query,
    connection,
)


carbon_change = (
    trend_data
    .groupby("company_id")
    .agg(
        first_emissions=(
            "carbon_emissions_tons",
            "first",
        ),
        latest_emissions=(
            "carbon_emissions_tons",
            "last",
        ),
    )
    .reset_index()
)


carbon_change["carbon_change_pct"] = (
    (
        carbon_change["latest_emissions"]
        - carbon_change["first_emissions"]
    )
    / carbon_change["first_emissions"]
    * 100
)


analytics = analytics.merge(
    carbon_change[
        [
            "company_id",
            "carbon_change_pct",
        ]
    ],
    on="company_id",
    how="left",
)


# --------------------------------------------------
# 6. Load industry benchmarks
# --------------------------------------------------

benchmarks = pd.read_sql_query(
    """
    SELECT *
    FROM industry_benchmarks;
    """,
    connection,
)


analytics = analytics.merge(
    benchmarks,
    on="industry",
    how="left",
)


# --------------------------------------------------
# 7. Compare companies with industry benchmarks
# --------------------------------------------------

analytics["emissions_vs_benchmark"] = (
    analytics["emissions_intensity"]
    / analytics["emissions_intensity_benchmark"]
)

analytics["energy_vs_benchmark"] = (
    analytics["energy_intensity"]
    / analytics["energy_intensity_benchmark"]
)

analytics["water_vs_benchmark"] = (
    analytics["water_intensity"]
    / analytics["water_intensity_benchmark"]
)


# --------------------------------------------------
# 8. Normalize sustainability metrics
# --------------------------------------------------

def normalize_inverse(series):
    minimum = series.min()
    maximum = series.max()

    if maximum == minimum:
        return pd.Series(
            100,
            index=series.index,
        )

    return (
        1
        - (
            (series - minimum)
            / (maximum - minimum)
        )
    ) * 100


def normalize_positive(series):
    minimum = series.min()
    maximum = series.max()

    if maximum == minimum:
        return pd.Series(
            100,
            index=series.index,
        )

    return (
        (series - minimum)
        / (maximum - minimum)
    ) * 100


analytics["emissions_score"] = normalize_inverse(
    analytics["emissions_vs_benchmark"]
)

analytics["energy_score"] = normalize_inverse(
    analytics["energy_vs_benchmark"]
)

analytics["water_score"] = normalize_inverse(
    analytics["water_vs_benchmark"]
)

analytics["renewable_score"] = normalize_positive(
    analytics["avg_renewable_energy_pct"]
)

analytics["waste_score"] = normalize_inverse(
    analytics["total_waste_output"]
)


# --------------------------------------------------
# 9. Calculate sustainability score
# --------------------------------------------------

analytics["sustainability_score"] = (
    analytics["emissions_score"] * 0.30
    + analytics["renewable_score"] * 0.25
    + analytics["energy_score"] * 0.20
    + analytics["water_score"] * 0.15
    + analytics["waste_score"] * 0.10
)


# --------------------------------------------------
# 10. Assign risk level
# --------------------------------------------------

def assign_risk(score):

    if score >= 80:
        return "Low Risk"

    elif score >= 60:
        return "Medium Risk"

    else:
        return "High Risk"


analytics["risk_level"] = (
    analytics["sustainability_score"]
    .apply(assign_risk)
)


# --------------------------------------------------
# 11. Create sustainability ranking
# --------------------------------------------------

analytics["sustainability_rank"] = (
    analytics["sustainability_score"]
    .rank(
        ascending=False,
        method="dense",
    )
    .astype(int)
)


# --------------------------------------------------
# 12. Round numeric columns
# --------------------------------------------------

numeric_columns = analytics.select_dtypes(
    include=np.number
).columns


analytics[numeric_columns] = (
    analytics[numeric_columns]
    .round(2)
)


# --------------------------------------------------
# 13. Sort companies by sustainability ranking
# --------------------------------------------------

analytics = analytics.sort_values(
    "sustainability_rank"
)


# --------------------------------------------------
# 14. Save analytics output
# --------------------------------------------------

analytics.to_csv(
    OUTPUT_PATH,
    index=False,
)


# --------------------------------------------------
# 15. Display key results
# --------------------------------------------------

print("\nSustainability Analytics Results:\n")

print(
    analytics[
        [
            "company_name",
            "industry",
            "carbon_change_pct",
            "sustainability_score",
            "risk_level",
            "sustainability_rank",
        ]
    ].to_string(index=False)
)


print(
    "\nAnalytics file created successfully:"
)

print(OUTPUT_PATH)


# --------------------------------------------------
# 16. Close database connection
# --------------------------------------------------

connection.close()