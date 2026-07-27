DROP TABLE IF EXISTS sustainability_metrics;
DROP TABLE IF EXISTS industry_benchmarks;
DROP TABLE IF EXISTS companies;


CREATE TABLE companies (
    company_id TEXT PRIMARY KEY,
    company_name TEXT NOT NULL,
    industry TEXT NOT NULL,
    founded_year INTEGER,
    employees INTEGER,
    annual_revenue_million REAL,
    region TEXT
);


CREATE TABLE industry_benchmarks (
    industry TEXT PRIMARY KEY,
    emissions_intensity_benchmark REAL NOT NULL,
    energy_intensity_benchmark REAL NOT NULL,
    water_intensity_benchmark REAL NOT NULL
);


CREATE TABLE sustainability_metrics (
    metric_id INTEGER PRIMARY KEY,
    company_id TEXT NOT NULL,
    period TEXT NOT NULL,
    energy_consumption_mwh REAL NOT NULL,
    carbon_emissions_tons REAL NOT NULL,
    water_usage_cubic_m REAL NOT NULL,
    waste_output_tons REAL NOT NULL,
    renewable_energy_pct REAL NOT NULL,

    FOREIGN KEY (company_id)
        REFERENCES companies(company_id),

    UNIQUE (company_id, period)
);