import streamlit as st
import pandas as pd
import plotly.express as px

# -----------------------------
# Page Config
# -----------------------------
st.set_page_config(
    page_title="Ethiopia Financial Inclusion Dashboard",
    layout="wide"
)

st.title("📊 Ethiopia Financial Inclusion Dashboard")

# -----------------------------
# Load Data
# -----------------------------
@st.cache_data
def load_data():

    fi = pd.read_excel("data/raw/ethiopia_fi_unified_data.xlsx")
    forecast = pd.read_csv("reports/forecast_results.csv")

    fi["observation_date"] = pd.to_datetime(fi["observation_date"])

    return fi, forecast


fi_data, forecast_data = load_data()


# -----------------------------
# Targets (Policy Goals)
# -----------------------------
TARGETS = {
    "ACC_OWNERSHIP": 80,
    "ACC_FAYDA": 70
}


# -----------------------------
# Sidebar Filters
# -----------------------------
st.sidebar.header("🔍 Filters")

indicator = st.sidebar.selectbox(
    "Select Indicator",
    sorted(fi_data["indicator_code"].unique())
)

start_date = st.sidebar.date_input(
    "Start Date",
    fi_data["observation_date"].min()
)

end_date = st.sidebar.date_input(
    "End Date",
    fi_data["observation_date"].max()
)


# -----------------------------
# Filter Data
# -----------------------------
filtered = fi_data[
    (fi_data["indicator_code"] == indicator) &
    (fi_data["observation_date"] >= pd.to_datetime(start_date)) &
    (fi_data["observation_date"] <= pd.to_datetime(end_date))
]


# -----------------------------
# Overview Metrics
# -----------------------------
st.subheader("📌 Key Metrics")

latest = filtered.sort_values("observation_date").tail(1)

if not latest.empty:

    latest_value = latest["value_numeric"].values[0]
    latest_date = latest["observation_date"].dt.year.values[0]

    forecast_val = forecast_data[
        forecast_data["indicator"] == indicator
    ]["forecast_2030"]

    forecast_2030 = (
        forecast_val.values[0]
        if not forecast_val.empty else None
    )

    target = TARGETS.get(indicator, None)

    col1, col2, col3, col4 = st.columns(4)

    col1.metric("Latest Value", f"{latest_value:.2f}")
    col2.metric("Latest Year", latest_date)

    if forecast_2030:
        col3.metric("2030 Forecast", f"{forecast_2030:.2f}")

    if target:
        gap = forecast_2030 - target if forecast_2030 else 0
        col4.metric("Target Gap", f"{gap:.2f}")


# -----------------------------
# Time Series Plot
# -----------------------------
st.subheader("📈 Indicator Trend")

fig1 = px.line(
    filtered,
    x="observation_date",
    y="value_numeric",
    title=f"{indicator} Over Time",
    markers=True
)

st.plotly_chart(fig1, use_container_width=True)


# -----------------------------
# Channel Comparison
# -----------------------------
st.subheader("📊 Channel Comparison")

if "source_name" in fi_data.columns:

    channel_data = filtered.groupby(
        ["observation_date", "source_name"]
    )["value_numeric"].mean().reset_index()

    fig2 = px.line(
        channel_data,
        x="observation_date",
        y="value_numeric",
        color="source_name",
        title="By Channel"
    )

    st.plotly_chart(fig2, use_container_width=True)


# -----------------------------
# Event Impact View
# -----------------------------
st.subheader("⚡ Event Impact")

events = fi_data[fi_data["record_type"] == "event"]

if not events.empty:

    event_counts = events["indicator_code"].value_counts().reset_index()
    event_counts.columns = ["Indicator", "Event Count"]

    fig3 = px.bar(
        event_counts,
        x="Indicator",
        y="Event Count",
        title="Events per Indicator"
    )

    st.plotly_chart(fig3, use_container_width=True)


# -----------------------------
# Forecast Section
# -----------------------------
st.subheader("🔮 Forecast Projections")

forecast_sel = forecast_data[
    forecast_data["indicator"] == indicator
]

if not forecast_sel.empty:

    scenarios = pd.DataFrame({
        "Scenario": ["Low", "Medium", "High"],
        "Value": [
            forecast_sel["forecast_2030"].values[0] * 0.9,
            forecast_sel["forecast_2030"].values[0],
            forecast_sel["forecast_2030"].values[0] * 1.1
        ]
    })

    fig4 = px.bar(
        scenarios,
        x="Scenario",
        y="Value",
        title="Forecast Scenarios"
    )

    st.plotly_chart(fig4, use_container_width=True)


# -----------------------------
# Regional Comparison
# -----------------------------
st.subheader("🌍 Regional Comparison")

if "region" in fi_data.columns:

    region_data = filtered.groupby("region")["value_numeric"].mean().reset_index()

    fig5 = px.bar(
        region_data,
        x="region",
        y="value_numeric",
        title="By Region"
    )

    st.plotly_chart(fig5, use_container_width=True)


# -----------------------------
# Data Preview
# -----------------------------
st.subheader("📄 Raw Data Preview")

st.dataframe(filtered)
