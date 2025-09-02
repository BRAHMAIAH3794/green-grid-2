import streamlit as st
import pandas as pd
import numpy as np
from datetime import datetime

# Page settings
st.set_page_config(page_title="GreenGrid App", layout="wide")

# Title and description
st.title("GreenGrid - Energy Usage Forecasting")
st.write("This demo shows live power usage, simple forecasting, and overload alerts.")

# 15 Substations
SUBSTATIONS = [f"S{i:02d}" for i in range(1, 16)]
CAPACITY = {sid: np.random.randint(1800, 2600) for sid in SUBSTATIONS}

# Save session data
if "data" not in st.session_state:
    st.session_state.data = pd.DataFrame(columns=["time", "substation", "load_kW"])

if "alerts" not in st.session_state:
    st.session_state.alerts = []

# Function to generate random load data
def generate_data():
    now = datetime.now().strftime("%H:%M:%S")
    sid = np.random.choice(SUBSTATIONS)
    load = np.random.randint(1000, 3000)
    return now, sid, load

# Button to simulate new data
if st.button("Generate New Data"):
    t, sid, load = generate_data()
    new_row = pd.DataFrame([[t, sid, load]], columns=["time", "substation", "load_kW"])
    st.session_state.data = pd.concat([st.session_state.data, new_row], ignore_index=True)

    # Check overload
    if load > CAPACITY[sid]:
        alert_msg = f"Overload Alert! {sid} exceeded capacity at {t} (Load: {load} kW, Limit: {CAPACITY[sid]} kW)"
        st.session_state.alerts.append(alert_msg)

# Display live data
st.subheader("Live Power Usage Data")
st.dataframe(st.session_state.data.tail(10))

# Simple forecast (average load per substation)
st.subheader("Forecast (Average Load)")
forecast = st.session_state.data.groupby("substation")["load_kW"].mean().reset_index()
st.bar_chart(forecast.set_index("substation"))

# Alerts
st.subheader("Overload Alerts")
if st.session_state.alerts:
    for alert in st.session_state.alerts[-5:]:
        st.error(alert)
else:
    st.success("No overloads detected yet")