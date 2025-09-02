import streamlit as st
import pandas as pd
import numpy as np
import time
from datetime import datetime

st.set_page_config(page_title="GreenGrid App", layout="wide")

st.title("GreenGrid - Energy Usage Forecasting")
st.write("This app shows live power usage, simple forecasting, and overload alerts.")

# 15 Substations
SUBSTATIONS = [f"S{i:02d}" for i in range(1, 16)]
CAPACITY = {sid: np.random.randint(1800, 2600) for sid in SUBSTATIONS}

# Save data
if "data" not in st.session_state:
    st.session_state.data = pd.DataFrame(columns=["time", "substation", "load_kW"])

if "alerts" not in st.session_state:
    st.session_state.alerts = []

# Function to generate random data
def generate_data():
    now = datetime.now().strftime("%H:%M:%S")
    sid = np.random.choice(SUBSTATIONS)
    load = np.random.randint(1000, 3000)
    return {"time": now, "substation": sid, "load_kW": load}

# Auto streaming
placeholder = st.empty()

for _ in range(100):  # runs for 100 updates
    new_data = generate_data()
    st.session_state.data = pd.concat(
        [st.session_state.data, pd.DataFrame([new_data])],
        ignore_index=True
    )

    # Check overload
    if new_data["load_kW"] > CAPACITY[new_data["substation"]]:
        st.session_state.alerts.append(
            f"Overload at {new_data['substation']} ({new_data['load_kW']} kW)"
        )

    with placeholder.container():
        # Live data table (last 10 records)
        st.subheader("Live Power Usage Data (Latest 10 readings)")
        st.dataframe(st.session_state.data.tail(10))

        # Line chart
        st.subheader("Usage Trend Over Time")
        chart_data = st.session_state.data.groupby("time")["load_kW"].mean()
        st.line_chart(chart_data)

        # Forecast (simple average)
        st.subheader("Forecast (Average Load)")
        forecast = st.session_state.data.groupby("substation")["load_kW"].mean()
        st.bar_chart(forecast)

        # Overload Alerts
        st.subheader("Overload Alerts")
        if st.session_state.alerts:
            for alert in st.session_state.alerts[-5:]:
                st.error(alert)
        else:
            st.success("No overloads detected yet")

    time.sleep(2)  # refresh every 2 seconds
