import os

import numpy as np
import pandas as pd


# Set random seed so the generated dataset is reproducible
np.random.seed(42)


# --------------------------------------------------
# 1. Define output path
# --------------------------------------------------

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(BASE_DIR, "data")

os.makedirs(DATA_DIR, exist_ok=True)


# --------------------------------------------------
# 2. Create company data
# --------------------------------------------------

companies = pd.DataFrame(
    {
        "company_id": [
            "C001",
            "C002",
            "C003",
            "C004",
            "C005",
            "C006",
            "C007",
            "C008",
            "C009",
            "C010",
        ],
        "company_name": [
            "GreenByte AI",
            "NovaFoods",
            "UrbanLogix",
            "EcoForge",
            "BlueWave Health",
            "TerraRetail",
            "SolarNest",
            "PureHarvest",
            "NextGrid Systems",
            "CircularWorks",
        ],
        "industry": [
            "Technology",
            "Food",
            "Logistics",
            "Manufacturing",
            "Healthcare",
            "Retail",
            "Energy",
            "Food",
            "Technology",
            "Manufacturing",
        ],
        "founded_year": [
            2018,
            2012,
            2015,
            2008,
            2017,
            2010,
            2019,
            2014,
            2020,
            2011,
        ],
        "employees": [
            420,
            850,
            650,
            1200,
            530,
            900,
            310,
            720,
            280,
            1050,
        ],
        "annual_revenue_million": [
            85,
            160,
            140,
            280,
            120,
            210,
            75,
            150,
            65,
            240,
        ],
        "region": [
            "North America",
            "North America",
            "Europe",
            "Asia",
            "North America",
            "Europe",
            "Asia",
            "North America",
            "Europe",
            "Asia",
        ],
    }
)


# --------------------------------------------------
# 3. Industry assumptions
# --------------------------------------------------

industry_profiles = {
    "Technology": {
        "energy": 900,
        "emissions": 300,
        "water": 1500,
        "waste": 20,
        "renewable": 55,
    },
    "Food": {
        "energy": 2200,
        "emissions": 900,
        "water": 12000,
        "waste": 180,
        "renewable": 30,
    },
    "Logistics": {
        "energy": 2800,
        "emissions": 1500,
        "water": 3000,
        "waste": 80,
        "renewable": 20,
    },
    "Manufacturing": {
        "energy": 4000,
        "emissions": 1900,
        "water": 9000,
        "waste": 250,
        "renewable": 25,
    },
    "Healthcare": {
        "energy": 1800,
        "emissions": 650,
        "water": 6000,
        "waste": 110,
        "renewable": 40,
    },
    "Retail": {
        "energy": 1500,
        "emissions": 550,
        "water": 3500,
        "waste": 100,
        "renewable": 35,
    },
    "Energy": {
        "energy": 3500,
        "emissions": 1200,
        "water": 7000,
        "waste": 140,
        "renewable": 65,
    },
}


# --------------------------------------------------
# 4. Generate monthly sustainability metrics
# --------------------------------------------------

periods = pd.date_range(
    start="2025-01-01",
    periods=12,
    freq="MS",
)

metrics_data = []

metric_id = 1

for _, company in companies.iterrows():

    profile = industry_profiles[company["industry"]]

    # Each company gets a slightly different sustainability trend
    company_trend = np.random.uniform(-0.02, 0.015)

    renewable_growth = np.random.uniform(0.2, 1.2)

    for month_index, period in enumerate(periods):

        trend_factor = 1 + company_trend * month_index

        energy = (
            profile["energy"]
            * trend_factor
            * np.random.normal(1, 0.05)
        )

        emissions = (
            profile["emissions"]
            * trend_factor
            * np.random.normal(1, 0.06)
        )

        water = (
            profile["water"]
            * trend_factor
            * np.random.normal(1, 0.05)
        )

        waste = (
            profile["waste"]
            * trend_factor
            * np.random.normal(1, 0.07)
        )

        renewable_pct = (
            profile["renewable"]
            + renewable_growth * month_index
            + np.random.normal(0, 2)
        )

        renewable_pct = np.clip(
            renewable_pct,
            0,
            100,
        )

        metrics_data.append(
            {
                "metric_id": metric_id,
                "company_id": company["company_id"],
                "period": period.strftime("%Y-%m"),
                "energy_consumption_mwh": round(energy, 2),
                "carbon_emissions_tons": round(emissions, 2),
                "water_usage_cubic_m": round(water, 2),
                "waste_output_tons": round(waste, 2),
                "renewable_energy_pct": round(renewable_pct, 2),
            }
        )

        metric_id += 1


sustainability_metrics = pd.DataFrame(metrics_data)


# --------------------------------------------------
# 5. Create industry benchmark data
# --------------------------------------------------

industry_benchmarks = pd.DataFrame(
    {
        "industry": [
            "Technology",
            "Food",
            "Logistics",
            "Manufacturing",
            "Healthcare",
            "Retail",
            "Energy",
        ],
        "emissions_intensity_benchmark": [
            5,
            8,
            12,
            10,
            6,
            5,
            9,
        ],
        "energy_intensity_benchmark": [
            18,
            22,
            25,
            24,
            20,
            17,
            28,
        ],
        "water_intensity_benchmark": [
            25,
            80,
            35,
            55,
            40,
            30,
            50,
        ],
    }
)


# --------------------------------------------------
# 6. Save CSV files
# --------------------------------------------------

companies.to_csv(
    os.path.join(DATA_DIR, "companies.csv"),
    index=False,
)

sustainability_metrics.to_csv(
    os.path.join(DATA_DIR, "sustainability_metrics.csv"),
    index=False,
)

industry_benchmarks.to_csv(
    os.path.join(DATA_DIR, "industry_benchmarks.csv"),
    index=False,
)


print("Mock sustainability data generated successfully.")

print(f"Companies: {companies.shape}")
print(
    f"Sustainability metrics: "
    f"{sustainability_metrics.shape}"
)
print(
    f"Industry benchmarks: "
    f"{industry_benchmarks.shape}"
)