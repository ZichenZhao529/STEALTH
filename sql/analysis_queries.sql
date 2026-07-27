-- ============================================
-- 1. Company sustainability summary
-- ============================================

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

    AVG(sm.renewable_energy_pct) AS avg_renewable_energy_pct

FROM companies AS c

JOIN sustainability_metrics AS sm
    ON c.company_id = sm.company_id

GROUP BY
    c.company_id,
    c.company_name,
    c.industry,
    c.employees,
    c.annual_revenue_million;