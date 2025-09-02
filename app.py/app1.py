import streamlit as st
import pandas as pd
import numpy as np
from datetime import datetime

# Page settings
st.set_page_config(page_title="GreenGrid App", layout="wide")

# Title and description
st.title("GreenGrid - Energy Usage Forecasting & Smart Control")
st.write("Live power usage, forecasting, overload alerts, and smart load management.")

# 15 Substations
SUBSTATIONS = [f"S{i:02d}" for i in range(1, 16)]
CAPACITY = {sid: np.random.randint(1800, 2600) for sid in SUBSTATIONS}

# Battery storage (simulation)
BATTERY_CAPACITY = 500  # kW
if "battery_charge" not in st.session_state:
    st.session_state.battery_charge = BATTERY_CAPACITY

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


# Smart overload handling
def manage_overload(sid, load, t):
    original_load = load
    # 1. Check overload
    if load > CAPACITY[sid]:
        # 2. Try load balancing
        for other_sid in SUBSTATIONS:
            if other_sid != sid and load <= CAPACITY[other_sid]:
                st.info(f"Redirecting {load} kW from {sid} to {other_sid}")
                return other_sid, load

        # 3. Try load shedding (reduce 20%)
        reduced_load = int(load * 0.8)
        st.warning(f"Load shedding at {sid}: reduced {load} → {reduced_load} kW")
        load = reduced_load

        # 4. Try battery support if still high
        if load > CAPACITY[sid] and st.session_state.battery_charge > 0:
            support = min(load - CAPACITY[sid], st.session_state.battery_charge)
            st.session_state.battery_charge -= support
            load -= support
            st.success(f"Battery discharged {support} kW to support {sid}")

        # Final alert if still overloaded
        if load > CAPACITY[sid]:
            alert_msg = f"⚠️ Overload Alert! {sid} exceeded capacity at {t} (Load: {original_load} kW → Adjusted: {load} kW, Limit: {CAPACITY[sid]} kW)"
            st.session_state.alerts.append(alert_msg)

    return sid, load


# Button to simulate new data
if st.button("Generate New Data"):
    t, sid, load = generate_data()
    sid, load = manage_overload(sid, load, t)  # apply smart control

    new_row = pd.DataFrame([[t, sid, load]], columns=["time", "substation", "load_kW"])
    st.session_state.data = pd.concat([st.session_state.data, new_row], ignore_index=True)


# Display live data
st.subheader("Live Power Usage Data")
st.dataframe(st.session_state.data.tail(10))

# Simple forecast (average load per substation)
st.subheader("Forecast (Average Load)")
if not st.session_state.data.empty:
    forecast = st.session_state.data.groupby("substation")["load_kW"].mean().reset_index()
    st.bar_chart(forecast.set_index("substation"))

# Usage Trend Over Time
st.subheader("Usage Trend Over Time")
if not st.session_state.data.empty:
    trend_data = st.session_state.data.set_index("time")
    st.line_chart(trend_data["load_kW"])

# Alerts
st.subheader("Overload Alerts")
if st.session_state.alerts:
    for alert in st.session_state.alerts[-5:]:
        st.error(alert)
else:
    st.success("No overloads detected yet")

# Battery status
st.subheader("Battery Storage Status")
st.progress(st.session_state.battery_charge / BATTERY_CAPACITY)
st.write(f"Battery charge: {st.session_state.battery_charge} / {BATTERY_CAPACITY} kW")
