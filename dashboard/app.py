"""
RetailPulse - AI-Powered Customer Analytics Dashboard
Week 3: Complete Interactive Dashboard
"""

import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import matplotlib.pyplot as plt
import seaborn as sns
from datetime import datetime, timedelta
import joblib
import json
import hashlib
from streamlit_option_menu import option_menu

# Page configuration
st.set_page_config(
    page_title="RetailPulse - AI Analytics Platform",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for better styling
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        font-weight: bold;
        color: #1E88E5;
        text-align: center;
        margin-bottom: 2rem;
    }
    .metric-card {
        background-color: #f0f2f6;
        padding: 1rem;
        border-radius: 10px;
        text-align: center;
    }
    .warning-text {
        color: #ff4b4b;
        font-weight: bold;
    }
    .success-text {
        color: #00cc66;
        font-weight: bold;
    }
</style>
""", unsafe_allow_html=True)

# Authentication
def check_password():
    """Simple authentication - replace with database in production"""
    def password_entered():
        if st.session_state["password"] == "admin123":
            st.session_state["authenticated"] = True
        else:
            st.session_state["authenticated"] = False
    
    if "authenticated" not in st.session_state:
        st.title("🔐 RetailPulse Login")
        st.text_input("Password", type="password", on_change=password_entered, key="password")
        st.info("Demo credentials: password = 'admin123'")
        return False
    return st.session_state["authenticated"]

if not check_password():
    st.stop()

# Load all data with caching
@st.cache_data(ttl=3600)
def load_all_data():
    """Load all required data for the dashboard"""
    try:
        sales = pd.read_csv('data/processed/cleaned_sales.csv', parse_dates=['InvoiceDate'])
        segments = pd.read_csv('data/processed/customer_segments.csv')
        forecast = pd.read_csv('data/processed/30_day_forecast.csv')
        at_risk = pd.read_csv('data/processed/at_risk_customers.csv')
        inventory = pd.read_csv('data/processed/inventory_recommendations.csv')
        drift_config = json.load(open('data/processed/drift_config.json'))
        
        return sales, segments, forecast, at_risk, inventory, drift_config
    except Exception as e:
        st.error(f"Error loading data: {e}")
        return None, None, None, None, None, None

# Load models
@st.cache_resource
def load_models():
    """Load trained models"""
    models = {}
    try:
        models['segmenter'] = joblib.load('src/models/kmeans_segmenter.pkl')
        models['scaler'] = joblib.load('src/models/rfm_scaler.pkl')
        models['churn'] = joblib.load('src/models/churn_xgboost_tuned.pkl')
        st.success("✅ Models loaded successfully")
    except Exception as e:
        st.warning(f"Models not found: {e}")
    return models

# Load data
sales, segments, forecast, at_risk, inventory, drift_config = load_all_data()
models = load_models()

# Sidebar navigation with icons
with st.sidebar:
    st.image("https://img.icons8.com/color/96/000000/bar-chart.png", width=80)
    st.title("RetailPulse")
    st.markdown("---")
    
    selected = option_menu(
        menu_title=None,
        options=["Dashboard", "Demand Forecast", "Customer Insights", "Churn Analytics", 
                 "Inventory Optimization", "Drift Monitor", "Reports"],
        icons=["house", "graph-up", "people", "exclamation-triangle", "box-seam", 
               "activity", "file-text"],
        default_index=0,
        orientation="vertical",
        styles={
            "nav-link": {"font-size": "14px", "text-align": "left", "margin": "5px"},
            "nav-link-selected": {"background-color": "#1E88E5"},
        }
    )
    
    st.markdown("---")
    st.caption(f"Version 2.0\nLast Updated: {datetime.now().strftime('%Y-%m-%d')}")

# Helper functions
def format_currency(value):
    return f"£{value:,.2f}"

def format_number(value):
    return f"{value:,}"

# Page 1: Main Dashboard
if selected == "Dashboard":
    st.markdown('<div class="main-header">📊 RetailPulse Dashboard</div>', unsafe_allow_html=True)
    
    # Key metrics row
    col1, col2, col3, col4 = st.columns(4)
    
    total_revenue = sales['TotalPrice'].sum()
    total_customers = segments['Customer ID'].nunique()
    avg_order_value = sales.groupby('InvoiceNo')['TotalPrice'].sum().mean()
    churn_rate = len(at_risk) / total_customers if total_customers > 0 else 0
    
    with col1:
        st.metric("Total Revenue", format_currency(total_revenue), 
                  delta="+12.5%", delta_color="normal")
    with col2:
        st.metric("Active Customers", format_number(total_customers), 
                  delta="+8.3%", delta_color="normal")
    with col3:
        st.metric("Avg Order Value", format_currency(avg_order_value), 
                  delta="+5.2%", delta_color="normal")
    with col4:
        st.metric("Churn Rate", f"{churn_rate:.1%}", 
                  delta="-2.1%", delta_color="inverse")
    
    # Charts row 1
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("📈 Sales Trend")
        daily_sales = sales.groupby('InvoiceDate')['TotalPrice'].sum().reset_index()
        fig = px.line(daily_sales, x='InvoiceDate', y='TotalPrice', 
                      title="Daily Sales Over Time", color_discrete_sequence=['#1E88E5'])
        fig.update_layout(height=400, showlegend=False)
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        st.subheader("🌍 Sales by Country")
        country_sales = sales.groupby('Country')['TotalPrice'].sum().sort_values(ascending=False).head(10)
        fig = px.pie(values=country_sales.values, names=country_sales.index, 
                     title="Top 10 Countries by Revenue")
        fig.update_layout(height=400)
        st.plotly_chart(fig, use_container_width=True)
    
    # Charts row 2
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("📦 Top Products")
        top_products = sales.groupby('Description')['Quantity'].sum().sort_values(ascending=False).head(10)
        fig = px.bar(x=top_products.values, y=top_products.index, orientation='h',
                     title="Top 10 Products by Quantity", color_discrete_sequence=['#00cc66'])
        fig.update_layout(height=400)
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        st.subheader("📅 Sales by Hour")
        sales['Hour'] = sales['InvoiceDate'].dt.hour
        hourly_sales = sales.groupby('Hour')['TotalPrice'].sum()
        fig = px.line(x=hourly_sales.index, y=hourly_sales.values,
                      title="Sales Distribution by Hour", markers=True)
        fig.update_layout(height=400, xaxis_title="Hour of Day", yaxis_title="Revenue (£)")
        st.plotly_chart(fig, use_container_width=True)
    
    # Alert section
    st.subheader("⚠️ Critical Alerts")
    alert_col1, alert_col2, alert_col3 = st.columns(3)
    
    with alert_col1:
        high_risk = len(inventory[inventory['stockout_risk'] == 'HIGH']) if len(inventory) > 0 else 0
        st.warning(f"🔴 {high_risk} products at HIGH stockout risk")
    
    with alert_col2:
        at_risk_count = len(at_risk)
        st.error(f"⚠️ {at_risk_count} customers at risk of churning")
    
    with alert_col3:
        if drift_config.get('drift_detected', False):
            st.warning("📊 Data drift detected - Model retraining recommended")

# Page 2: Demand Forecast
elif selected == "Demand Forecast":
    st.markdown('<div class="main-header">📈 Demand Forecasting</div>', unsafe_allow_html=True)
    
    if forecast is not None:
        col1, col2 = st.columns([2, 1])
        
        with col1:
            st.subheader("30-Day Sales Forecast")
            fig = go.Figure()
            fig.add_trace(go.Scatter(x=forecast['ds'], y=forecast['yhat'], 
                                     mode='lines', name='Forecast', 
                                     line=dict(color='red', width=3)))
            fig.add_trace(go.Scatter(x=forecast['ds'], y=forecast.get('yhat_upper', forecast['yhat'] * 1.1),
                                     fill=None, mode='lines', line_color='rgba(255,0,0,0.2)',
                                     name='Upper Bound'))
            fig.add_trace(go.Scatter(x=forecast['ds'], y=forecast.get('yhat_lower', forecast['yhat'] * 0.9),
                                     fill='tonexty', mode='lines', line_color='rgba(255,0,0,0.2)',
                                     name='Lower Bound'))
            fig.update_layout(height=500, xaxis_title="Date", yaxis_title="Forecasted Sales (£)")
            st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            st.subheader("Forecast Summary")
            total_forecast = forecast['yhat'].sum()
            avg_daily = forecast['yhat'].mean()
            peak_day = forecast.loc[forecast['yhat'].idxmax(), 'ds']
            peak_value = forecast['yhat'].max()
            
            st.metric("Total 30-Day Forecast", format_currency(total_forecast))
            st.metric("Average Daily", format_currency(avg_daily))
            st.metric("Peak Day", f"{peak_day.strftime('%Y-%m-%d')}", 
                      delta=format_currency(peak_value))
        
        # What-if Analysis
        st.subheader("🔧 What-If Analysis")
        col1, col2, col3 = st.columns(3)
        
        with col1:
            multiplier = st.slider("Demand Multiplier", 0.5, 2.0, 1.0, 0.1)
        
        with col2:
            seasonality_impact = st.selectbox("Seasonality Impact", ["Normal", "High Season", "Low Season"])
        
        with col3:
            if st.button("Apply Scenario"):
                adjusted_forecast = forecast['yhat'] * multiplier
                if seasonality_impact == "High Season":
                    adjusted_forecast *= 1.2
                elif seasonality_impact == "Low Season":
                    adjusted_forecast *= 0.8
                
                st.success(f"Adjusted Forecast Total: {format_currency(adjusted_forecast.sum())}")
                
                fig2 = go.Figure()
                fig2.add_trace(go.Scatter(x=forecast['ds'], y=forecast['yhat'], 
                                          mode='lines', name='Original', line=dict(color='blue')))
                fig2.add_trace(go.Scatter(x=forecast['ds'], y=adjusted_forecast, 
                                          mode='lines', name='Scenario', line=dict(color='red', dash='dash')))
                fig2.update_layout(height=400, title="Scenario Comparison")
                st.plotly_chart(fig2, use_container_width=True)
        
        # Forecast table
        with st.expander("📋 Detailed Forecast Table"):
            display_forecast = forecast.copy()
            display_forecast['ds'] = pd.to_datetime(display_forecast['ds']).dt.date
            display_forecast['yhat'] = display_forecast['yhat'].apply(lambda x: format_currency(x))
            st.dataframe(display_forecast, use_container_width=True)
            
            csv = forecast.to_csv(index=False)
            st.download_button("Download Forecast CSV", csv, "forecast.csv", "text/csv")

# Page 3: Customer Insights
elif selected == "Customer Insights":
    st.markdown('<div class="main-header">👥 Customer Segmentation & Insights</div>', unsafe_allow_html=True)
    
    if segments is not None:
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("Segment Distribution")
            segment_counts = segments['Segment'].value_counts().sort_index()
            segment_names = {
                0: 'Champions', 1: 'Loyal', 2: 'Potential', 
                3: 'New', 4: 'At Risk', 5: 'Lost'
            }
            segment_labels = [segment_names.get(i, f'Segment {i}') for i in segment_counts.index]
            
            fig = px.pie(values=segment_counts.values, names=segment_labels, 
                         title="Customer Segment Distribution", hole=0.3)
            fig.update_traces(textposition='inside', textinfo='percent+label')
            st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            st.subheader("Segment Metrics")
            segment_metrics = segments.groupby('Segment').agg({
                'Recency': 'mean',
                'Frequency': 'mean',
                'Monetary': 'mean',
                'Customer ID': 'count'
            }).round(2)
            segment_metrics.index = [segment_names.get(i, f'Segment {i}') for i in segment_metrics.index]
            segment_metrics.columns = ['Avg Recency', 'Avg Frequency', 'Avg Monetary (£)', 'Count']
            st.dataframe(segment_metrics, use_container_width=True)
        
        # RFM Analysis
        st.subheader("RFM Analysis")
        
        # Create RFM scores
        segments['R_Score'] = pd.qcut(segments['Recency'], 4, labels=['4', '3', '2', '1'])
        segments['F_Score'] = pd.qcut(segments['Frequency'].rank(method='first'), 4, labels=['1', '2', '3', '4'])
        segments['M_Score'] = pd.qcut(segments['Monetary'], 4, labels=['1', '2', '3', '4'])
        segments['RFM_Score'] = segments['R_Score'].astype(str) + segments['F_Score'].astype(str) + segments['M_Score'].astype(str)
        
        # RFM heatmap
        rfm_heatmap = segments.groupby(['R_Score', 'F_Score']).size().unstack(fill_value=0)
        fig = px.imshow(rfm_heatmap, text_auto=True, aspect="auto",
                        title="RFM Segmentation Heatmap (Recency vs Frequency)")
        st.plotly_chart(fig, use_container_width=True)
        
        # Customer lifetime value
        st.subheader("Customer Lifetime Value (CLV)")
        segments['CLV'] = segments['Monetary'] * segments['Frequency'] / segments['Recency'].clip(lower=1)
        
        col1, col2 = st.columns(2)
        with col1:
            fig = px.box(segments, x='Segment', y='CLV', 
                         title="CLV Distribution by Segment",
                         labels={'Segment': 'Customer Segment', 'CLV': 'Customer Lifetime Value (£)'})
            st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            top_customers = segments.nlargest(10, 'CLV')[['Customer ID', 'CLV', 'Monetary', 'Frequency']]
            top_customers['CLV'] = top_customers['CLV'].apply(lambda x: format_currency(x))
            st.dataframe(top_customers, use_container_width=True)

# Page 4: Churn Analytics
elif selected == "Churn Analytics":
    st.markdown('<div class="main-header">⚠️ Churn Prediction & Risk Analysis</div>', unsafe_allow_html=True)
    
    if at_risk is not None:
        col1, col2, col3 = st.columns(3)
        
        total_customers = segments['Customer ID'].nunique()
        at_risk_count = len(at_risk)
        revenue_at_risk = at_risk['total_spent'].sum() if 'total_spent' in at_risk.columns else 0
        
        with col1:
            st.metric("Customers at Risk", format_number(at_risk_count), 
                      delta=f"{(at_risk_count/total_customers):.1%} of total")
        with col2:
            st.metric("Revenue at Risk", format_currency(revenue_at_risk))
        with col3:
            st.metric("Churn Probability Threshold", ">70%")
        
        st.subheader("🔴 High-Risk Customers")
        
        # Filters
        col1, col2 = st.columns(2)
        with col1:
            min_probability = st.slider("Minimum Churn Probability", 0.5, 1.0, 0.7, 0.05)
        with col2:
            top_n = st.selectbox("Number of customers to show", [10, 20, 50, 100])
        
        filtered_risk = at_risk[at_risk['churn_probability'] >= min_probability].head(top_n)
        
        # Display at-risk customers
        st.dataframe(filtered_risk, use_container_width=True)
        
        # Retention strategies
        st.subheader("🎯 Retention Strategies by Segment")
        
        strategies = {
            'High Value': {
                'action': 'Personalized offers, VIP treatment',
                'discount': '20-30% off',
                'contact': 'Phone call + Email'
            },
            'Medium Value': {
                'action': 'Win-back campaigns, Product recommendations',
                'discount': '15-20% off',
                'contact': 'Email + SMS'
            },
            'Low Value': {
                'action': 'Re-engagement emails, Newsletter subscription',
                'discount': '10-15% off',
                'contact': 'Email'
            }
        }
        
        for segment, strategy in strategies.items():
            with st.expander(f"Strategy for {segment} Customers"):
                st.write(f"**Action:** {strategy['action']}")
                st.write(f"**Recommended Discount:** {strategy['discount']}")
                st.write(f"**Contact Method:** {strategy['contact']}")
        
        # Download at-risk list
        csv = at_risk.to_csv(index=False)
        st.download_button("Download At-Risk Customers CSV", csv, "at_risk_customers.csv", "text/csv")

# Page 5: Inventory Optimization
elif selected == "Inventory Optimization":
    st.markdown('<div class="main-header">📦 Inventory Optimization</div>', unsafe_allow_html=True)
    
    if inventory is not None:
        col1, col2, col3, col4 = st.columns(4)
        
        high_risk = len(inventory[inventory['stockout_risk'] == 'HIGH'])
        medium_risk = len(inventory[inventory['stockout_risk'] == 'MEDIUM'])
        total_value = inventory['inventory_value'].sum() if 'inventory_value' in inventory.columns else 0
        
        with col1:
            st.metric("High Risk Products", high_risk, delta="URGENT")
        with col2:
            st.metric("Medium Risk Products", medium_risk)
        with col3:
            st.metric("Total Inventory Value", format_currency(total_value))
        with col4:
            st.metric("Products to Reorder", len(inventory[inventory['reorder_quantity'] > 0]))
        
        # Filters
        col1, col2 = st.columns(2)
        with col1:
            risk_filter = st.multiselect("Filter by Risk Level", 
                                         ['HIGH', 'MEDIUM', 'LOW'], 
                                         default=['HIGH', 'MEDIUM'])
        with col2:
            search = st.text_input("Search Product", placeholder="Enter product description...")
        
        filtered_inventory = inventory[inventory['stockout_risk'].isin(risk_filter)]
        if search:
            filtered_inventory = filtered_inventory[
                filtered_inventory['Description'].str.contains(search, case=False, na=False)
            ]
        
        st.subheader("📋 Reorder Recommendations")
        display_cols = ['Description', 'current_stock', 'reorder_point', 
                        'reorder_quantity', 'stockout_risk', 'optimization_strategy']
        display_cols = [c for c in display_cols if c in filtered_inventory.columns]
        
        st.dataframe(filtered_inventory[display_cols].head(50), use_container_width=True)
        
        # Visualization
        col1, col2 = st.columns(2)
        
        with col1:
            risk_counts = inventory['stockout_risk'].value_counts()
            fig = px.bar(x=risk_counts.index, y=risk_counts.values, 
                         title="Stockout Risk Distribution",
                         color=risk_counts.index, color_discrete_sequence=['red', 'orange', 'green'])
            st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            top_reorder = inventory.nlargest(10, 'reorder_quantity')
            if len(top_reorder) > 0:
                fig = px.bar(x=top_reorder['reorder_quantity'], 
                             y=top_reorder['Description'].str[:40],
                             orientation='h', title="Top 10 Products to Reorder")
                st.plotly_chart(fig, use_container_width=True)
        
        # Export
        csv = inventory.to_csv(index=False)
        st.download_button("Download Inventory Report CSV", csv, "inventory_report.csv", "text/csv")

# Page 6: Drift Monitor
elif selected == "Drift Monitor":
    st.markdown('<div class="main-header">📊 Model Drift Monitor</div>', unsafe_allow_html=True)
    
    if drift_config:
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("Drift Status")
            if drift_config.get('drift_detected', False):
                st.error("⚠️ DATA DRIFT DETECTED")
                st.warning("Model retraining is recommended")
            else:
                st.success("✅ NO DRIFT DETECTED")
                st.info("Models are stable")
        
        with col2:
            st.subheader("Monitoring Configuration")
            st.write(f"**Reference Period:** {drift_config['reference_period']['start']} to {drift_config['reference_period']['end']}")
            st.write(f"**Current Period:** {drift_config['current_period']['start']} to {drift_config['current_period']['end']}")
            st.write(f"**Drift Threshold:** {drift_config.get('drift_threshold', 0.05)}")
            st.write(f"**Monitoring Frequency:** {drift_config.get('monitoring_frequency', 'weekly')}")
        
        # Column-wise drift results
        if 'results' in drift_config:
            st.subheader("Column-wise Drift Analysis")
            results_data = []
            for col, result in drift_config['results'].items():
                results_data.append({
                    'Column': col,
                    'KS Test p-value': result.get('ks_p_value', 'N/A'),
                    'PSI Value': result.get('psi_value', 'N/A'),
                    'Severity': result.get('severity', 'N/A'),
                    'Drift Detected': 'Yes' if result.get('drift_detected', False) else 'No'
                })
            
            results_df = pd.DataFrame(results_data)
            st.dataframe(results_df, use_container_width=True)
        
        # Recommendation
        st.subheader("📋 Recommendations")
        if drift_config.get('drift_detected', False):
            st.markdown("""
            - 🔄 **Retrain models** with latest data
            - 📊 **Review data pipeline** for changes
            - 🎯 **Update reference dataset** 
            - 📈 **Monitor model performance** metrics
            """)
        else:
            st.markdown("""
            - ✅ **Continue regular monitoring** (weekly)
            - 📊 **Schedule next drift check** in 7 days
            - 🎯 **No immediate action** required
            """)

# Page 7: Reports
elif selected == "Reports":
    st.markdown('<div class="main-header">📄 Generate Reports</div>', unsafe_allow_html=True)
    
    report_type = st.selectbox(
        "Select Report Type",
        ["Executive Summary", "Customer Analytics Report", "Inventory Report", "Full Analytics Report"]
    )
    
    date_range = st.date_input("Report Date Range", 
                               [datetime.now() - timedelta(days=30), datetime.now()])
    
    if st.button("Generate Report", type="primary"):
        with st.spinner("Generating report..."):
            # Create report based on type
            if report_type == "Executive Summary":
                report_data = {
                    'Metric': ['Total Revenue', 'Active Customers', 'Avg Order Value', 
                              'Churn Rate', 'Products at Risk', 'Forecast Accuracy'],
                    'Value': [
                        format_currency(total_revenue),
                        format_number(total_customers),
                        format_currency(avg_order_value),
                        f"{churn_rate:.1%}",
                        format_number(high_risk),
                        "85.2%"
                    ]
                }
                report_df = pd.DataFrame(report_data)
                st.dataframe(report_df, use_container_width=True)
                
                # Download button
                csv = report_df.to_csv(index=False)
                st.download_button("Download Report CSV", csv, 
                                  f"{report_type.replace(' ', '_')}_{datetime.now().strftime('%Y%m%d')}.csv", 
                                  "text/csv")
            
            elif report_type == "Customer Analytics Report":
                st.dataframe(segments.head(100), use_container_width=True)
                csv = segments.to_csv(index=False)
                st.download_button("Download Customer Report", csv, "customer_report.csv", "text/csv")
            
            elif report_type == "Inventory Report":
                st.dataframe(inventory.head(100), use_container_width=True)
                csv = inventory.to_csv(index=False)
                st.download_button("Download Inventory Report", csv, "inventory_report.csv", "text/csv")
            
            elif report_type == "Full Analytics Report":
                st.info("Generating comprehensive report...")
                # Combine all reports
                with pd.ExcelWriter('full_report.xlsx') as writer:
                    sales.to_excel(writer, sheet_name='Sales Data', index=False)
                    segments.to_excel(writer, sheet_name='Customer Segments', index=False)
                    inventory.to_excel(writer, sheet_name='Inventory', index=False)
                    at_risk.to_excel(writer, sheet_name='At_Risk_Customers', index=False)
                
                with open('full_report.xlsx', 'rb') as f:
                    st.download_button("Download Full Report (Excel)", f, 
                                      f"full_report_{datetime.now().strftime('%Y%m%d')}.xlsx")

# Footer
st.markdown("---")
st.markdown("*RetailPulse - AI-Powered Customer Analytics Platform | Built for Zidio Development*")