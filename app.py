from pathlib import Path

import pandas as pd
import plotly.express as px
import streamlit as st


# ==================================================
# 1. Page configuration
# ==================================================

st.set_page_config(
    page_title="Sustainability Analytics Dashboard",
    page_icon="🌱",
    layout="wide",
    initial_sidebar_state="expanded",
)


# ==================================================
# 2. Styling
# ==================================================

st.markdown(
    """
    <style>
        .block-container {
            padding-top: 1.8rem;
            padding-bottom: 2rem;
        }

        h1 {
            font-size: 2.3rem !important;
            margin-bottom: 0.2rem !important;
        }

        h2, h3 {
            margin-top: 0.8rem !important;
        }

        [data-testid="stMetric"] {
            background-color: rgba(240, 242, 246, 0.65);
            border: 1px solid rgba(49, 51, 63, 0.12);
            border-radius: 12px;
            padding: 18px;
        }

        [data-testid="stMetricLabel"] {
            font-size: 0.95rem;
        }

        [data-testid="stSidebar"] {
            border-right: 1px solid rgba(49, 51, 63, 0.12);
        }

        .summary-card {
            border: 1px solid rgba(49, 51, 63, 0.12);
            border-radius: 12px;
            padding: 16px 18px;
            margin-bottom: 10px;
            background-color: rgba(240, 242, 246, 0.45);
        }

        .summary-title {
            font-size: 0.85rem;
            color: #68707c;
            margin-bottom: 4px;
        }

        .summary-value {
            font-size: 1.08rem;
            font-weight: 600;
        }
    </style>
    """,
    unsafe_allow_html=True,
)


# ==================================================
# 3. File paths
# ==================================================

BASE_DIR = Path(__file__).resolve().parent.parent

COMPANY_ANALYTICS_PATH = (
    BASE_DIR / "data" / "company_analytics.csv"
)

METRICS_PATH = (
    BASE_DIR / "data" / "sustainability_metrics.csv"
)

COMPANIES_PATH = (
    BASE_DIR / "data" / "companies.csv"
)


# ==================================================
# 4. Load data
# ==================================================

@st.cache_data
def load_data():
    company_analytics = pd.read_csv(
        COMPANY_ANALYTICS_PATH
    )

    monthly_metrics = pd.read_csv(
        METRICS_PATH
    )

    companies = pd.read_csv(
        COMPANIES_PATH
    )

    monthly_metrics = monthly_metrics.merge(
        companies[
            [
                "company_id",
                "company_name",
                "industry",
                "region",
            ]
        ],
        on="company_id",
        how="left",
    )

    monthly_metrics["period"] = pd.to_datetime(
        monthly_metrics["period"],
        errors="coerce",
    )

    return (
        company_analytics,
        monthly_metrics,
        companies,
    )


company_df, monthly_df, companies_df = load_data()


# ==================================================
# 5. Sidebar filters
# ==================================================

st.sidebar.title("Dashboard Filters")

industry_options = ["All"] + sorted(
    company_df["industry"]
    .dropna()
    .unique()
    .tolist()
)

selected_industry = st.sidebar.selectbox(
    "Industry",
    industry_options,
)

risk_options = ["All"] + sorted(
    company_df["risk_level"]
    .dropna()
    .unique()
    .tolist()
)

selected_risk = st.sidebar.selectbox(
    "Risk Level",
    risk_options,
)

company_options = ["All"] + sorted(
    company_df["company_name"]
    .dropna()
    .unique()
    .tolist()
)

selected_company = st.sidebar.selectbox(
    "Company",
    company_options,
)

st.sidebar.divider()

st.sidebar.caption(
    "Use the filters to compare portfolio companies "
    "and identify environmental risks."
)


# ==================================================
# 6. Apply filters
# ==================================================

filtered_company_df = company_df.copy()
filtered_monthly_df = monthly_df.copy()

if selected_industry != "All":
    filtered_company_df = filtered_company_df[
        filtered_company_df["industry"]
        == selected_industry
    ]

    filtered_monthly_df = filtered_monthly_df[
        filtered_monthly_df["industry"]
        == selected_industry
    ]

if selected_risk != "All":
    allowed_companies = filtered_company_df.loc[
        filtered_company_df["risk_level"]
        == selected_risk,
        "company_name",
    ]

    filtered_company_df = filtered_company_df[
        filtered_company_df["risk_level"]
        == selected_risk
    ]

    filtered_monthly_df = filtered_monthly_df[
        filtered_monthly_df["company_name"]
        .isin(allowed_companies)
    ]

if selected_company != "All":
    filtered_company_df = filtered_company_df[
        filtered_company_df["company_name"]
        == selected_company
    ]

    filtered_monthly_df = filtered_monthly_df[
        filtered_monthly_df["company_name"]
        == selected_company
    ]


# ==================================================
# 7. Dashboard heading
# ==================================================

st.title("🌱 Sustainability Analytics Dashboard")

st.caption(
    "Portfolio-level environmental performance, "
    "benchmarking, trend analysis, and risk monitoring"
)


if filtered_company_df.empty:
    st.warning(
        "No companies match the selected filters. "
        "Please adjust the sidebar selections."
    )
    st.stop()


# ==================================================
# 8. KPI calculations
# ==================================================

total_companies = (
    filtered_company_df["company_name"].nunique()
)

average_score = (
    filtered_company_df["sustainability_score"].mean()
)

high_risk_count = (
    filtered_company_df["risk_level"]
    .eq("High Risk")
    .sum()
)

average_renewable = (
    filtered_company_df[
        "avg_renewable_energy_pct"
    ].mean()
)

total_emissions = (
    filtered_company_df["total_emissions"].sum()
)


# ==================================================
# 9. KPI cards
# ==================================================

kpi1, kpi2, kpi3, kpi4, kpi5 = st.columns(5)

kpi1.metric(
    label="Portfolio Companies",
    value=f"{total_companies}",
)

kpi2.metric(
    label="Average Score",
    value=f"{average_score:.1f}",
)

kpi3.metric(
    label="High-Risk Companies",
    value=f"{high_risk_count}",
)

kpi4.metric(
    label="Renewable Energy",
    value=f"{average_renewable:.1f}%",
)

kpi5.metric(
    label="Total Emissions",
    value=f"{total_emissions:,.0f} t",
)


# ==================================================
# 10. Executive summary
# ==================================================

st.subheader("Executive Summary")

best_company = filtered_company_df.loc[
    filtered_company_df[
        "sustainability_score"
    ].idxmax()
]

lowest_company = filtered_company_df.loc[
    filtered_company_df[
        "sustainability_score"
    ].idxmin()
]

largest_reduction = filtered_company_df.loc[
    filtered_company_df[
        "carbon_change_pct"
    ].idxmin()
]

highest_emitter = filtered_company_df.loc[
    filtered_company_df[
        "total_emissions"
    ].idxmax()
]


summary1, summary2, summary3, summary4 = st.columns(4)

with summary1:
    st.markdown(
        f"""
        <div class="summary-card">
            <div class="summary-title">
                Top Sustainability Performer
            </div>
            <div class="summary-value">
                {best_company["company_name"]}
            </div>
            <div>
                Score: {best_company["sustainability_score"]:.1f}
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

with summary2:
    st.markdown(
        f"""
        <div class="summary-card">
            <div class="summary-title">
                Company Requiring Attention
            </div>
            <div class="summary-value">
                {lowest_company["company_name"]}
            </div>
            <div>
                Score: {lowest_company["sustainability_score"]:.1f}
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

with summary3:
    st.markdown(
        f"""
        <div class="summary-card">
            <div class="summary-title">
                Largest Carbon Reduction
            </div>
            <div class="summary-value">
                {largest_reduction["company_name"]}
            </div>
            <div>
                Change: {largest_reduction["carbon_change_pct"]:.1f}%
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

with summary4:
    st.markdown(
        f"""
        <div class="summary-card">
            <div class="summary-title">
                Highest Total Emissions
            </div>
            <div class="summary-value">
                {highest_emitter["company_name"]}
            </div>
            <div>
                {highest_emitter["total_emissions"]:,.0f} tons
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


st.divider()


# ==================================================
# 11. Ranking and emissions charts
# ==================================================

chart_col1, chart_col2 = st.columns(2)

with chart_col1:
    st.subheader("Sustainability Score Ranking")

    ranking_df = filtered_company_df.sort_values(
        "sustainability_score",
        ascending=True,
    )

    ranking_chart = px.bar(
        ranking_df,
        x="sustainability_score",
        y="company_name",
        orientation="h",
        color="risk_level",
        color_discrete_map={
            "Low Risk": "#2E8B57",
            "Medium Risk": "#E6A700",
            "High Risk": "#C74440",
        },
        labels={
            "sustainability_score":
                "Sustainability Score",
            "company_name": "",
            "risk_level": "Risk Level",
        },
        hover_data={
            "industry": True,
            "carbon_change_pct": ":.1f",
            "avg_renewable_energy_pct": ":.1f",
        },
    )

    ranking_chart.update_layout(
        xaxis_range=[0, 100],
        legend_title_text="Risk",
        margin=dict(
            l=10,
            r=10,
            t=20,
            b=10,
        ),
    )

    st.plotly_chart(
        ranking_chart,
        use_container_width=True,
    )


with chart_col2:
    st.subheader("Carbon Emissions by Company")

    emissions_df = filtered_company_df.sort_values(
        "total_emissions",
        ascending=False,
    )

    emissions_chart = px.bar(
        emissions_df,
        x="company_name",
        y="total_emissions",
        color="industry",
        labels={
            "company_name": "",
            "total_emissions":
                "Total Emissions (tons)",
            "industry": "Industry",
        },
        hover_data={
            "emissions_intensity": ":.2f",
            "risk_level": True,
            "sustainability_score": ":.1f",
        },
    )

    emissions_chart.update_layout(
        xaxis_tickangle=-35,
        margin=dict(
            l=10,
            r=10,
            t=20,
            b=10,
        ),
    )

    st.plotly_chart(
        emissions_chart,
        use_container_width=True,
    )


# ==================================================
# 12. Monthly carbon trend
# ==================================================

st.subheader("Monthly Carbon Emissions Trend")

trend_df = (
    filtered_monthly_df
    .dropna(subset=["period"])
    .sort_values(
        ["company_name", "period"]
    )
)

carbon_trend_chart = px.line(
    trend_df,
    x="period",
    y="carbon_emissions_tons",
    color="company_name",
    markers=True,
    labels={
        "period": "Reporting Period",
        "carbon_emissions_tons":
            "Carbon Emissions (tons)",
        "company_name": "Company",
    },
    hover_data={
        "industry": True,
        "energy_consumption_mwh": ":.1f",
        "renewable_energy_pct": ":.1f",
    },
)

carbon_trend_chart.update_layout(
    legend_title_text="Company",
    hovermode="x unified",
    margin=dict(
        l=10,
        r=10,
        t=20,
        b=10,
    ),
)

st.plotly_chart(
    carbon_trend_chart,
    use_container_width=True,
)


# ==================================================
# 13. Renewable energy and carbon change
# ==================================================

comparison_col1, comparison_col2 = st.columns(2)

with comparison_col1:
    st.subheader("Renewable Energy Adoption")

    renewable_df = filtered_company_df.sort_values(
        "avg_renewable_energy_pct",
        ascending=True,
    )

    renewable_chart = px.bar(
        renewable_df,
        x="avg_renewable_energy_pct",
        y="company_name",
        orientation="h",
        labels={
            "avg_renewable_energy_pct":
                "Average Renewable Energy (%)",
            "company_name": "",
        },
        hover_data={
            "industry": True,
            "sustainability_score": ":.1f",
        },
    )

    renewable_chart.update_layout(
        xaxis_range=[0, 100],
        margin=dict(
            l=10,
            r=10,
            t=20,
            b=10,
        ),
    )

    st.plotly_chart(
        renewable_chart,
        use_container_width=True,
    )


with comparison_col2:
    st.subheader("Carbon Change by Company")

    carbon_change_df = (
        filtered_company_df.sort_values(
            "carbon_change_pct",
            ascending=True,
        )
    )

    carbon_change_df["trend_status"] = (
        carbon_change_df[
            "carbon_change_pct"
        ].apply(
            lambda value:
                "Improving"
                if value < 0
                else "Increasing"
        )
    )

    carbon_change_chart = px.bar(
        carbon_change_df,
        x="carbon_change_pct",
        y="company_name",
        orientation="h",
        color="trend_status",
        color_discrete_map={
            "Improving": "#2E8B57",
            "Increasing": "#C74440",
        },
        labels={
            "carbon_change_pct":
                "Carbon Change (%)",
            "company_name": "",
            "trend_status": "Trend",
        },
        hover_data={
            "industry": True,
            "risk_level": True,
        },
    )

    carbon_change_chart.add_vline(
        x=0,
        line_dash="dash",
        line_color="gray",
    )

    carbon_change_chart.update_layout(
        margin=dict(
            l=10,
            r=10,
            t=20,
            b=10,
        ),
    )

    st.plotly_chart(
        carbon_change_chart,
        use_container_width=True,
    )


st.divider()


# ==================================================
# 14. Risk monitor
# ==================================================

st.subheader("Environmental Risk Monitor")

risk_table = filtered_company_df[
    [
        "company_name",
        "industry",
        "sustainability_score",
        "risk_level",
        "carbon_change_pct",
        "emissions_intensity",
        "energy_intensity",
        "avg_renewable_energy_pct",
    ]
].copy()

risk_table["risk_level"] = (
    risk_table["risk_level"].replace(
        {
            "Low Risk": "🟢 Low Risk",
            "Medium Risk": "🟡 Medium Risk",
            "High Risk": "🔴 High Risk",
        }
    )
)

risk_table = risk_table.rename(
    columns={
        "company_name": "Company",
        "industry": "Industry",
        "sustainability_score": "Score",
        "risk_level": "Risk Level",
        "carbon_change_pct": "Carbon Change %",
        "emissions_intensity":
            "Emissions Intensity",
        "energy_intensity":
            "Energy Intensity",
        "avg_renewable_energy_pct":
            "Renewable Energy %",
    }
)

risk_priority = {
    "🔴 High Risk": 1,
    "🟡 Medium Risk": 2,
    "🟢 Low Risk": 3,
}

risk_table["Risk Priority"] = (
    risk_table["Risk Level"]
    .map(risk_priority)
)

risk_table = (
    risk_table
    .sort_values(
        ["Risk Priority", "Score"],
        ascending=[True, True],
    )
    .drop(columns="Risk Priority")
)

st.dataframe(
    risk_table,
    use_container_width=True,
    hide_index=True,
    column_config={
        "Score": st.column_config.NumberColumn(
            format="%.1f"
        ),
        "Carbon Change %":
            st.column_config.NumberColumn(
                format="%.1f%%"
            ),
        "Emissions Intensity":
            st.column_config.NumberColumn(
                format="%.2f"
            ),
        "Energy Intensity":
            st.column_config.NumberColumn(
                format="%.2f"
            ),
        "Renewable Energy %":
            st.column_config.NumberColumn(
                format="%.1f%%"
            ),
    },
)


# ==================================================
# 15. Full datasets
# ==================================================

with st.expander(
    "View Full Portfolio Analytics Data"
):
    st.dataframe(
        filtered_company_df,
        use_container_width=True,
        hide_index=True,
    )

with st.expander(
    "View Monthly Sustainability Records"
):
    st.dataframe(
        filtered_monthly_df.sort_values(
            ["company_name", "period"]
        ),
        use_container_width=True,
        hide_index=True,
    )


# ==================================================
# 16. Footer
# ==================================================

st.caption(
    "Prototype dashboard based on mock portfolio "
    "company sustainability data. Sustainability "
    "scores and risk levels are internal analytical "
    "measures rather than official ESG ratings."
)