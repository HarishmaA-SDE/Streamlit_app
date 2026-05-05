import streamlit as st
import pandas as pd
import plotly.express as px

# Page config
st.set_page_config(
    page_title="Transformer Dashboard",
    layout="wide",
    page_icon="⚡"
)

# Title
st.markdown("## ⚡ Transformer Health Monitoring Dashboard")

# File upload
uploaded_file = st.sidebar.file_uploader(
    "Upload CSV / Excel",
    type=["csv", "xlsx"]
)

def load_data(file):
    if file.name.endswith(".csv"):
        return pd.read_csv(file)
    else:
        return pd.read_excel(file)

if uploaded_file:
    df = load_data(uploaded_file)

    # Preprocessing
    df["Time"] = pd.to_datetime(df["Time"])
    df = df.sort_values("Time")

    # Sidebar filters
    st.sidebar.markdown("### 🔍 Filters")

    start_time = st.sidebar.date_input("Start Date", df["Time"].min())
    end_time = st.sidebar.date_input("End Date", df["Time"].max())

    df = df[
        (df["Time"] >= pd.to_datetime(start_time)) &
        (df["Time"] <= pd.to_datetime(end_time))
    ]

    # Feature Engineering
    df["Temp Diff"] = df["Winding Temp (°C)"] - df["Oil Temp (°C)"]

    # ===== KPI SECTION =====
    st.markdown("### 📊 Key Metrics")

    col1, col2, col3, col4 = st.columns(4)

    col1.metric("⚡ Max Voltage", f"{df['Voltage (kV)'].max():.2f} kV")
    col2.metric("🔌 Max Current", f"{df['Current (A)'].max()} A")
    col3.metric("🌡️ Max Winding Temp", f"{df['Winding Temp (°C)'].max()} °C")
    col4.metric("📉 Avg Temp Diff", f"{df['Temp Diff'].mean():.2f} °C")

    st.divider()

    # ===== CHARTS =====
    st.markdown("### 📈 Trends")

    col1, col2 = st.columns(2)

    with col1:
        fig_v = px.line(df, x="Time", y="Voltage (kV)", title="Voltage Trend")
        st.plotly_chart(fig_v, use_container_width=True)

    with col2:
        fig_c = px.line(df, x="Time", y="Current (A)", title="Current Trend")
        st.plotly_chart(fig_c, use_container_width=True)

    col3, col4 = st.columns(2)

    with col3:
        fig_temp = px.line(
            df,
            x="Time",
            y=["Oil Temp (°C)", "Winding Temp (°C)"],
            title="Temperature Trends"
        )
        st.plotly_chart(fig_temp, use_container_width=True)

    with col4:
        fig_diff = px.line(df, x="Time", y="Temp Diff", title="Temp Difference")
        st.plotly_chart(fig_diff, use_container_width=True)

    st.divider()

    # ===== STATUS =====
    st.markdown("### 📊 Status Overview")

    col1, col2 = st.columns([2, 1])

    with col1:
   
        status_counts = df["Status"].value_counts().reset_index()
        status_counts.columns = ["Status", "Count"]

        fig_status = px.bar(
            status_counts,
            x="Status",
            y="Count",
            title="Status Distribution"
        )

    st.plotly_chart(fig_status, use_container_width=True)

    with col2:
        st.markdown("### ⚠️ Alerts")

        if (df["Winding Temp (°C)"] > 90).any():
            st.error("High Winding Temperature!")

        if (df["Current (A)"] > 100).any():
            st.warning("High Current detected!")

        if not (
            (df["Winding Temp (°C)"] > 90).any() or
            (df["Current (A)"] > 100).any()
        ):
            st.success("All systems normal ✅")

    st.divider()

    # ===== DATA TABLE =====
    st.markdown("### 📄 Data Preview")
    st.dataframe(df, use_container_width=True)

else:
    st.info("👈 Upload a CSV or Excel file to get started")