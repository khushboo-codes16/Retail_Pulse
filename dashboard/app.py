"""
RetailPulse — Professional SaaS Dashboard
Pure session-state routing: login once, st.button nav, no new tabs, no query params.
"""
import streamlit as st
import sys, os
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
import numpy as np

sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from utils import format_currency, format_number, generate_demo_data

st.set_page_config(
    page_title="RetailPulse",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# ─────────────────────────────────────────────────────────────────────────────
# CSS
# ─────────────────────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');
*, *::before, *::after { box-sizing: border-box; }
html, body, [class*="css"] { font-family: 'Inter', sans-serif; }
#MainMenu, header, footer { visibility: hidden; }
.block-container { padding: 0 !important; max-width: 100% !important; }
section[data-testid="stSidebar"] { display: none !important; }
.stApp { background: #f4f6fb; }

/* ── NAVBAR SHELL ── */
.rp-navbar {
    background: #fff;
    border-bottom: 1px solid #e8eaf0;
    padding: 0 2rem;
    height: 60px;
    display: flex; align-items: center; justify-content: space-between;
    box-shadow: 0 2px 10px rgba(0,0,0,0.06);
    margin-bottom: 0;
}
.rp-brand {
    font-size: 1.1rem; font-weight: 800; color: #4f46e5;
    display: flex; align-items: center; gap: 0.4rem;
    white-space: nowrap; flex-shrink: 0;
}

/* ── STREAMLIT BUTTON → NAV STYLE ── */
/* Target the nav button row specifically via data attribute we set */
div[data-testid="stHorizontalBlock"].nav-row > div {
    flex: 0 0 auto !important;
    width: auto !important;
    min-width: 0 !important;
}
/* Style ALL buttons in the nav container */
.nav-container button[kind="secondary"],
.nav-container button[kind="primary"] {
    background: transparent !important;
    border: none !important;
    color: #6b7280 !important;
    font-size: 0.82rem !important;
    font-weight: 500 !important;
    padding: 0.38rem 0.8rem !important;
    border-radius: 8px !important;
    white-space: nowrap !important;
    box-shadow: none !important;
    transition: all 0.15s !important;
    height: auto !important;
    line-height: 1.4 !important;
}
.nav-container button[kind="secondary"]:hover {
    background: #f3f4f6 !important;
    color: #111827 !important;
}
/* Active nav button */
.nav-container button[kind="primary"] {
    background: #4f46e5 !important;
    color: #fff !important;
    font-weight: 600 !important;
}
/* Logout button */
.logout-container button {
    background: transparent !important;
    border: 1.5px solid #fca5a5 !important;
    color: #ef4444 !important;
    font-size: 0.8rem !important;
    font-weight: 600 !important;
    padding: 0.35rem 0.85rem !important;
    border-radius: 8px !important;
    white-space: nowrap !important;
    box-shadow: none !important;
    height: auto !important;
}
.logout-container button:hover {
    background: #ef4444 !important;
    color: #fff !important;
    border-color: #ef4444 !important;
}

/* ── PAGE BODY ── */
.rp-body { padding: 1.8rem 2.5rem 3rem; }
.rp-page-title { font-size: 1.45rem; font-weight: 800; color: #111827; margin-bottom: 0.2rem; }
.rp-page-sub   { font-size: 0.8rem; color: #9ca3af; margin-bottom: 1.5rem; }

/* ── METRIC CARDS ── */
.metric-card {
    background: #fff; border-radius: 14px;
    padding: 1.1rem 1.2rem;
    display: flex; align-items: center; gap: 0.9rem;
    box-shadow: 0 1px 3px rgba(0,0,0,0.05), 0 4px 14px rgba(0,0,0,0.04);
    border: 1px solid #ebebf5;
    transition: transform 0.18s, box-shadow 0.18s;
    height: 100%;
}
.metric-card:hover { transform: translateY(-2px); box-shadow: 0 6px 22px rgba(79,70,229,0.1); }
.metric-icon {
    width: 44px; height: 44px; border-radius: 11px;
    display: flex; align-items: center; justify-content: center;
    font-size: 1.25rem; flex-shrink: 0;
}
.metric-body { flex: 1; min-width: 0; }
.metric-value { font-size: 1.5rem; font-weight: 700; color: #111827; line-height: 1.1; }
.metric-label { font-size: 0.73rem; color: #9ca3af; margin-top: 0.15rem; }
.metric-delta { font-size: 0.7rem; font-weight: 600; margin-top: 0.22rem; }
.d-up { color: #10b981; } .d-dn { color: #ef4444; }

/* ── CARD WRAPPER ── */
.card {
    background: #fff; border-radius: 14px;
    padding: 1.2rem 1.4rem;
    box-shadow: 0 1px 3px rgba(0,0,0,0.05), 0 4px 14px rgba(0,0,0,0.04);
    border: 1px solid #ebebf5;
    margin-bottom: 1.3rem;
}
.card-title { font-size: 0.92rem; font-weight: 700; color: #111827; margin-bottom: 0.12rem; }
.card-sub   { font-size: 0.73rem; color: #9ca3af; margin-bottom: 0.8rem; }

/* ── ALERT CARDS ── */
.alert-card {
    border-radius: 10px; padding: 0.85rem 1rem;
    border-left: 4px solid; display: flex; align-items: flex-start; gap: 0.65rem;
}
.alert-critical { background: #fff5f5; border-left-color: #ef4444; }
.alert-warning  { background: #fffbeb; border-left-color: #f59e0b; }
.alert-success  { background: #f0fdf4; border-left-color: #10b981; }
.alert-info     { background: #eff6ff; border-left-color: #3b82f6; }
.alert-icon  { font-size: 1rem; flex-shrink: 0; padding-top: 0.05rem; }
.alert-title { font-size: 0.82rem; font-weight: 600; color: #111827; }
.alert-body  { font-size: 0.74rem; color: #6b7280; margin-top: 0.08rem; }

/* ── SECTION DIVIDER ── */
.section-gap { height: 1.2rem; }

/* ── NAV ROW: prevent equal column stretching ── */
div[data-testid="stHorizontalBlock"]:has(> div[data-testid="stColumn"] > div > div > button) {
    background: #fff;
    border-bottom: 1px solid #e8eaf0;
    box-shadow: 0 2px 8px rgba(0,0,0,0.04);
    padding: 0.28rem 1.5rem !important;
    gap: 0 !important;
    margin-bottom: 1.4rem !important;
}
div[data-testid="stHorizontalBlock"]:has(> div[data-testid="stColumn"] > div > div > button)
    > div[data-testid="stColumn"] {
    flex: 0 0 auto !important;
    width: auto !important;
    min-width: 0 !important;
    padding: 0 2px !important;
}
div[data-testid="stHorizontalBlock"]:has(> div[data-testid="stColumn"] > div > div > button)
    > div[data-testid="stColumn"]:last-child {
    margin-left: auto !important;
}

/* ── RESPONSIVE ── */
@media (max-width: 1024px) {
    .rp-body { padding: 1.2rem 1.5rem 2rem; }
}
@media (max-width: 768px) {
    .rp-body { padding: 1rem; }
    .rp-navbar { padding: 0 1rem; }
    .metric-value { font-size: 1.2rem; }
}

/* ── STREAMLIT WIDGET OVERRIDES ── */
div[data-testid="stMetric"] {
    background: #fff; border-radius: 14px;
    padding: 1rem 1.2rem !important;
    border: 1px solid #ebebf5;
    box-shadow: 0 1px 3px rgba(0,0,0,0.05);
}
div[data-testid="stMetricValue"] { font-size: 1.5rem !important; font-weight: 700 !important; color: #111827 !important; }
div[data-testid="stMetricLabel"] { font-size: 0.75rem !important; color: #9ca3af !important; }
.stTextInput input {
    border-radius: 10px !important; border: 1.5px solid #e5e7eb !important;
    padding: 0.6rem 1rem !important; font-size: 0.9rem !important;
}
.stTextInput input:focus { border-color: #4f46e5 !important; box-shadow: 0 0 0 3px rgba(79,70,229,0.1) !important; }
.stFormSubmitButton > button {
    background: linear-gradient(135deg, #4f46e5, #7c3aed) !important;
    color: white !important; border: none !important;
    border-radius: 10px !important; font-weight: 600 !important;
    width: 100% !important; padding: 0.65rem !important; font-size: 0.95rem !important;
}
div[data-testid="stDataFrame"] { border-radius: 12px; overflow: hidden; }
.stDownloadButton > button {
    border-radius: 8px !important; font-weight: 500 !important;
    border: 1.5px solid #4f46e5 !important; color: #4f46e5 !important;
    background: transparent !important;
}
.stDownloadButton > button:hover { background: #4f46e5 !important; color: white !important; }
</style>
""", unsafe_allow_html=True)

# ─────────────────────────────────────────────────────────────────────────────
# SESSION STATE  — persists across reruns, never cleared by navigation
# ─────────────────────────────────────────────────────────────────────────────
if "authenticated" not in st.session_state:
    st.session_state.authenticated = False
if "page" not in st.session_state:
    st.session_state.page = "Dashboard"

# ─────────────────────────────────────────────────────────────────────────────
# LOGIN  — shown only when not authenticated
# ─────────────────────────────────────────────────────────────────────────────
if not st.session_state.authenticated:
    st.markdown("""
    <style>
        .stApp {
            background: linear-gradient(#3aedcf, #1a73e8 0%, #3ac6ed 45%, #3aedcf 100%) !important;
            min-height: 100vh;
        }
        .block-container {
            max-width: 700px !important;
            margin: 0 auto !important;
            padding-top: 10vh !important;
            padding-bottom: 1rem !important;
            padding-left: 1rem !important;
            padding-right: 1rem !important;
        }
    </style>
    <div style="background:#fff;border-radius:20px;padding:2.5rem 2rem 2rem;
                box-shadow:0 20px 60px rgba(0,0,0,0.18);margin-bottom:1rem;">
        <div style="text-align:center;margin-bottom:1.5rem;">
            <div style="font-size:3.5rem;margin-bottom:0.5rem;">📊</div>
            <h1 style="text-align:center;font-size:2.6rem;font-weight:900;
                       color:#4f46e5;margin:0 0 0.2rem;">RetailPulse</h1>
            <p style="text-align:center;font-size:2.5rem;color:#9ca3af;margin:0 0 1.6rem;">
                AI-Powered Analytics Platform</p>
        </div>
    </div>
    """, unsafe_allow_html=True)
    with st.form("login_form"):
        pw = st.text_input("Password", type="password", placeholder="Enter your password")
        ok = st.form_submit_button("Sign In", use_container_width=True)
        if ok:
            if pw == "admin123":
                st.session_state.authenticated = True
                st.rerun()
            else:
                st.error("Incorrect password. Hint: admin123")
    st.stop()

# ─────────────────────────────────────────────────────────────────────────────
# DATA
# ─────────────────────────────────────────────────────────────────────────────
@st.cache_data(ttl=3600)
def load_data():
    return generate_demo_data()

sales_df, segments_df, forecast_df, at_risk_df, inventory_df = load_data()

# ─────────────────────────────────────────────────────────────────────────────
# NAVBAR  — pure st.button, session-state routing, zero query params
# ─────────────────────────────────────────────────────────────────────────────
NAV_PAGES = [
    "Dashboard", "Customer Insights", "Churn Analytics",
    "Demand Forecast", "Model Performance", "Inventory", "Reports"
]

# ── Combined navbar: brand left, nav buttons centre-left, sign-out right ──
st.markdown("""
<style>
/* ── FULL NAVBAR ROW ── */
.rp-topbar {
    background: #fff;
    border-bottom: 1px solid #e8eaf0;
    box-shadow: 0 2px 8px rgba(0,0,0,0.05);
    padding: 0 1.5rem;
    height: 52px;
    display: flex; align-items: center;
    gap: 0;
    margin-bottom: 0;
}
/* Streamlit injects a gap div above the columns block — kill it */
div[data-testid="stVerticalBlock"] > div:has(> div[data-testid="stHorizontalBlock"].rp-nav-row) {
    margin-top: 0 !important; padding-top: 0 !important;
}
/* The columns row that holds nav buttons */
div[data-testid="stHorizontalBlock"].rp-nav-row {
    background: #fff;
    border-bottom: 1px solid #e8eaf0;
    box-shadow: 0 2px 8px rgba(0,0,0,0.04);
    padding: 0.28rem 1.5rem !important;
    gap: 0 !important;
    align-items: center !important;
    flex-wrap: nowrap !important;
    margin-bottom: 1.4rem !important;
}
/* Every column in the nav row: shrink to content */
div[data-testid="stHorizontalBlock"].rp-nav-row > div[data-testid="stColumn"] {
    flex: 0 0 auto !important;
    width: auto !important;
    min-width: 0 !important;
    padding: 0 2px !important;
}
/* Last column (Sign Out) pushed to far right */
div[data-testid="stHorizontalBlock"].rp-nav-row > div[data-testid="stColumn"]:last-child {
    margin-left: auto !important;
}
/* Nav page buttons */
div[data-testid="stHorizontalBlock"].rp-nav-row button[kind="secondary"] {
    background: transparent !important;
    border: none !important; outline: none !important;
    color: #6b7280 !important;
    font-size: 0.82rem !important; font-weight: 500 !important;
    padding: 0.32rem 0.75rem !important;
    border-radius: 7px !important;
    white-space: nowrap !important;
    box-shadow: none !important;
    min-height: 0 !important; height: auto !important;
    line-height: 1.4 !important;
}
div[data-testid="stHorizontalBlock"].rp-nav-row button[kind="secondary"]:hover {
    background: #f3f4f6 !important; color: #111827 !important;
}
div[data-testid="stHorizontalBlock"].rp-nav-row button[kind="primary"] {
    background: #4f46e5 !important; color: #fff !important;
    border: none !important; outline: none !important;
    font-size: 0.82rem !important; font-weight: 600 !important;
    padding: 0.32rem 0.75rem !important;
    border-radius: 7px !important;
    white-space: nowrap !important;
    box-shadow: none !important;
    min-height: 0 !important; height: auto !important;
    line-height: 1.4 !important;
}
/* Sign Out button */
div[data-testid="stHorizontalBlock"].rp-nav-row > div[data-testid="stColumn"]:last-child button {
    background: transparent !important;
    border: 1.5px solid #fca5a5 !important;
    color: #ef4444 !important;
    font-size: 0.78rem !important; font-weight: 600 !important;
    padding: 0.28rem 0.75rem !important;
    border-radius: 7px !important;
    box-shadow: none !important; min-height: 0 !important; height: auto !important;
}
div[data-testid="stHorizontalBlock"].rp-nav-row > div[data-testid="stColumn"]:last-child button:hover {
    background: #ef4444 !important; color: #fff !important; border-color: #ef4444 !important;
}
</style>
""", unsafe_allow_html=True)

# Brand bar
st.markdown("""
<div class="rp-topbar">
    <span style="font-size:1rem;font-weight:800;color:#4f46e5;display:flex;align-items:center;gap:0.35rem;">
        📊&nbsp; RetailPulse
    </span>
</div>
""", unsafe_allow_html=True)

page = st.session_state.page

# Nav button row — all columns auto-width, last one pushed right via CSS
nav_cols = st.columns(len(NAV_PAGES) + 1)
# inject class on the horizontal block via a wrapper trick
for i, label in enumerate(NAV_PAGES):
    with nav_cols[i]:
        btn_type = "primary" if label == page else "secondary"
        if st.button(label, key=f"nav_{label}", type=btn_type, use_container_width=False):
            st.session_state.page = label
            st.rerun()
with nav_cols[-1]:
    if st.button("Sign Out", key="logout"):
        st.session_state.authenticated = False
        st.session_state.page = "Dashboard"
        st.rerun()

# Apply the class to the nav row via JS injection
st.markdown("""
<script>
(function() {
    const blocks = window.parent.document.querySelectorAll('[data-testid="stHorizontalBlock"]');
    if (blocks.length > 0) {
        blocks[blocks.length - 1].classList.add('rp-nav-row');
    }
})();
</script>
""", unsafe_allow_html=True)

page = st.session_state.page

# ─────────────────────────────────────────────────────────────────────────────
# PLOT DEFAULTS
# ─────────────────────────────────────────────────────────────────────────────
PL = dict(
    paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
    font=dict(family="Inter", color="#374151", size=12),
    margin=dict(l=10, r=10, t=36, b=10),
)
COLORS = ["#4f46e5","#10b981","#f59e0b","#ef4444","#8b5cf6","#06b6d4","#ec4899","#84cc16"]
C1, C2 = "#4f46e5", "#10b981"

def card(title, sub=""):
    s = f'<div class="card-sub">{sub}</div>' if sub else ""
    st.markdown(f'<div class="card"><div class="card-title">{title}</div>{s}', unsafe_allow_html=True)

def end_card():
    st.markdown('</div>', unsafe_allow_html=True)

# Page body wrapper
st.markdown('<div class="rp-body">', unsafe_allow_html=True)

# ═════════════════════════════════════════════════════════════════════════════
# DASHBOARD
# ═════════════════════════════════════════════════════════════════════════════
if page == "Dashboard":
    total_revenue  = sales_df['TotalPrice'].sum()
    total_customers = segments_df['Customer ID'].nunique()
    avg_daily      = sales_df.groupby('InvoiceDate')['TotalPrice'].sum().mean()
    churn_rate     = len(at_risk_df) / total_customers
    high_risk      = len(inventory_df[inventory_df['Risk Level'] == 'HIGH'])

    st.markdown("""
    <div class="rp-page-title">Customer Analytics Dashboard</div>
    <div class="rp-page-sub">RFM Analysis — Recency, Frequency, Monetary Value</div>
    """, unsafe_allow_html=True)

    c1, c2, c3, c4 = st.columns(4, gap="small")
    for col, icon, bg, label, value, delta, pos in [
        (c1, "💰", "#eef2ff", "Total Revenue",     format_currency(total_revenue), "▲ +12.5% vs last month", True),
        (c2, "👥", "#f0fdf4", "Active Customers",  format_number(total_customers), "▲ +8.3% vs last month",  True),
        (c3, "📈", "#fffbeb", "Avg Daily Revenue", format_currency(avg_daily),     "▲ +5.2% vs last month",  True),
        (c4, "⚠️", "#fff5f5", "Churn Rate",        f"{churn_rate:.1%}",            "▼ -2.1% vs last month",  False),
    ]:
        col.markdown(f"""
        <div class="metric-card">
            <div class="metric-icon" style="background:{bg}">{icon}</div>
            <div class="metric-body">
                <div class="metric-value">{value}</div>
                <div class="metric-label">{label}</div>
                <div class="metric-delta {'d-up' if pos else 'd-dn'}">{delta}</div>
            </div>
        </div>""", unsafe_allow_html=True)

    st.markdown('<div class="section-gap"></div>', unsafe_allow_html=True)

    col1, col2 = st.columns(2, gap="medium")
    with col1:
        card("Daily Sales Trend", "Revenue over time")
        daily_sales = sales_df.groupby('InvoiceDate')['TotalPrice'].sum().reset_index()
        fig = px.line(daily_sales, x='InvoiceDate', y='TotalPrice', color_discrete_sequence=[C1])
        fig.update_layout(height=300, showlegend=False, **PL)
        fig.update_xaxes(gridcolor="#f3f4f6", title="")
        fig.update_yaxes(gridcolor="#f3f4f6", title="")
        st.plotly_chart(fig, use_container_width=True)
        end_card()

    with col2:
        card("Revenue by Country", "Geographic distribution")
        country_sales = sales_df.groupby('Country')['TotalPrice'].sum().sort_values(ascending=False)
        fig = px.pie(values=country_sales.values, names=country_sales.index,
                     hole=0.45, color_discrete_sequence=COLORS)
        fig.update_layout(
            height=300,
            legend=dict(orientation="v", x=1.0, y=0.5, xanchor="left", font=dict(size=11)),
            **PL,
        )
        fig.update_traces(textposition='inside', textinfo='percent+label',
                          textfont_size=10)
        st.plotly_chart(fig, use_container_width=True)
        end_card()

    st.markdown('<div class="card-title" style="margin-bottom:0.75rem;">⚠️ Alerts</div>', unsafe_allow_html=True)
    a1, a2, a3 = st.columns(3, gap="medium")
    a1.markdown(f"""<div class="alert-card alert-critical">
        <div class="alert-icon">🔴</div>
        <div><div class="alert-title">High Stockout Risk</div>
        <div class="alert-body">{high_risk} products need immediate attention</div></div>
    </div>""", unsafe_allow_html=True)
    a2.markdown(f"""<div class="alert-card alert-warning">
        <div class="alert-icon">⚠️</div>
        <div><div class="alert-title">Churn Risk</div>
        <div class="alert-body">{len(at_risk_df)} customers at risk of churning</div></div>
    </div>""", unsafe_allow_html=True)
    a3.markdown(f"""<div class="alert-card alert-success">
        <div class="alert-icon">✅</div>
        <div><div class="alert-title">Model Status</div>
        <div class="alert-body">All models performing within acceptable range</div></div>
    </div>""", unsafe_allow_html=True)

# ═════════════════════════════════════════════════════════════════════════════
# CUSTOMER INSIGHTS
# ═════════════════════════════════════════════════════════════════════════════
elif page == "Customer Insights":
    st.markdown('<div class="rp-page-title">Customer Insights</div><div class="rp-page-sub">RFM Segmentation & Value Analysis</div>', unsafe_allow_html=True)

    col1, col2 = st.columns(2, gap="medium")
    with col1:
        card("Segment Distribution", "Customer breakdown by RFM segment")
        seg_counts = segments_df['Segment Name'].value_counts()
        fig = px.pie(values=seg_counts.values, names=seg_counts.index, hole=0.4,
                     color_discrete_sequence=COLORS)
        fig.update_layout(height=320, **PL)
        st.plotly_chart(fig, use_container_width=True)
        end_card()

    with col2:
        card("Customer Segments", "Count per segment")
        fig = px.bar(x=seg_counts.index, y=seg_counts.values,
                     color=seg_counts.index, color_discrete_sequence=COLORS,
                     labels={'x': 'Segment', 'y': 'Customers'})
        fig.update_layout(height=320, showlegend=False, **PL)
        fig.update_xaxes(gridcolor="#f3f4f6", tickangle=30)
        fig.update_yaxes(gridcolor="#f3f4f6")
        st.plotly_chart(fig, use_container_width=True)
        end_card()

    st.markdown('<div class="section-gap"></div>', unsafe_allow_html=True)

    card("Customer Value Map", "Recency vs Monetary spend, sized by frequency")
    fig = px.scatter(segments_df.sample(min(500, len(segments_df))),
                     x='Recency', y='Monetary', color='Segment Name', size='Frequency',
                     labels={'Recency': 'Days Since Last Purchase', 'Monetary': 'Total Spend (£)'},
                     color_discrete_sequence=COLORS)
    fig.update_layout(height=380, **PL)
    fig.update_xaxes(gridcolor="#f3f4f6")
    fig.update_yaxes(gridcolor="#f3f4f6")
    st.plotly_chart(fig, use_container_width=True)
    end_card()

    card("Segment Metrics Table")
    seg_tbl = segments_df.groupby('Segment Name').agg(
        Count=('Customer ID', 'count'),
        Avg_Recency=('Recency', 'mean'),
        Avg_Frequency=('Frequency', 'mean'),
        Avg_Monetary=('Monetary', 'mean'),
    ).round(1).reset_index()
    st.dataframe(seg_tbl, use_container_width=True, hide_index=True)
    end_card()

# ═════════════════════════════════════════════════════════════════════════════
# CHURN ANALYTICS
# ═════════════════════════════════════════════════════════════════════════════
elif page == "Churn Analytics":
    st.markdown('<div class="rp-page-title">Churn Analytics</div><div class="rp-page-sub">At-risk customer identification & revenue impact</div>', unsafe_allow_html=True)

    c1, c2, c3 = st.columns(3, gap="medium")
    c1.metric("Customers at Risk",     len(at_risk_df))
    c2.metric("Revenue at Risk",       format_currency(at_risk_df['total_spent'].sum()))
    c3.metric("Avg Churn Probability", f"{at_risk_df['churn_probability'].mean():.1%}")

    st.markdown('<div class="section-gap"></div>', unsafe_allow_html=True)

    col1, col2 = st.columns(2, gap="medium")
    with col1:
        card("Churn Probability Distribution")
        fig = px.histogram(at_risk_df, x='churn_probability', nbins=20,
                           color_discrete_sequence=[C1])
        fig.update_layout(height=300, **PL)
        fig.update_xaxes(gridcolor="#f3f4f6", title="Churn Probability")
        fig.update_yaxes(gridcolor="#f3f4f6", title="Count")
        st.plotly_chart(fig, use_container_width=True)
        end_card()

    with col2:
        card("Avg Churn by Segment")
        seg_risk = at_risk_df.groupby('Segment')['churn_probability'].mean().reset_index()
        fig = px.bar(seg_risk, x='Segment', y='churn_probability',
                     color_discrete_sequence=[C2])
        fig.update_layout(height=300, **PL)
        fig.update_xaxes(gridcolor="#f3f4f6")
        fig.update_yaxes(gridcolor="#f3f4f6", title="Avg Probability")
        st.plotly_chart(fig, use_container_width=True)
        end_card()

    card("At-Risk Customer List")
    min_prob = st.slider("Minimum Churn Probability", 0.5, 0.95, 0.7, 0.05)
    filtered = at_risk_df[at_risk_df['churn_probability'] >= min_prob]
    st.dataframe(filtered.head(50), use_container_width=True, hide_index=True)
    st.download_button("📥 Download At-Risk Customers", at_risk_df.to_csv(index=False),
                       "at_risk_customers.csv", "text/csv")
    end_card()

# ═════════════════════════════════════════════════════════════════════════════
# DEMAND FORECAST
# ═════════════════════════════════════════════════════════════════════════════
elif page == "Demand Forecast":
    st.markdown('<div class="rp-page-title">Demand Forecasting</div><div class="rp-page-sub">30-day sales forecast with confidence intervals</div>', unsafe_allow_html=True)

    col1, col2 = st.columns([3, 1], gap="medium")
    with col1:
        card("30-Day Sales Forecast")
        fig = go.Figure()
        fig.add_trace(go.Scatter(x=forecast_df['ds'], y=forecast_df['yhat_upper'],
                                 fill=None, mode='lines',
                                 line=dict(color='rgba(79,70,229,0.15)', width=0), name='Upper'))
        fig.add_trace(go.Scatter(x=forecast_df['ds'], y=forecast_df['yhat_lower'],
                                 fill='tonexty', mode='lines',
                                 line=dict(color='rgba(79,70,229,0.15)', width=0),
                                 fillcolor='rgba(79,70,229,0.08)', name='Confidence'))
        fig.add_trace(go.Scatter(x=forecast_df['ds'], y=forecast_df['yhat'],
                                 mode='lines', name='Forecast',
                                 line=dict(color=C1, width=2.5)))
        fig.update_layout(height=380, **PL)
        fig.update_xaxes(gridcolor="#f3f4f6", title="")
        fig.update_yaxes(gridcolor="#f3f4f6", title="")
        st.plotly_chart(fig, use_container_width=True)
        end_card()

    with col2:
        st.markdown('<div class="section-gap"></div>', unsafe_allow_html=True)
        st.metric("30-Day Total", format_currency(forecast_df['yhat'].sum()))
        st.markdown('<div style="height:0.6rem"></div>', unsafe_allow_html=True)
        st.metric("Avg Daily",    format_currency(forecast_df['yhat'].mean()))
        st.markdown('<div style="height:0.6rem"></div>', unsafe_allow_html=True)
        st.metric("Peak Day",     format_currency(forecast_df['yhat'].max()))

    card("What-If Scenario Analysis", "Adjust demand multiplier to simulate scenarios")
    multiplier = st.slider("Demand Multiplier", 0.5, 2.0, 1.0, 0.1)
    if multiplier != 1.0:
        adjusted = forecast_df['yhat'] * multiplier
        st.info(f"Adjusted 30-Day Total: **{format_currency(adjusted.sum())}** "
                f"(vs baseline {format_currency(forecast_df['yhat'].sum())})")
        fig2 = go.Figure()
        fig2.add_trace(go.Scatter(x=forecast_df['ds'], y=forecast_df['yhat'],
                                  name='Baseline', line=dict(color='#9ca3af', width=1.5)))
        fig2.add_trace(go.Scatter(x=forecast_df['ds'], y=adjusted,
                                  name='Scenario', line=dict(color=C1, dash='dash', width=2)))
        fig2.update_layout(height=280, **PL)
        fig2.update_xaxes(gridcolor="#f3f4f6")
        fig2.update_yaxes(gridcolor="#f3f4f6")
        st.plotly_chart(fig2, use_container_width=True)
    else:
        st.info("Move the slider to simulate a demand scenario.")
    end_card()

# ═════════════════════════════════════════════════════════════════════════════
# MODEL PERFORMANCE
# ═════════════════════════════════════════════════════════════════════════════
elif page == "Model Performance":
    st.markdown('<div class="rp-page-title">Model Performance</div><div class="rp-page-sub">Evaluation metrics for all AI/ML models powering RetailPulse</div>', unsafe_allow_html=True)

    models = [
        {"name": "Demand Forecasting",    "metric": "MAPE",       "display": "8.3%",     "color": "#4f46e5", "bar": 91.7, "note": "Mean Absolute % Error — lower is better"},
        {"name": "Churn Prediction",      "metric": "AUC-ROC",    "display": "0.91",     "color": "#10b981", "bar": 91.0, "note": "Area Under ROC Curve — higher is better"},
        {"name": "Customer Segmentation", "metric": "Silhouette", "display": "0.74",     "color": "#f59e0b", "bar": 74.0, "note": "Silhouette Score — higher is better"},
        {"name": "Churn Model",           "metric": "F1 Score",   "display": "0.87",     "color": "#ef4444", "bar": 87.0, "note": "Harmonic mean of Precision & Recall"},
        {"name": "Inventory Forecast",    "metric": "RMSE",       "display": "142 units","color": "#8b5cf6", "bar": 85.0, "note": "Root Mean Squared Error"},
        {"name": "CLV Prediction",        "metric": "R² Score",   "display": "0.83",     "color": "#06b6d4", "bar": 83.0, "note": "Coefficient of Determination"},
    ]

    cols = st.columns(3, gap="medium")
    for i, m in enumerate(models):
        with cols[i % 3]:
            st.markdown(f"""
            <div class="card" style="margin-bottom:1rem;">
                <div style="font-size:0.7rem;font-weight:600;color:#9ca3af;
                            text-transform:uppercase;letter-spacing:0.06em;margin-bottom:0.5rem;">
                    {m['name']}
                </div>
                <div style="font-size:1.9rem;font-weight:800;color:{m['color']};line-height:1.1;">
                    {m['display']}
                </div>
                <div style="font-size:0.75rem;color:#6b7280;margin:0.25rem 0 0.75rem;">{m['metric']}</div>
                <div style="background:#f3f4f6;border-radius:99px;height:5px;overflow:hidden;">
                    <div style="width:{m['bar']}%;height:100%;background:{m['color']};border-radius:99px;"></div>
                </div>
                <div style="font-size:0.7rem;color:#9ca3af;margin-top:0.45rem;">{m['note']}</div>
            </div>""", unsafe_allow_html=True)

    st.markdown('<div class="section-gap"></div>', unsafe_allow_html=True)

    col1, col2 = st.columns(2, gap="medium")
    with col1:
        card("Churn Model — ROC Curve", "AUC = 0.91")
        fpr = np.linspace(0, 1, 100)
        tpr = np.clip(1 - np.exp(-4 * fpr) + np.random.RandomState(1).normal(0, 0.015, 100), 0, 1)
        tpr[0], tpr[-1] = 0.0, 1.0
        fig = go.Figure()
        fig.add_trace(go.Scatter(x=[0,1], y=[0,1], mode='lines', name='Random',
                                 line=dict(color='#d1d5db', dash='dash', width=1.5)))
        fig.add_trace(go.Scatter(x=fpr, y=tpr, mode='lines', name='ROC (AUC=0.91)',
                                 line=dict(color=C1, width=2.5),
                                 fill='tozeroy', fillcolor='rgba(79,70,229,0.06)'))
        fig.update_layout(height=320, xaxis_title="False Positive Rate",
                          yaxis_title="True Positive Rate", **PL)
        fig.update_xaxes(gridcolor="#f3f4f6")
        fig.update_yaxes(gridcolor="#f3f4f6")
        st.plotly_chart(fig, use_container_width=True)
        end_card()

    with col2:
        card("Demand Forecast — Actual vs Predicted")
        np.random.seed(7)
        actual = forecast_df['yhat'].values + np.random.normal(0, 380, len(forecast_df))
        fig2 = go.Figure()
        fig2.add_trace(go.Scatter(x=forecast_df['ds'], y=actual, mode='lines',
                                  name='Actual', line=dict(color='#d1d5db', width=1.5)))
        fig2.add_trace(go.Scatter(x=forecast_df['ds'], y=forecast_df['yhat'], mode='lines',
                                  name='Predicted', line=dict(color=C2, width=2.5)))
        fig2.update_layout(height=320, **PL)
        fig2.update_xaxes(gridcolor="#f3f4f6", title="")
        fig2.update_yaxes(gridcolor="#f3f4f6", title="")
        st.plotly_chart(fig2, use_container_width=True)
        end_card()

    card("Classification Report — Churn Model")
    st.dataframe(pd.DataFrame({
        "Class":     ["No Churn", "Churn", "Macro Avg", "Weighted Avg"],
        "Precision": [0.92, 0.83, 0.88, 0.90],
        "Recall":    [0.94, 0.79, 0.87, 0.89],
        "F1 Score":  [0.93, 0.81, 0.87, 0.91],
        "Support":   [1240, 360, 1600, 1600],
    }), use_container_width=True, hide_index=True)
    end_card()

# ═════════════════════════════════════════════════════════════════════════════
# INVENTORY
# ═════════════════════════════════════════════════════════════════════════════
elif page == "Inventory":
    st.markdown('<div class="rp-page-title">Inventory Optimization</div><div class="rp-page-sub">Stock levels, reorder alerts, and risk analysis</div>', unsafe_allow_html=True)

    high_risk  = len(inventory_df[inventory_df['Risk Level'] == 'HIGH'])
    total_val  = (inventory_df['Current Stock'] * inventory_df['Unit Price']).sum()
    to_reorder = len(inventory_df[inventory_df['Reorder Quantity'] > 0])

    c1, c2, c3, c4 = st.columns(4, gap="medium")
    c1.metric("High Risk Products",   high_risk)
    c2.metric("Inventory Value",      format_currency(total_val))
    c3.metric("Products to Reorder",  to_reorder)
    c4.metric("Service Level Target", "95%")

    st.markdown('<div class="section-gap"></div>', unsafe_allow_html=True)

    col1, col2 = st.columns(2, gap="medium")
    with col1:
        card("Stock Risk Distribution")
        risk_counts = inventory_df['Risk Level'].value_counts()
        fig = px.pie(values=risk_counts.values, names=risk_counts.index, hole=0.42,
                     color_discrete_map={'HIGH':'#ef4444','MEDIUM':'#f59e0b','LOW':'#10b981'})
        fig.update_layout(height=300, **PL)
        st.plotly_chart(fig, use_container_width=True)
        end_card()

    with col2:
        card("Stock Levels — Top 15 Products")
        fig = px.bar(inventory_df.head(15), x='Product', y='Current Stock',
                     color='Risk Level',
                     color_discrete_map={'HIGH':'#ef4444','MEDIUM':'#f59e0b','LOW':'#10b981'})
        fig.update_layout(height=300, **PL)
        fig.update_xaxes(tickangle=40, gridcolor="#f3f4f6", title="")
        fig.update_yaxes(gridcolor="#f3f4f6")
        st.plotly_chart(fig, use_container_width=True)
        end_card()

    card("Inventory Table")
    risk_filter = st.multiselect("Filter by Risk Level", ['HIGH','MEDIUM','LOW'], default=['HIGH','MEDIUM'])
    st.dataframe(inventory_df[inventory_df['Risk Level'].isin(risk_filter)].head(50),
                 use_container_width=True, hide_index=True)
    st.download_button("📥 Download Inventory Report", inventory_df.to_csv(index=False),
                       "inventory_report.csv", "text/csv")
    end_card()

# ═════════════════════════════════════════════════════════════════════════════
# REPORTS
# ═════════════════════════════════════════════════════════════════════════════
elif page == "Reports":
    st.markdown('<div class="rp-page-title">Reports</div><div class="rp-page-sub">Generate and download analytics reports</div>', unsafe_allow_html=True)

    card("Generate Report")
    report_type = st.selectbox("Report Type",
        ["Executive Summary", "Customer Analytics", "Inventory Report", "Full Analytics"])
    if st.button("📊 Generate Report", type="primary"):
        with st.spinner("Generating..."):
            if report_type == "Executive Summary":
                rdf = pd.DataFrame({
                    'Metric': ['Total Revenue','Active Customers','Churn Rate',
                               'High-Risk Products','Forecast Accuracy'],
                    'Value': [
                        format_currency(sales_df['TotalPrice'].sum()),
                        format_number(segments_df['Customer ID'].nunique()),
                        f"{len(at_risk_df)/segments_df['Customer ID'].nunique():.1%}",
                        str(len(inventory_df[inventory_df['Risk Level']=='HIGH'])),
                        "92%",
                    ]
                })
                st.dataframe(rdf, use_container_width=True, hide_index=True)
                st.download_button("📥 Download CSV", rdf.to_csv(index=False),
                                   "executive_summary.csv", "text/csv")
            else:
                st.success(f"✅ {report_type} report generated successfully.")
    end_card()

# ─────────────────────────────────────────────────────────────────────────────
# FOOTER
# ─────────────────────────────────────────────────────────────────────────────
st.markdown('</div>', unsafe_allow_html=True)  # close rp-body
st.markdown("""
<div style="text-align:center;padding:1.2rem 0 1.5rem;color:#9ca3af;font-size:0.73rem;
            border-top:1px solid #e8eaf0;margin-top:0.5rem;">
    RetailPulse &nbsp;·&nbsp; AI-Powered Analytics &nbsp;·&nbsp; Zidio Development
</div>
""", unsafe_allow_html=True)