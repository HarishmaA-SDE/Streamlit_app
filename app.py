# =========================================================
# IMPORT LIBRARIES
# =========================================================
import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

# =========================================================
# PAGE CONFIG
# =========================================================
st.set_page_config(
    page_title="Integrated Transformer Monitoring System",
    page_icon="⚡",
    layout="wide"
)

# =========================================================
# CUSTOM CSS
# =========================================================
st.markdown("""
<style>

/* Main Background */
.stApp {
    background-color: #081028;
    color: white;
}

/* KPI Cards */
.metric-card {
    background: linear-gradient(135deg, #132347, #1d3b70);
    padding: 20px;
    border-radius: 15px;
    color: white;
    box-shadow: 0px 4px 12px rgba(0,0,0,0.4);
    border: 1px solid rgba(255,255,255,0.1);
}

.metric-title {
    font-size: 18px;
    color: #cbd5e1;
    margin-bottom: 10px;
}

.metric-value {
    font-size: 34px;
    font-weight: bold;
    color: white;
}

/* Sidebar */
section[data-testid="stSidebar"] {
    background-color: #060f24;
}

/* Dataframe */
[data-testid="stDataFrame"] {
    border-radius: 12px;
    overflow: hidden;
}

/* Headers */
h1, h2, h3, h4 {
    color: white !important;
}

/* Alert Box */
.alert-box {
    padding: 15px;
    border-radius: 12px;
    margin-bottom: 10px;
    color: white;
    font-weight: 500;
}

.red {
    background-color: rgba(255, 0, 0, 0.25);
    border-left: 5px solid red;
}

.orange {
    background-color: rgba(255, 165, 0, 0.25);
    border-left: 5px solid orange;
}

.green {
    background-color: rgba(0, 128, 0, 0.25);
    border-left: 5px solid limegreen;
}

</style>
""", unsafe_allow_html=True)

# =========================================================
# HEADER
# =========================================================
col1, col2 = st.columns([8, 2])

with col1:
    st.markdown("""
    # Integrated - Transformer Electrical Monitoring System
    ### VIT Vellore
    """)

with col2:
    st.markdown("""
    <div style='text-align:right; padding-top:25px;'>
        <h4 style='color:white;'>Developed by Harikrishnan A & Anish S</h4>
    </div>
    """, unsafe_allow_html=True)

st.divider()

# =========================================================
# FILE UPLOAD
# =========================================================
uploaded_file = st.sidebar.file_uploader(
    "Upload CSV or Excel File",
    type=["csv", "xlsx"]
)

# =========================================================
# LOAD DATA
# =========================================================
def load_data(file):
    if file.name.endswith(".csv"):
        return pd.read_csv(file)
    else:
        return pd.read_excel(file)

# =========================================================
# MAIN APP
# =========================================================
if uploaded_file:

    df = load_data(uploaded_file)

    # Convert Time Column
    df["Time"] = pd.to_datetime(df["Time"])

    # Sort by Time
    df = df.sort_values("Time")

    # =====================================================
    # SIDEBAR FILTERS
    # =====================================================
    st.sidebar.markdown("## Filters")

    start_date = st.sidebar.date_input(
        "Start Date",
        df["Time"].min()
    )

    end_date = st.sidebar.date_input(
        "End Date",
        df["Time"].max()
    )

    filtered_df = df[
        (df["Time"] >= pd.to_datetime(start_date)) &
        (df["Time"] <= pd.to_datetime(end_date))
    ]

    # =====================================================
    # FEATURE ENGINEERING
    # =====================================================
    filtered_df["Temp Difference"] = (
        filtered_df["Winding Temp (°C)"] -
        filtered_df["Oil Temp (°C)"]
    )

    # Trip Points
    trip_df = filtered_df[
        filtered_df["Status"].isin(["TRIP", "Tripped"])
    ]

    # =====================================================
    # KPI SECTION
    # =====================================================
    st.markdown("## System Overview")

    c1, c2, c3, c4 = st.columns(4)

    with c1:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-title">⚡ Max Voltage</div>
            <div class="metric-value">
                {filtered_df['Voltage (kV)'].max():.2f} kV
            </div>
        </div>
        """, unsafe_allow_html=True)

    with c2:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-title">🔌 Max Current</div>
            <div class="metric-value">
                {filtered_df['Current (A)'].max()} A
            </div>
        </div>
        """, unsafe_allow_html=True)

    with c3:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-title">🌡️ Max Winding Temp</div>
            <div class="metric-value">
                {filtered_df['Winding Temp (°C)'].max()} °C
            </div>
        </div>
        """, unsafe_allow_html=True)

    with c4:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-title">🚨 Trip Events</div>
            <div class="metric-value">
                {trip_df.shape[0]}
            </div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # =====================================================
    # VOLTAGE GRAPH
    # =====================================================
    st.markdown("## Trends")

    col1, col2 = st.columns(2)

    with col1:

        fig_voltage = go.Figure()

        fig_voltage.add_trace(
            go.Scatter(
                x=filtered_df["Time"],
                y=filtered_df["Voltage (kV)"],
                mode='lines',
                name='Voltage',
                line=dict(color='#4ea8ff', width=3)
            )
        )

        # Highlight Trip Points
        fig_voltage.add_trace(
            go.Scatter(
                x=trip_df["Time"],
                y=trip_df["Voltage (kV)"],
                mode='markers',
                name='Trip Points',
                marker=dict(
                    color='red',
                    size=12,
                    symbol='x'
                )
            )
        )

        fig_voltage.update_layout(
            title="Voltage (kV)",
            template="plotly_dark",
            paper_bgcolor="#081028",
            plot_bgcolor="#081028",
            hovermode="x unified"
        )

        st.plotly_chart(fig_voltage, use_container_width=True)

    # =====================================================
    # CURRENT GRAPH
    # =====================================================
    with col2:

        fig_current = go.Figure()

        fig_current.add_trace(
            go.Scatter(
                x=filtered_df["Time"],
                y=filtered_df["Current (A)"],
                mode='lines',
                name='Current',
                line=dict(color='#32d583', width=3)
            )
        )

        fig_current.add_trace(
            go.Scatter(
                x=trip_df["Time"],
                y=trip_df["Current (A)"],
                mode='markers',
                name='Trip Points',
                marker=dict(
                    color='red',
                    size=12,
                    symbol='x'
                )
            )
        )

        fig_current.update_layout(
            title="Current (A)",
            template="plotly_dark",
            paper_bgcolor="#081028",
            plot_bgcolor="#081028",
            hovermode="x unified"
        )

        st.plotly_chart(fig_current, use_container_width=True)

    # =====================================================
    # TEMPERATURE GRAPH
    # =====================================================
    col3, col4 = st.columns(2)

    with col3:

        fig_temp = go.Figure()

        fig_temp.add_trace(
            go.Scatter(
                x=filtered_df["Time"],
                y=filtered_df["Oil Temp (°C)"],
                mode='lines',
                name='Oil Temp',
                line=dict(color='#4ea8ff', width=3)
            )
        )

        fig_temp.add_trace(
            go.Scatter(
                x=filtered_df["Time"],
                y=filtered_df["Winding Temp (°C)"],
                mode='lines',
                name='Winding Temp',
                line=dict(color='#ff9f1c', width=3)
            )
        )

        fig_temp.add_trace(
            go.Scatter(
                x=trip_df["Time"],
                y=trip_df["Winding Temp (°C)"],
                mode='markers',
                name='Trip Points',
                marker=dict(
                    color='red',
                    size=12,
                    symbol='x'
                )
            )
        )

        fig_temp.update_layout(
            title="Temperature (°C)",
            template="plotly_dark",
            paper_bgcolor="#081028",
            plot_bgcolor="#081028",
            hovermode="x unified"
        )

        st.plotly_chart(fig_temp, use_container_width=True)

    # =====================================================
    # TEMP DIFFERENCE
    # =====================================================
    with col4:

        fig_diff = px.area(
            filtered_df,
            x="Time",
            y="Temp Difference",
            title="Temperature Difference"
        )

        fig_diff.update_layout(
            template="plotly_dark",
            paper_bgcolor="#081028",
            plot_bgcolor="#081028",
            hovermode="x unified"
        )

        st.plotly_chart(fig_diff, use_container_width=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # =====================================================
    # STATUS & ALERTS
    # =====================================================
    col5, col6 = st.columns([2, 1])

    # Status Distribution
    with col5:

        status_counts = (
            filtered_df["Status"]
            .value_counts()
            .reset_index()
        )

        status_counts.columns = ["Status", "Count"]

        fig_status = px.pie(
            status_counts,
            names="Status",
            values="Count",
            hole=0.5
        )

        fig_status.update_layout(
            title="Status Distribution",
            template="plotly_dark",
            paper_bgcolor="#081028"
        )

        st.plotly_chart(fig_status, use_container_width=True)

    # Alerts
    with col6:

        st.markdown("## Alerts")

        if trip_df.shape[0] > 0:
            st.markdown(f"""
            <div class="alert-box red">
            🚨 {trip_df.shape[0]} Trip Events Detected
            </div>
            """, unsafe_allow_html=True)

        if (filtered_df["Winding Temp (°C)"] > 100).any():
            st.markdown("""
            <div class="alert-box orange">
            🌡️ High Winding Temperature
            </div>
            """, unsafe_allow_html=True)

        if (filtered_df["Current (A)"] > 150).any():
            st.markdown("""
            <div class="alert-box orange">
            🔌 High Current Detected
            </div>
            """, unsafe_allow_html=True)

        st.markdown("""
        <div class="alert-box green">
        ✅ System Monitoring Active
        </div>
        """, unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # =====================================================
    # DATA TABLE
    # =====================================================
    st.markdown("## Data Table")

    st.dataframe(
        filtered_df,
        use_container_width=True,
        height=400
    )

# =========================================================
# NO FILE
# =========================================================
else:

    st.info("Upload a CSV or Excel file from the sidebar.")
