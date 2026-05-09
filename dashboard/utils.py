"""
Utility functions for RetailPulse Dashboard
"""

import streamlit as st
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import hashlib
import base64

def get_base64_image(image_path):
    """Convert image to base64 for embedding"""
    try:
        with open(image_path, "rb") as img_file:
            return base64.b64encode(img_file.read()).decode()
    except:
        return None

def apply_custom_css():
    """Apply custom CSS styling"""
    with open('dashboard/assets/style.css', 'r') as f:
        css = f.read()
    st.markdown(f'<style>{css}</style>', unsafe_allow_html=True)

def format_currency(value):
    """Format currency values"""
    return f"£{value:,.0f}"

def format_number(value):
    """Format large numbers"""
    return f"{value:,}"

def show_header():
    """Display custom header"""
    st.markdown("""
    <div class="custom-header">
        <h1>📊 RetailPulse</h1>
        <p>AI-Powered Customer Analytics & Demand Forecasting Platform</p>
    </div>
    """, unsafe_allow_html=True)

def show_top_nav(current_page):
    """Display top navigation bar with logout"""
    
    nav_items = {
        "Dashboard": "🏠",
        "Demand Forecast": "📈",
        "Customer Insights": "👥",
        "Churn Analytics": "⚠️",
        "Inventory": "📦",
        "Reports": "📄"
    }
    
    nav_html = '<div class="top-nav"><div class="nav-links">'
    
    for page, icon in nav_items.items():
        active_class = 'active' if page == current_page else ''
        nav_html += f'<a href="?page={page.replace(" ", "_")}" class="nav-item {active_class}">{icon} {page}</a>'
    
    nav_html += f'</div><button onclick="logout()" class="logout-btn">🚪 Logout</button></div>'
    
    st.markdown(nav_html, unsafe_allow_html=True)
    
    # JavaScript for logout
    st.markdown("""
    <script>
    function logout() {
        sessionStorage.clear();
        window.location.href = window.location.pathname + '?logout=true';
    }
    </script>
    """, unsafe_allow_html=True)

def check_logout():
    """Handle logout functionality"""
    import streamlit as st
    
    if st.query_params.get('logout') == 'true':
        st.session_state.authenticated = False
        st.query_params.clear()
        st.rerun()

def generate_demo_data():
    """Generate realistic demo data for the dashboard"""
    np.random.seed(42)
    
    # Sales data
    dates = pd.date_range(start='2023-01-01', end='2024-12-31', freq='D')
    sales_data = []
    for i, date in enumerate(dates):
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