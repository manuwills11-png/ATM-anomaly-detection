import streamlit as st
import pandas as pd
import random
import datetime
from streamlit_autorefresh import st_autorefresh
from engine import train_model, load_severity, predict_atm

# --------------------------------------------------
# PAGE CONFIG
# --------------------------------------------------

st.set_page_config(
    page_title="ATM Fleet Monitoring",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&family=IBM+Plex+Mono:wght@400;500&display=swap');

    html, body, [class*="css"] {
        font-family: 'Inter', sans-serif;
    }

    .stApp {
        background-color: #1a1d23;
    }

    #MainMenu, footer { visibility: hidden; }
    .block-container { padding: 0 2rem 3rem 2rem; max-width: 1400px; }

    /* ── TOP NAV BAR ── */
    .topbar {
        display: flex;
        align-items: center;
        justify-content: space-between;
        background: #13151a;
        border-bottom: 1px solid #2e3138;
        padding: 0.9rem 2rem;
        margin: 0 -2rem 2rem -2rem;
    }

    .topbar-left {
        display: flex;
        align-items: center;
        gap: 1rem;
    }

    .topbar-logo {
        width: 32px; height: 32px;
        background: #2563eb;
        border-radius: 6px;
        display: flex; align-items: center; justify-content: center;
        font-size: 1rem;
        flex-shrink: 0;
    }

    .topbar-title {
        font-size: 0.95rem;
        font-weight: 600;
        color: #f1f3f6;
        letter-spacing: 0.01em;
    }

    .topbar-subtitle {
        font-size: 0.72rem;
        color: #6b7280;
        margin-top: 0.05rem;
    }

    .topbar-right {
        display: flex;
        align-items: center;
        gap: 1.5rem;
    }

    .live-badge {
        display: flex;
        align-items: center;
        gap: 0.4rem;
        background: rgba(34,197,94,0.1);
        border: 1px solid rgba(34,197,94,0.25);
        padding: 0.28rem 0.75rem;
        border-radius: 4px;
        font-size: 0.7rem;
        font-weight: 500;
        color: #4ade80;
        letter-spacing: 0.05em;
    }

    .live-indicator {
        width: 6px; height: 6px;
        border-radius: 50%;
        background: #22c55e;
        animation: blink 2s ease-in-out infinite;
    }

    @keyframes blink {
        0%, 100% { opacity: 1; }
        50% { opacity: 0.35; }
    }

    .topbar-timestamp {
        font-family: 'IBM Plex Mono', monospace;
        font-size: 0.7rem;
        color: #4b5563;
    }

    /* ── METRIC CARDS ── */
    .kpi-row {
        display: grid;
        grid-template-columns: repeat(4, 1fr);
        gap: 1rem;
        margin-bottom: 1.75rem;
    }

    .kpi-card {
        background: #20242c;
        border: 1px solid #2e3138;
        border-radius: 8px;
        padding: 1.1rem 1.3rem;
        position: relative;
    }

    .kpi-card-top {
        display: flex;
        align-items: center;
        justify-content: space-between;
        margin-bottom: 0.6rem;
    }

    .kpi-label {
        font-size: 0.72rem;
        font-weight: 500;
        color: #6b7280;
        text-transform: uppercase;
        letter-spacing: 0.06em;
    }

    .kpi-icon {
        width: 28px; height: 28px;
        border-radius: 6px;
        display: flex; align-items: center; justify-content: center;
        font-size: 0.8rem;
    }

    .kpi-value {
        font-size: 1.85rem;
        font-weight: 700;
        color: #f1f3f6;
        line-height: 1;
        letter-spacing: -0.02em;
    }

    .kpi-card.alert-red { border-left: 3px solid #ef4444; }
    .kpi-card.alert-amber { border-left: 3px solid #f59e0b; }
    .kpi-card.alert-green { border-left: 3px solid #22c55e; }
    .kpi-card.alert-blue { border-left: 3px solid #3b82f6; }

    .kpi-card.alert-red .kpi-value { color: #fca5a5; }
    .kpi-card.alert-amber .kpi-value { color: #fcd34d; }
    .kpi-card.alert-green .kpi-value { color: #86efac; }
    .kpi-card.alert-blue .kpi-value { color: #93c5fd; }

    .kpi-footnote {
        font-size: 0.7rem;
        color: #4b5563;
        margin-top: 0.35rem;
    }

    /* ── SECTION LABELS ── */
    .section-label {
        font-size: 0.72rem;
        font-weight: 600;
        color: #6b7280;
        text-transform: uppercase;
        letter-spacing: 0.08em;
        margin: 0 0 0.75rem 0;
        padding-bottom: 0.5rem;
        border-bottom: 1px solid #2e3138;
    }

    /* ── ATM TABLE ── */
    .atm-table {
        background: #20242c;
        border: 1px solid #2e3138;
        border-radius: 8px;
        overflow: hidden;
        margin-bottom: 1.25rem;
    }

    .atm-table-header {
        display: grid;
        grid-template-columns: 90px 110px 120px 110px 90px 80px 90px 90px;
        background: #13151a;
        border-bottom: 1px solid #2e3138;
        padding: 0.6rem 1rem;
    }

    .atm-th {
        font-size: 0.65rem;
        font-weight: 600;
        color: #4b5563;
        text-transform: uppercase;
        letter-spacing: 0.08em;
    }

    .atm-row {
        display: grid;
        grid-template-columns: 90px 110px 120px 110px 90px 80px 90px 90px;
        padding: 0.72rem 1rem;
        border-bottom: 1px solid #1e2128;
        align-items: center;
        transition: background 0.15s ease;
    }

    .atm-row:last-child { border-bottom: none; }
    .atm-row:hover { background: rgba(255,255,255,0.02); }
    .atm-row.row-critical { background: rgba(239,68,68,0.05); }
    .atm-row.row-critical:hover { background: rgba(239,68,68,0.08); }
    .atm-row.row-warning { background: rgba(245,158,11,0.04); }
    .atm-row.row-warning:hover { background: rgba(245,158,11,0.07); }

    .atm-cell {
        font-size: 0.8rem;
        color: #c9d1dc;
        font-family: 'IBM Plex Mono', monospace;
    }

    .atm-cell.atm-id-cell {
        font-weight: 600;
        color: #e2e8f0;
        font-family: 'Inter', sans-serif;
        font-size: 0.82rem;
    }

    .atm-cell.val-high { color: #fca5a5; }
    .atm-cell.val-med  { color: #fcd34d; }
    .atm-cell.val-ok   { color: #86efac; }

    .badge {
        display: inline-block;
        font-size: 0.63rem;
        font-weight: 600;
        padding: 0.18rem 0.5rem;
        border-radius: 4px;
        letter-spacing: 0.04em;
        text-transform: uppercase;
        font-family: 'Inter', sans-serif;
    }

    .badge.critical {
        background: rgba(239,68,68,0.14);
        color: #fca5a5;
        border: 1px solid rgba(239,68,68,0.28);
    }

    .badge.warning {
        background: rgba(245,158,11,0.11);
        color: #fcd34d;
        border: 1px solid rgba(245,158,11,0.24);
    }

    .badge.nominal {
        background: rgba(34,197,94,0.09);
        color: #86efac;
        border: 1px solid rgba(34,197,94,0.2);
    }

    .risk-track {
        width: 64px;
        height: 5px;
        background: #2e3138;
        border-radius: 3px;
        overflow: hidden;
        display: inline-block;
        vertical-align: middle;
    }

    .risk-fill {
        height: 100%;
        border-radius: 3px;
    }

    /* ── CHART CARDS ── */
    .chart-card {
        background: #20242c;
        border: 1px solid #2e3138;
        border-radius: 8px;
        padding: 1.1rem 1.2rem;
    }

    .chart-title {
        font-size: 0.72rem;
        font-weight: 600;
        color: #6b7280;
        text-transform: uppercase;
        letter-spacing: 0.08em;
        margin-bottom: 0.75rem;
    }

    /* ── ALERT PANEL ── */
    .alert-panel {
        background: #20242c;
        border: 1px solid #2e3138;
        border-radius: 8px;
        overflow: hidden;
    }

    .alert-panel-header {
        padding: 0.6rem 1rem;
        background: #13151a;
        border-bottom: 1px solid #2e3138;
        font-size: 0.68rem;
        font-weight: 600;
        color: #6b7280;
        text-transform: uppercase;
        letter-spacing: 0.09em;
    }

    .alert-item {
        display: flex;
        align-items: center;
        gap: 0.9rem;
        padding: 0.65rem 1rem;
        border-bottom: 1px solid #1e2128;
        font-size: 0.79rem;
    }

    .alert-item:last-child { border-bottom: none; }
    .alert-item.crit { border-left: 3px solid #ef4444; }
    .alert-item.warn { border-left: 3px solid #f59e0b; }

    .alert-dot-crit { width: 7px; height: 7px; border-radius: 50%; background: #ef4444; flex-shrink: 0; }
    .alert-dot-warn { width: 7px; height: 7px; border-radius: 50%; background: #f59e0b; flex-shrink: 0; }

    .alert-atm { font-weight: 600; color: #e2e8f0; min-width: 72px; }
    .alert-msg { color: #9ca3af; flex: 1; }
    .alert-score { font-family: 'IBM Plex Mono', monospace; font-size: 0.73rem; color: #6b7280; }

    .all-clear {
        display: flex;
        align-items: center;
        gap: 0.75rem;
        padding: 0.85rem 1rem;
        font-size: 0.8rem;
        color: #86efac;
    }

    /* ── SIDEBAR ── */
    [data-testid="stSidebar"] {
        background: #13151a !important;
        border-right: 1px solid #2e3138 !important;
    }

    .sb-section-title {
        font-size: 0.63rem;
        font-weight: 600;
        color: #4b5563;
        text-transform: uppercase;
        letter-spacing: 0.1em;
        padding: 0.8rem 0 0.4rem 0;
        border-top: 1px solid #2e3138;
        margin-top: 0.4rem;
    }

    .sb-row {
        display: flex;
        justify-content: space-between;
        align-items: center;
        padding: 0.45rem 0;
        border-bottom: 1px solid #1e2128;
        font-size: 0.8rem;
    }

    .sb-key { color: #6b7280; }
    .sb-val { font-family: 'IBM Plex Mono', monospace; font-weight: 500; color: #e2e8f0; font-size: 0.78rem; }
    .sb-val.red { color: #fca5a5; }
    .sb-val.amber { color: #fcd34d; }
    .sb-val.green { color: #86efac; }

    div.stCaption {
        font-family: 'IBM Plex Mono', monospace !important;
        font-size: 0.63rem !important;
        color: #374151 !important;
        text-transform: uppercase;
        letter-spacing: 0.07em;
    }
</style>
""", unsafe_allow_html=True)

st_autorefresh(interval=5000, key="atm_refresh")

# --------------------------------------------------
# LOAD MODEL
# --------------------------------------------------

@st.cache_resource
def setup():
    model = train_model()
    severity = load_severity()
    return model, severity

model, severity_weight = setup()

# --------------------------------------------------
# ATM STATE
# --------------------------------------------------

def initialize_atms():
    return [{
        "atm_id": f"ATM-{i:03d}",
        "latency": random.randint(500, 1500),
        "packet_loss": random.randint(0, 5),
        "cpu_usage": random.randint(30, 60),
        "transactions_last_5min": random.randint(50, 150)
    } for i in range(1, 6)]

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
# PREDICTIONS
# --------------------------------------------------

results = []
for atm in atms:
    prediction, confidence, risk_score = predict_atm(model, severity_weight, atm)
    results.append({
        "ATM ID": atm["atm_id"],
        "Latency": atm["latency"],
        "Packet Loss": atm["packet_loss"],
        "CPU Usage": atm["cpu_usage"],
        "Transactions (5min)": atm["transactions_last_5min"],
        "Prediction": prediction,
        "Confidence (%)": round(confidence * 100, 2),
        "Risk Score": round(risk_score, 2),
    })

df = pd.DataFrame(results)
df["Status"] = df["Risk Score"].apply(
    lambda x: "Critical" if x > 4 else "Warning" if x > 3 else "Nominal"
)

high_risk_count = len(df[df["Risk Score"] > 3])
avg_risk = round(df["Risk Score"].mean(), 2)
active_failures = len(df[df["Prediction"] != "Normal"])
nominal_count = len(df) - high_risk_count
now_str = datetime.datetime.now().strftime("%d %b %Y  %H:%M:%S")

# --------------------------------------------------
# TOP BAR
# --------------------------------------------------

st.markdown(f"""
<div class="topbar">
    <div class="topbar-left">
        <div class="topbar-logo">🏧</div>
        <div>
            <div class="topbar-title">ATM Fleet Monitoring</div>
            <div class="topbar-subtitle">Network Operations Center</div>
        </div>
    </div>
    <div class="topbar-right">
        <div class="topbar-timestamp">{now_str}</div>
        <div class="live-badge"><div class="live-indicator"></div>Live</div>
    </div>
</div>
""", unsafe_allow_html=True)

# --------------------------------------------------
# KPI CARDS
# --------------------------------------------------

risk_cls  = "alert-red" if avg_risk > 4 else "alert-amber" if avg_risk > 3 else "alert-green"
fail_cls  = "alert-red" if active_failures > 0 else "alert-green"
high_cls  = "alert-red" if high_risk_count > 0 else "alert-green"

st.markdown(f"""
<div class="kpi-row">
    <div class="kpi-card alert-blue">
        <div class="kpi-card-top">
            <div class="kpi-label">Total Units</div>
            <div class="kpi-icon" style="background:rgba(59,130,246,0.12);">🖥</div>
        </div>
        <div class="kpi-value">{len(df)}</div>
        <div class="kpi-footnote">Active in fleet</div>
    </div>
    <div class="kpi-card {high_cls}">
        <div class="kpi-card-top">
            <div class="kpi-label">High Risk</div>
            <div class="kpi-icon" style="background:rgba(239,68,68,0.1);">⚠</div>
        </div>
        <div class="kpi-value">{high_risk_count}</div>
        <div class="kpi-footnote">Risk score above 3.0</div>
    </div>
    <div class="kpi-card {fail_cls}">
        <div class="kpi-card-top">
            <div class="kpi-label">Active Failures</div>
            <div class="kpi-icon" style="background:rgba(239,68,68,0.1);">✕</div>
        </div>
        <div class="kpi-value">{active_failures}</div>
        <div class="kpi-footnote">{nominal_count} units nominal</div>
    </div>
    <div class="kpi-card {risk_cls}">
        <div class="kpi-card-top">
            <div class="kpi-label">Avg Risk Score</div>
            <div class="kpi-icon" style="background:rgba(245,158,11,0.1);">◈</div>
        </div>
        <div class="kpi-value">{avg_risk}</div>
        <div class="kpi-footnote">Fleet average / 5.0</div>
    </div>
</div>
""", unsafe_allow_html=True)

# --------------------------------------------------
# CHARTS
# --------------------------------------------------

col1, col2 = st.columns([3, 2])

with col1:
    st.markdown('<div class="chart-card">', unsafe_allow_html=True)
    st.markdown('<div class="chart-title">Risk Score — 20 Cycle Trend</div>', unsafe_allow_html=True)
    if "history" not in st.session_state:
        st.session_state.history = []
    st.session_state.history.append(df["Risk Score"].mean())
    if len(st.session_state.history) > 20:
        st.session_state.history.pop(0)
    st.line_chart(pd.DataFrame({"Avg Risk": st.session_state.history}), color="#3b82f6", height=170)
    st.markdown('</div>', unsafe_allow_html=True)

with col2:
    st.markdown('<div class="chart-card">', unsafe_allow_html=True)
    st.markdown('<div class="chart-title">Risk by Unit</div>', unsafe_allow_html=True)
    st.bar_chart(df.set_index("ATM ID")[["Risk Score"]], color="#6366f1", height=170)
    st.markdown('</div>', unsafe_allow_html=True)

st.markdown("<div style='height:1.25rem'></div>", unsafe_allow_html=True)

# --------------------------------------------------
# ATM TABLE
# --------------------------------------------------

st.markdown('<div class="section-label">Terminal Status</div>', unsafe_allow_html=True)
st.markdown('<div class="atm-table">', unsafe_allow_html=True)
st.markdown("""
<div class="atm-table-header">
    <div class="atm-th">Unit ID</div>
    <div class="atm-th">Status</div>
    <div class="atm-th">Prediction</div>
    <div class="atm-th">Risk Score</div>
    <div class="atm-th">Latency</div>
    <div class="atm-th">CPU</div>
    <div class="atm-th">Pkt Loss</div>
    <div class="atm-th">TXN / 5m</div>
</div>
""", unsafe_allow_html=True)

def latency_cls(v): return "val-high" if v > 1200 else "val-med" if v > 800 else "val-ok"
def cpu_cls(v):     return "val-high" if v > 75  else "val-med" if v > 55  else "val-ok"
def loss_cls(v):    return "val-high" if v > 3   else "val-med" if v > 1   else "val-ok"
def txn_cls(v):     return "val-high" if v < 30  else "val-med" if v < 60  else "val-ok"

for _, row in df.iterrows():
    status = row["Status"]
    risk = row["Risk Score"]
    row_class = "row-critical" if status == "Critical" else "row-warning" if status == "Warning" else ""
    badge_cls = status.lower()
    bar_pct = min(100, risk / 5 * 100)
    bar_color = "#ef4444" if risk > 4 else "#f59e0b" if risk > 3 else "#22c55e"

    st.markdown(f"""
    <div class="atm-row {row_class}">
        <div class="atm-cell atm-id-cell">{row['ATM ID']}</div>
        <div class="atm-cell"><span class="badge {badge_cls}">{status}</span></div>
        <div class="atm-cell" style="color:#9ca3af; font-family:'Inter',sans-serif; font-size:0.78rem;">{row['Prediction']}</div>
        <div class="atm-cell">
            <div class="risk-track"><div class="risk-fill" style="width:{bar_pct}%; background:{bar_color};"></div></div>
            <span style="font-size:0.75rem; color:#9ca3af; margin-left:0.4rem;">{risk}</span>
        </div>
        <div class="atm-cell {latency_cls(row['Latency'])}">{row['Latency']} ms</div>
        <div class="atm-cell {cpu_cls(row['CPU Usage'])}">{row['CPU Usage']}%</div>
        <div class="atm-cell {loss_cls(row['Packet Loss'])}">{row['Packet Loss']}%</div>
        <div class="atm-cell {txn_cls(row['Transactions (5min)'])}">{row['Transactions (5min)']}</div>
    </div>
    """, unsafe_allow_html=True)

st.markdown('</div>', unsafe_allow_html=True)
st.markdown("<div style='height:0.5rem'></div>", unsafe_allow_html=True)

# --------------------------------------------------
# ALERTS
# --------------------------------------------------

st.markdown('<div class="section-label">Active Alerts</div>', unsafe_allow_html=True)
st.markdown('<div class="alert-panel">', unsafe_allow_html=True)
st.markdown('<div class="alert-panel-header">Alert Feed</div>', unsafe_allow_html=True)

flagged = df[df["Risk Score"] > 3].sort_values("Risk Score", ascending=False)

if flagged.empty:
    st.markdown("""
    <div class="all-clear">
        <span>✓</span>
        <span>All terminals operating within normal thresholds. No alerts at this time.</span>
    </div>
    """, unsafe_allow_html=True)
else:
    for _, row in flagged.iterrows():
        level = "crit" if row["Risk Score"] > 4 else "warn"
        dot = "alert-dot-crit" if level == "crit" else "alert-dot-warn"
        label = "Critical" if level == "crit" else "Warning"
        st.markdown(f"""
        <div class="alert-item {level}">
            <div class="{dot}"></div>
            <div class="alert-atm">{row['ATM ID']}</div>
            <div class="alert-msg">{label} — {row['Prediction']} · Confidence {row['Confidence (%)']}%</div>
            <div class="alert-score">Risk {row['Risk Score']}</div>
        </div>
        """, unsafe_allow_html=True)

st.markdown('</div>', unsafe_allow_html=True)

# --------------------------------------------------
# SIDEBAR
# --------------------------------------------------

with st.sidebar:
    st.markdown("""
    <div style="padding: 0.25rem 0 1rem 0;">
        <div style="font-size:0.88rem; font-weight:600; color:#e2e8f0;">Fleet Summary</div>
        <div style="font-size:0.7rem; color:#4b5563; margin-top:0.1rem;">Real-time overview</div>
    </div>
    """, unsafe_allow_html=True)

    crit_n = len(df[df["Status"] == "Critical"])
    warn_n = len(df[df["Status"] == "Warning"])

    st.markdown('<div class="sb-section-title">Status Breakdown</div>', unsafe_allow_html=True)

    rows = [
        ("Total Units",    len(df),         ""),
        ("Nominal",        nominal_count,   "green"),
        ("Warning",        warn_n,          "amber" if warn_n > 0 else "green"),
        ("Critical",       crit_n,          "red"   if crit_n > 0 else "green"),
        ("Active Failures",active_failures, "red"   if active_failures > 0 else "green"),
        ("Avg Risk Score", avg_risk,        "red"   if avg_risk > 4 else "amber" if avg_risk > 3 else "green"),
    ]

    for label, value, cls in rows:
        val_attr = f'class="sb-val {cls}"' if cls else 'class="sb-val"'
        st.markdown(f"""
        <div class="sb-row">
            <span class="sb-key">{label}</span>
            <span {val_attr}>{value}</span>
        </div>
        """, unsafe_allow_html=True)

    st.markdown('<div class="sb-section-title">Configuration</div>', unsafe_allow_html=True)
    st.markdown(f"""
    <div class="sb-row"><span class="sb-key">Refresh</span><span class="sb-val">5 s</span></div>
    <div class="sb-row"><span class="sb-key">Fleet size</span><span class="sb-val">{len(df)} units</span></div>
    <div class="sb-row"><span class="sb-key">Risk threshold</span><span class="sb-val">3.0 / 5.0</span></div>
    """, unsafe_allow_html=True)

    st.markdown(f"""
    <div style="margin-top:1.5rem; font-family:'IBM Plex Mono',monospace; font-size:0.62rem;
                color:#374151; text-transform:uppercase; letter-spacing:0.08em; line-height:1.8;">
        Last updated<br>{now_str}
    </div>
    """, unsafe_allow_html=True)

st.caption("ATM Fleet Monitoring · Auto-refresh every 5 seconds")
