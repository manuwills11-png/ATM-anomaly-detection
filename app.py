import streamlit as st
import pandas as pd
import random
from streamlit_autorefresh import st_autorefresh
from engine import train_model, load_severity, predict_atm

# --------------------------------------------------
# PAGE CONFIG
# --------------------------------------------------

st.set_page_config(
    page_title="ATM Fleet Monitoring",
    layout="wide"
)

st.title("🏧 ATM Fleet Monitoring Dashboard")

# Auto refresh every 5 seconds
st_autorefresh(interval=5000, key="atm_refresh")

# --------------------------------------------------
# LOAD MODEL & CONFIG (Cached)
# --------------------------------------------------

@st.cache_resource
def setup():
    model = train_model()
    severity = load_severity()
    return model, severity

model, severity_weight = setup()

# --------------------------------------------------
# INITIALIZE PERSISTENT ATMs
# --------------------------------------------------

def initialize_atms():
    atms = []
    for i in range(1, 6):
        atms.append({
            "atm_id": f"ATM_{i}",
            "latency": random.randint(500, 1500),
            "packet_loss": random.randint(0, 5),
            "cpu_usage": random.randint(30, 60),
            "transactions_last_5min": random.randint(50, 150)
        })
    return atms

def update_atms(atms):
    for atm in atms:
        atm["latency"] = max(100, atm["latency"] + random.randint(-200, 200))
        atm["packet_loss"] = max(0, atm["packet_loss"] + random.randint(-5, 5))
        atm["cpu_usage"] = max(0, min(100, atm["cpu_usage"] + random.randint(-10, 10)))
        atm["transactions_last_5min"] = max(0, atm["transactions_last_5min"] + random.randint(-20, 20))
    return atms

if "atms" not in st.session_state:
    st.session_state.atms = initialize_atms()

st.session_state.atms = update_atms(st.session_state.atms)
atms = st.session_state.atms

# --------------------------------------------------
# PREDICT & CALCULATE RISK
# --------------------------------------------------

results = []

for atm in atms:
    prediction, confidence, risk_score = predict_atm(
        model,
        severity_weight,
        atm
    )

    results.append({
        "ATM ID": atm["atm_id"],
        "Latency": atm["latency"],
        "Packet Loss": atm["packet_loss"],
        "CPU Usage": atm["cpu_usage"],
        "Transactions (5min)": atm["transactions_last_5min"],
        "Prediction": prediction,
        "Confidence (%)": round(confidence * 100, 2),
        "Risk Score": round(risk_score, 2)
    })

df_results = pd.DataFrame(results)

# --------------------------------------------------
# SUMMARY METRICS
# --------------------------------------------------

col1, col2, col3 = st.columns(3)

high_risk_count = len(df_results[df_results["Risk Score"] > 3])
avg_risk = round(df_results["Risk Score"].mean(), 2)
active_failures = len(df_results[df_results["Prediction"] != "Normal"])

col1.metric("🚨 High Risk ATMs", high_risk_count)
col2.metric("📊 Average Risk Score", avg_risk)
col3.metric("⚠ Active Failures", active_failures)

st.markdown("---")

# --------------------------------------------------
# COLOR HIGHLIGHTING
# --------------------------------------------------

def highlight_risk(row):
    if row["Risk Score"] > 4:
        return ["background-color: #ff4b4b"] * len(row)
    elif row["Risk Score"] > 3:
        return ["background-color: #ffa500"] * len(row)
    else:
        return [""] * len(row)

styled_df = df_results.style.apply(highlight_risk, axis=1)

st.dataframe(styled_df, use_container_width=True)

# --------------------------------------------------
# ALERT SECTION
# --------------------------------------------------

high_risk_atms = df_results[df_results["Risk Score"] > 3]

if not high_risk_atms.empty:
    st.error("🚨 Critical ATMs Detected")
    st.dataframe(high_risk_atms[["ATM ID", "Prediction", "Risk Score"]])
else:
    st.success("✅ All ATMs Operating Within Safe Thresholds")