import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import joblib
from datetime import datetime, timedelta
import hashlib

import joblib
model = joblib.load('models/churn_model.pkl')
# Page config
st.set_page_config(page_title="RetailPulse - AI Analytics", layout="wide")

# Simple authentication (replace with database in production)
def check_password():
    """Simple password check - replace with real auth in production"""
    def password_entered():
        if st.session_state["password"] == "admin123":
            st.session_state["authenticated"] = True
        else:
            st.session_state["authenticated"] = False
    
    if "authenticated" not in st.session_state:
        st.text_input("Password", type="password", on_change=password_entered, key="password")
        st.info("Demo credentials: password = 'admin123'")
        return False
    return st.session_state["authenticated"]

if not check_password():
    st.stop()

# Load data
@st.cache_data
def load_data():
    sales = pd.read_csv('../data/processed/cleaned_sales.csv', parse_dates=['InvoiceDate'])
    segments = pd.read_csv('../data/processed/customer_segments.csv')
    forecast = pd.read_csv('../data/processed/30_day_forecast.csv')
    at_risk = pd.read_csv('../data/processed/at_risk_customers.csv')
    return sales, segments, forecast, at_risk

sales, segments, forecast, at_risk = load_data()

# Sidebar navigation
st.sidebar.title("📊 RetailPulse")
st.sidebar.markdown("---")
page = st.sidebar.selectbox(
    "Navigate",
    ["🏠 Dashboard Overview", "📈 Demand Forecast", "👥 Customer Segments", 
     "⚠️ Churn Risk", "📦 Inventory Optimization", "📄 Reports"]
)

# Main content
if page == "🏠 Dashboard Overview":
    st.title("RetailPulse - AI-Powered Analytics Dashboard")
    st.markdown(f"*Last Updated: {datetime.now().strftime('%Y-%m-%d %H:%M')}*")
    
    # Key metrics
    col1, col2, col3, col4 = st.columns(4)
    
    total_revenue = sales['TotalPrice'].sum()
    total_customers = segments['Customer ID'].nunique()
    avg_order_value = sales.groupby('InvoiceNo')['TotalPrice'].sum().mean()
    churn_rate = len(at_risk) / total_customers
    
    col1.metric("Total Revenue", f"£{total_revenue:,.0f}")
    col2.metric("Active Customers", f"{total_customers:,}")
    col3.metric("Avg Order Value", f"£{avg_order_value:.2f}")
    col4.metric("At-Risk Customers", f"{churn_rate:.1%}")
    
    # Sales trend
    st.subheader("Sales Trend")
    daily_sales = sales.groupby('InvoiceDate')['TotalPrice'].sum().reset_index()
    fig = px.line(daily_sales, x='InvoiceDate', y='TotalPrice', 
                  title="Daily Sales Over Time")
    st.plotly_chart(fig, use_container_width=True)
    
    # Top products
    col1, col2 = st.columns(2)
    with col1:
        top_products = sales.groupby('Description')['Quantity'].sum().sort_values(ascending=False).head(10)
        fig = px.bar(x=top_products.values, y=top_products.index, orientation='h',
                     title="Top 10 Products by Quantity")
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        country_sales = sales.groupby('Country')['TotalPrice'].sum().sort_values(ascending=False).head(10)
        fig = px.pie(values=country_sales.values, names=country_sales.index, title="Sales by Country")
        st.plotly_chart(fig, use_container_width=True)

elif page == "📈 Demand Forecast":
    st.title("30-Day Demand Forecast")
    
    # Display forecast
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=forecast['ds'], y=forecast['yhat'], 
                             mode='lines', name='Forecast', line=dict(color='red')))
    fig.update_layout(title="Next 30 Days Sales Forecast",
                      xaxis_title="Date", yaxis_title="Predicted Sales (£)")
    st.plotly_chart(fig, use_container_width=True)
    
    # Show forecast table
    st.subheader("Forecast Details")
    forecast['ds'] = pd.to_datetime(forecast['ds']).dt.date
    st.dataframe(forecast.rename(columns={'ds': 'Date', 'yhat': 'Predicted Sales (£)'}))

elif page == "👥 Customer Segments":
    st.title("Customer Segmentation Analysis")
    
    # Segment distribution
    segment_counts = segments['Segment'].value_counts().reset_index()
    segment_counts.columns = ['Segment', 'Count']
    
    fig = px.bar(segment_counts, x='Segment', y='Count', title="Customer Segment Distribution")
    st.plotly_chart(fig, use_container_width=True)
    
    # Segment metrics
    st.subheader("Segment Characteristics")
    segment_metrics = segments.groupby('Segment').agg({
        'Recency': 'mean',
        'Frequency': 'mean',
        'Monetary': 'mean',
        'Customer ID': 'count'
    }).round(2)
    segment_metrics.columns = ['Avg Recency (days)', 'Avg Frequency', 'Avg Monetary (£)', 'Count']
    st.dataframe(segment_metrics)
    
    # Download segments
    csv = segments.to_csv(index=False)
    st.download_button("Download Segments Data", csv, "customer_segments.csv", "text/csv")

elif page == "⚠️ Churn Risk":
    st.title("Customer Churn Risk Analysis")

    # Apply ML model
    try:
        features = at_risk.drop(columns=['Customer ID'], errors='ignore')
        at_risk['Churn Probability'] = model.predict_proba(features)[:, 1]
    except Exception as e:
        st.error(f"Model error: {e}")

    st.metric("Customers at Risk", len(at_risk), 
              delta=f"{len(at_risk) / segments['Customer ID'].nunique():.1%} of total")

    st.subheader("At-Risk Customers with ML Prediction")
    st.dataframe(at_risk.head(50))

    # Download
    csv = at_risk.to_csv(index=False)
    st.download_button("Download At-Risk List", csv, "at_risk_customers.csv", "text/csv")

elif page == "📦 Inventory Optimization":
    st.title("Inventory Optimization Recommendations")
    
    # Load product-level data
    product_demand = sales.groupby('Description').agg({
        'Quantity': 'sum',
        'InvoiceNo': 'nunique'
    }).reset_index()
    product_demand.columns = ['Product', 'Total Sold', 'Unique Orders']
    product_demand['Avg Order Size'] = product_demand['Total Sold'] / product_demand['Unique Orders']
    
    # Optimization logic
    product_demand['Recommended Reorder Qty'] = product_demand['Avg Order Size'] * 3  # 3 weeks of stock
    product_demand['Safety Stock'] = product_demand['Avg Order Size'] * 1.5
    
    st.subheader("Top Products - Reorder Recommendations")
    st.dataframe(product_demand.head(20))
    
    st.info("""
    **Optimization Logic:**
    - Reorder Quantity = Average Order Size × 3 (3 weeks of inventory)
    - Safety Stock = Average Order Size × 1.5
    - Update weekly based on demand forecast
    """)

elif page == "📄 Reports":
    st.title("Generate Reports")
    
    report_type = st.selectbox("Select Report Type", 
                               ["Executive Summary", "Customer Analytics", "Inventory Report", "Full Analytics"])
    
    if st.button("Generate Report"):
        with st.spinner("Generating report..."):
            # Create report DataFrame
            report_data = {
                'Metric': ['Total Revenue', 'Active Customers', 'Avg Order Value', 
                          'Churn Rate', 'Total Products Sold', 'Unique Countries'],
                'Value': [f"£{sales['TotalPrice'].sum():,.0f}", 
                         f"{segments['Customer ID'].nunique():,}",
                         f"£{sales.groupby('InvoiceNo')['TotalPrice'].sum().mean():.2f}",
                         f"{len(at_risk) / segments['Customer ID'].nunique():.1%}",
                         f"{sales['Quantity'].sum():,}",
                         f"{sales['Country'].nunique()}"]
            }
            report_df = pd.DataFrame(report_data)
            st.dataframe(report_df)
            
            # Download
            csv = report_df.to_csv(index=False)
            st.download_button("Download Report", csv, f"retailpulse_report_{datetime.now().strftime('%Y%m%d')}.csv", "text/csv")

st.sidebar.markdown("---")
st.sidebar.info("""
**RetailPulse v2.0**
- AI-Powered Analytics
- Real-time Insights
- Predictive Forecasting
""")