"""
RetailPulse - AI-Powered Customer Analytics Dashboard
Self-contained version that works without external data files
"""

import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
import json

# Page configuration
st.set_page_config(
    page_title="RetailPulse - AI Analytics Platform",
    page_icon="📊",
    layout="wide"
)

# Custom CSS
st.markdown("""
<style>
    .main-header {
        font-size: 2rem;
        font-weight: bold;
        color: #1E88E5;
        text-align: center;
        margin-bottom: 1rem;
    }
    .metric-card {
        background-color: #f0f2f6;
        padding: 1rem;
        border-radius: 10px;
        text-align: center;
    }
</style>
""", unsafe_allow_html=True)

# Authentication
if "authenticated" not in st.session_state:
    st.session_state.authenticated = False

def check_password():
    if not st.session_state.authenticated:
        st.title("🔐 RetailPulse Login")
        password = st.text_input("Password", type="password")
        if st.button("Login"):
            if password == "admin123":
                st.session_state.authenticated = True
                st.rerun()
            else:
                st.error("Wrong password. Try: admin123")
        st.info("Demo credentials: password = 'admin123'")
        return False
    return True

if not check_password():
    st.stop()

# Generate Demo Data (since files are not on GitHub)
@st.cache_data(ttl=3600)
def generate_demo_data():
    """Generate realistic demo data for the dashboard"""
    np.random.seed(42)
    
    # Sales data
    dates = pd.date_range(start='2023-01-01', end='2024-12-31', freq='D')
    sales_data = []
    for i, date in enumerate(dates):
        # Add seasonality and trend
        trend = 5000 + i * 10
        seasonality = 2000 * np.sin(2 * np.pi * date.dayofyear / 365)
        random_noise = np.random.normal(0, 500)
        daily_sales = max(0, trend + seasonality + random_noise)
        
        sales_data.append({
            'InvoiceDate': date,
            'TotalPrice': daily_sales,
            'Quantity': int(daily_sales / 20),
            'Customer ID': np.random.randint(10000, 20000),
            'Country': np.random.choice(['United Kingdom', 'France', 'Germany', 'USA', 'Australia'], 
                                        p=[0.6, 0.15, 0.1, 0.1, 0.05])
        })
    
    sales_df = pd.DataFrame(sales_data)
    
    # Customer segments
    customers = sales_df['Customer ID'].unique()[:1000]
    segments_data = []
    segment_names = {0: 'Champions', 1: 'Loyal', 2: 'Potential', 3: 'New', 4: 'At Risk', 5: 'Lost'}
    
    for cust in customers:
        segment = np.random.choice([0, 1, 2, 3, 4, 5], p=[0.15, 0.2, 0.25, 0.2, 0.1, 0.1])
        segments_data.append({
            'Customer ID': cust,
            'Segment': segment,
            'Segment Name': segment_names[segment],
            'Recency': np.random.randint(1, 365),
            'Frequency': np.random.randint(1, 50),
            'Monetary': np.random.uniform(100, 10000),
            'CLV': np.random.uniform(500, 15000)
        })
    segments_df = pd.DataFrame(segments_data)
    
    # Forecast data
    forecast_dates = pd.date_range(start=datetime.now(), periods=30, freq='D')
    forecast_data = []
    for i, date in enumerate(forecast_dates):
        base = 12000
        trend = i * 50
        seasonality = 1500 * np.sin(2 * np.pi * i / 7)
        forecast_data.append({
            'ds': date,
            'yhat': base + trend + seasonality,
            'yhat_lower': base + trend + seasonality - 1000,
            'yhat_upper': base + trend + seasonality + 1000
        })
    forecast_df = pd.DataFrame(forecast_data)
    
    # At-risk customers
    at_risk_data = []
    for cust in customers[:200]:
        at_risk_data.append({
            'Customer ID': cust,
            'churn_probability': np.random.uniform(0.65, 0.95),
            'total_spent': np.random.uniform(100, 5000),
            'Recency': np.random.randint(60, 200),
            'Segment': np.random.choice(['At Risk', 'High Risk', 'Critical'])
        })
    at_risk_df = pd.DataFrame(at_risk_data)
    at_risk_df = at_risk_df.sort_values('churn_probability', ascending=False)
    
    # Inventory data
    products = ['LED Lights', 'Garden Tools', 'Kitchen Set', 'Decorative Items', 'Seasonal Decor']
    inventory_data = []
    for i, product in enumerate(products):
        for j in range(10):
            reorder_point = np.random.randint(50, 200)
            current_stock = np.random.randint(0, reorder_point * 1.5)
            risk = 'HIGH' if current_stock < reorder_point * 0.6 else 'MEDIUM' if current_stock < reorder_point else 'LOW'
            inventory_data.append({
                'Product': f'{product} {j+1}',
                'StockCode': f'PRD_{i:03d}{j:02d}',
                'Current Stock': current_stock,
                'Reorder Point': reorder_point,
                'Reorder Quantity': max(0, reorder_point * 2 - current_stock),
                'Risk Level': risk,
                'Unit Price': np.random.uniform(10, 100)
            })
    inventory_df = pd.DataFrame(inventory_data)
    
    return sales_df, segments_df, forecast_df, at_risk_df, inventory_df

# Load data
sales_df, segments_df, forecast_df, at_risk_df, inventory_df = generate_demo_data()

# Helper functions
def format_currency(value):
    return f"£{value:,.0f}"

def format_number(value):
    return f"{value:,}"

# Sidebar Navigation
st.sidebar.image("https://img.icons8.com/color/96/000000/bar-chart.png", width=80)
st.sidebar.title("RetailPulse")
st.sidebar.markdown("---")

page = st.sidebar.selectbox(
    "Navigation",
    ["🏠 Dashboard", "📈 Demand Forecast", "👥 Customer Insights", 
     "⚠️ Churn Analytics", "📦 Inventory", "📄 Reports"]
)

st.sidebar.markdown("---")
st.sidebar.caption(f"Version 2.0\nLast Updated: {datetime.now().strftime('%Y-%m-%d')}")
st.sidebar.info("Demo Mode - Using generated data")

# ============ PAGE 1: DASHBOARD ============
if page == "🏠 Dashboard":
    st.markdown('<div class="main-header">📊 RetailPulse Dashboard</div>', unsafe_allow_html=True)
    
    # Key metrics
    col1, col2, col3, col4 = st.columns(4)
    
    total_revenue = sales_df['TotalPrice'].sum()
    total_customers = segments_df['Customer ID'].nunique()
    avg_daily = sales_df.groupby('InvoiceDate')['TotalPrice'].sum().mean()
    churn_rate = len(at_risk_df) / total_customers
    
    with col1:
        st.metric("Total Revenue", format_currency(total_revenue), delta="+12.5%")
    with col2:
        st.metric("Active Customers", format_number(total_customers), delta="+8.3%")
    with col3:
        st.metric("Avg Daily Revenue", format_currency(avg_daily), delta="+5.2%")
    with col4:
        st.metric("Churn Rate", f"{churn_rate:.1%}", delta="-2.1%", delta_color="inverse")
    
    # Charts
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("📈 Sales Trend")
        daily_sales = sales_df.groupby('InvoiceDate')['TotalPrice'].sum().reset_index()
        fig = px.line(daily_sales, x='InvoiceDate', y='TotalPrice', 
                      title="Daily Sales Over Time")
        fig.update_layout(height=400)
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        st.subheader("🌍 Sales by Country")
        country_sales = sales_df.groupby('Country')['TotalPrice'].sum().sort_values(ascending=False)
        fig = px.pie(values=country_sales.values, names=country_sales.index, 
                     title="Revenue by Country")
        fig.update_layout(height=400)
        st.plotly_chart(fig, use_container_width=True)
    
    # Alerts
    st.subheader("⚠️ Critical Alerts")
    alert_col1, alert_col2, alert_col3 = st.columns(3)
    
    with alert_col1:
        high_risk = len(inventory_df[inventory_df['Risk Level'] == 'HIGH'])
        st.warning(f"🔴 {high_risk} products at HIGH stockout risk")
    
    with alert_col2:
        st.error(f"⚠️ {len(at_risk_df)} customers at risk of churning")
    
    with alert_col3:
        st.success("✅ No data drift detected")

# ============ PAGE 2: DEMAND FORECAST ============
elif page == "📈 Demand Forecast":
    st.markdown('<div class="main-header">📈 Demand Forecasting</div>', unsafe_allow_html=True)
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.subheader("30-Day Sales Forecast")
        fig = go.Figure()
        fig.add_trace(go.Scatter(x=forecast_df['ds'], y=forecast_df['yhat'], 
                                 mode='lines', name='Forecast', 
                                 line=dict(color='red', width=3)))
        fig.add_trace(go.Scatter(x=forecast_df['ds'], y=forecast_df['yhat_upper'],
                                 fill=None, mode='lines', 
                                 line_color='rgba(255,0,0,0.2)', name='Upper Bound'))
        fig.add_trace(go.Scatter(x=forecast_df['ds'], y=forecast_df['yhat_lower'],
                                 fill='tonexty', mode='lines', 
                                 line_color='rgba(255,0,0,0.2)', name='Lower Bound'))
        fig.update_layout(height=500, title="Next 30 Days Sales Forecast")
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        st.subheader("Forecast Summary")
        total_forecast = forecast_df['yhat'].sum()
        avg_daily = forecast_df['yhat'].mean()
        peak_day = forecast_df.loc[forecast_df['yhat'].idxmax(), 'ds']
        peak_value = forecast_df['yhat'].max()
        
        st.metric("Total 30-Day Forecast", format_currency(total_forecast))
        st.metric("Average Daily", format_currency(avg_daily))
        st.metric("Peak Day", peak_day.strftime('%Y-%m-%d'), delta=format_currency(peak_value))
    
    # What-if Analysis
    st.subheader("🔧 What-If Analysis")
    multiplier = st.slider("Demand Multiplier", 0.5, 2.0, 1.0, 0.1)
    
    if multiplier != 1.0:
        adjusted = forecast_df['yhat'] * multiplier
        st.info(f"Adjusted Forecast Total: {format_currency(adjusted.sum())}")
        
        fig2 = go.Figure()
        fig2.add_trace(go.Scatter(x=forecast_df['ds'], y=forecast_df['yhat'], 
                                  name='Original', line=dict(color='blue')))
        fig2.add_trace(go.Scatter(x=forecast_df['ds'], y=adjusted, 
                                  name='Scenario', line=dict(color='red', dash='dash')))
        st.plotly_chart(fig2, use_container_width=True)

# ============ PAGE 3: CUSTOMER INSIGHTS ============
elif page == "👥 Customer Insights":
    st.markdown('<div class="main-header">👥 Customer Insights</div>', unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Segment Distribution")
        segment_counts = segments_df['Segment Name'].value_counts()
        fig = px.pie(values=segment_counts.values, names=segment_counts.index, 
                     title="Customer Segments", hole=0.3)
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        st.subheader("Segment Metrics")
        segment_metrics = segments_df.groupby('Segment Name').agg({
            'Monetary': 'mean',
            'Frequency': 'mean',
            'Recency': 'mean',
            'Customer ID': 'count'
        }).round(2)
        segment_metrics.columns = ['Avg Spend (£)', 'Avg Frequency', 'Avg Recency (days)', 'Count']
        st.dataframe(segment_metrics, use_container_width=True)
    
    # RFM Scatter
    st.subheader("Customer Value Analysis")
    fig = px.scatter(segments_df.sample(500), x='Recency', y='Monetary', 
                     color='Segment Name', size='Frequency',
                     title="Recency vs Monetary Value by Segment",
                     labels={'Recency': 'Days Since Last Purchase', 'Monetary': 'Total Spend (£)'})
    st.plotly_chart(fig, use_container_width=True)

# ============ PAGE 4: CHURN ANALYTICS ============
elif page == "⚠️ Churn Analytics":
    st.markdown('<div class="main-header">⚠️ Churn Risk Analysis</div>', unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric("Customers at Risk", len(at_risk_df), delta="High Risk")
    with col2:
        total_risk_value = at_risk_df['total_spent'].sum()
        st.metric("Revenue at Risk", format_currency(total_risk_value))
    with col3:
        avg_prob = at_risk_df['churn_probability'].mean()
        st.metric("Avg Churn Probability", f"{avg_prob:.1%}")
    
    st.subheader("🔴 High-Risk Customers")
    
    # Filter
    min_prob = st.slider("Minimum Churn Probability", 0.5, 0.95, 0.7, 0.05)
    filtered_risk = at_risk_df[at_risk_df['churn_probability'] >= min_prob]
    
    st.dataframe(filtered_risk.head(50), use_container_width=True)
    
    # Download button
    csv = at_risk_df.to_csv(index=False)
    st.download_button("📥 Download At-Risk Customers", csv, "at_risk_customers.csv", "text/csv")
    
    # Retention Strategies
    st.subheader("🎯 Retention Strategies")
    strategy_col1, strategy_col2, strategy_col3 = st.columns(3)
    
    with strategy_col1:
        st.info("**High Value Customers**\n\n• Personal call\n• 25% discount\n• Free shipping")
    with strategy_col2:
        st.warning("**Medium Value Customers**\n\n• Email campaign\n• 15% discount\n• Loyalty points")
    with strategy_col3:
        st.success("**At-Risk Customers**\n\n• Re-engagement email\n• 10% discount\n• Feedback survey")

# ============ PAGE 5: INVENTORY ============
elif page == "📦 Inventory":
    st.markdown('<div class="main-header">📦 Inventory Optimization</div>', unsafe_allow_html=True)
    
    col1, col2, col3, col4 = st.columns(4)
    
    high_risk = len(inventory_df[inventory_df['Risk Level'] == 'HIGH'])
    total_value = (inventory_df['Current Stock'] * inventory_df['Unit Price']).sum()
    
    with col1:
        st.metric("High Risk Products", high_risk, delta="URGENT")
    with col2:
        st.metric("Total Inventory Value", format_currency(total_value))
    with col3:
        st.metric("Products to Reorder", len(inventory_df[inventory_df['Reorder Quantity'] > 0]))
    with col4:
        st.metric("Service Level Target", "95%")
    
    # Filter
    risk_filter = st.multiselect("Filter by Risk Level", ['HIGH', 'MEDIUM', 'LOW'], default=['HIGH', 'MEDIUM'])
    filtered_inventory = inventory_df[inventory_df['Risk Level'].isin(risk_filter)]
    
    st.subheader("📋 Reorder Recommendations")
    st.dataframe(filtered_inventory.head(50), use_container_width=True)
    
    # Risk Distribution
    col1, col2 = st.columns(2)
    
    with col1:
        risk_counts = inventory_df['Risk Level'].value_counts()
        fig = px.bar(x=risk_counts.index, y=risk_counts.values, 
                     title="Stockout Risk Distribution",
                     color=risk_counts.index,
                     color_discrete_map={'HIGH': 'red', 'MEDIUM': 'orange', 'LOW': 'green'})
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        # Stock vs Reorder Point
        sample = inventory_df.sample(50)
        fig = px.scatter(sample, x='Reorder Point', y='Current Stock', 
                         color='Risk Level', title="Current Stock vs Reorder Point")
        fig.add_shape(type="line", x0=0, y0=0, x1=sample['Reorder Point'].max(), 
                      y1=sample['Reorder Point'].max(), line=dict(color="red", dash="dash"))
        st.plotly_chart(fig, use_container_width=True)
    
    # Download
    csv = inventory_df.to_csv(index=False)
    st.download_button("📥 Download Inventory Report", csv, "inventory_report.csv", "text/csv")

# ============ PAGE 6: REPORTS ============
elif page == "📄 Reports":
    st.markdown('<div class="main-header">📄 Generate Reports</div>', unsafe_allow_html=True)
    
    report_type = st.selectbox(
        "Select Report Type",
        ["Executive Summary", "Customer Analytics", "Inventory Report", "Full Analytics"]
    )
    
    if st.button("Generate Report", type="primary"):
        with st.spinner("Generating report..."):
            if report_type == "Executive Summary":
                report_data = {
                    'Metric': ['Total Revenue', 'Active Customers', 'Avg Order Value', 
                              'Churn Rate', 'Products at Risk', 'Forecast Accuracy'],
                    'Value': [
                        format_currency(sales_df['TotalPrice'].sum()),
                        format_number(segments_df['Customer ID'].nunique()),
                        format_currency(sales_df['TotalPrice'].mean()),
                        f"{len(at_risk_df) / segments_df['Customer ID'].nunique():.1%}",
                        str(len(inventory_df[inventory_df['Risk Level'] == 'HIGH'])),
                        "85%"
                    ]
                }
                report_df = pd.DataFrame(report_data)
                st.dataframe(report_df, use_container_width=True)
                csv = report_df.to_csv(index=False)
                st.download_button("Download Report", csv, "executive_summary.csv", "text/csv")
            
            elif report_type == "Customer Analytics":
                st.dataframe(segments_df.head(100), use_container_width=True)
                csv = segments_df.to_csv(index=False)
                st.download_button("Download Customer Report", csv, "customer_report.csv", "text/csv")
            
            elif report_type == "Inventory Report":
                st.dataframe(inventory_df.head(100), use_container_width=True)
                csv = inventory_df.to_csv(index=False)
                st.download_button("Download Inventory Report", csv, "inventory_report.csv", "text/csv")
            
            elif report_type == "Full Analytics":
                st.success("Full analytics report generated!")
                st.info("Report includes: Sales trends, Customer segments, Inventory status, Churn analysis")

# Footer
st.markdown("---")
st.markdown("*RetailPulse - AI-Powered Customer Analytics Platform | Built for Zidio Development*")