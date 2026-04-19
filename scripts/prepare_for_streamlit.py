#!/usr/bin/env python3
"""
Prepare RetailPulse for Streamlit Cloud deployment
This script creates lightweight versions of data files for cloud deployment
"""

import pandas as pd
import numpy as np
import os
import json
from datetime import datetime, timedelta

def prepare_demo_data():
    """Create lightweight demo data for cloud deployment"""
    
    print("🚀 Preparing RetailPulse for Streamlit Cloud...")
    
    # Create data directory if it doesn't exist
    os.makedirs('data/processed', exist_ok=True)
    os.makedirs('src/models', exist_ok=True)
    
    # Initialize variables to avoid UnboundLocalError
    df = None
    segments_data = []
    inventory_data = []
    at_risk_data = []
    
    # Check if we have real data, otherwise create sample data
    if os.path.exists('data/processed/cleaned_sales.csv'):
        print("✅ Using existing processed data")
        df = pd.read_csv('data/processed/cleaned_sales.csv')
        
        # Limit rows for cloud (50k is fine)
        if len(df) > 50000:
            df = df.sample(n=50000, random_state=42)
            df.to_csv('data/processed/cleaned_sales.csv', index=False)
            print(f"   Limited to 50,000 rows for cloud deployment")
    else:
        print("📊 Creating sample sales data for demo...")
        # Create sample data for demo
        dates = pd.date_range(start='2023-01-01', end='2024-12-31', freq='D')
        np.random.seed(42)
        
        sample_data = []
        for date in dates:
            daily_sales = np.random.normal(10000, 2000)
            sample_data.append({
                'InvoiceDate': date,
                'TotalPrice': max(0, daily_sales),
                'Quantity': int(np.random.normal(500, 100)),
                'InvoiceNo': f'INV_{date.strftime("%Y%m%d")}',
                'Customer ID': np.random.randint(10000, 20000),
                'Country': np.random.choice(['United Kingdom', 'France', 'Germany', 'USA', 'Australia']),
                'Price': np.random.uniform(5, 50),
                'Description': np.random.choice(['Product A', 'Product B', 'Product C', 'Product D'])
            })
        
        df = pd.DataFrame(sample_data)
        df.to_csv('data/processed/cleaned_sales.csv', index=False)
        print("✅ Sample data created")
    
    # Get unique customers from dataframe
    unique_customers = df['Customer ID'].unique()[:1000]  # Limit for cloud
    
    # Create customer segments if not exists
    customer_segments_path = 'data/processed/customer_segments.csv'
    if not os.path.exists(customer_segments_path):
        print("👥 Creating customer segments...")
        segments_data = []
        for i, cust in enumerate(unique_customers):
            segments_data.append({
                'Customer ID': cust,
                'Segment': np.random.choice([0, 1, 2, 3, 4, 5]),
                'Recency': np.random.randint(1, 365),
                'Frequency': np.random.randint(1, 50),
                'Monetary': np.random.uniform(50, 5000),
                'CLV': np.random.uniform(100, 10000)
            })
        segments_df = pd.DataFrame(segments_data)
        segments_df.to_csv(customer_segments_path, index=False)
        print(f"   Created {len(segments_data)} customer segments")
    else:
        segments_df = pd.read_csv(customer_segments_path)
        segments_data = segments_df.to_dict('records')
        print(f"✅ Using existing customer segments ({len(segments_data)} records)")
    
    # Create forecast data
    forecast_path = 'data/processed/30_day_forecast.csv'
    if not os.path.exists(forecast_path):
        print("📈 Creating forecast data...")
        forecast_dates = pd.date_range(start=datetime.now(), periods=30, freq='D')
        forecast_data = []
        for i, date in enumerate(forecast_dates):
            forecast_data.append({
                'ds': date,
                'yhat': np.random.normal(12000, 1500),
                'yhat_lower': np.random.normal(10000, 1200),
                'yhat_upper': np.random.normal(14000, 1800)
            })
        forecast_df = pd.DataFrame(forecast_data)
        forecast_df.to_csv(forecast_path, index=False)
        print("✅ Forecast data created")
    else:
        print("✅ Using existing forecast data")
    
    # Create at-risk customers
    at_risk_path = 'data/processed/at_risk_customers.csv'
    if not os.path.exists(at_risk_path):
        print("⚠️ Creating at-risk customers data...")
        at_risk_data = []
        for cust in unique_customers[:200]:
            at_risk_data.append({
                'Customer ID': cust,
                'churn_probability': np.random.uniform(0.6, 0.95),
                'total_spent': np.random.uniform(100, 5000),
                'Recency': np.random.randint(60, 180)
            })
        at_risk_df = pd.DataFrame(at_risk_data)
        at_risk_df.to_csv(at_risk_path, index=False)
        print(f"   Created {len(at_risk_data)} at-risk customers")
    else:
        at_risk_df = pd.read_csv(at_risk_path)
        at_risk_data = at_risk_df.to_dict('records')
        print(f"✅ Using existing at-risk customers ({len(at_risk_data)} records)")
    
    # Create inventory recommendations
    inventory_path = 'data/processed/inventory_recommendations.csv'
    if not os.path.exists(inventory_path):
        print("📦 Creating inventory data...")
        products = ['Product A', 'Product B', 'Product C', 'Product D', 'Product E']
        inventory_data = []
        for i, product in enumerate(products):
            for j in range(20):
                inventory_data.append({
                    'StockCode': f'STK_{i:04d}{j:02d}',
                    'Description': f'{product} Variant {j+1}',
                    'current_stock': np.random.randint(0, 500),
                    'reorder_point': np.random.randint(50, 200),
                    'reorder_quantity': np.random.randint(0, 300),
                    'stockout_risk': np.random.choice(['HIGH', 'MEDIUM', 'LOW'], p=[0.2, 0.3, 0.5]),
                    'inventory_value': np.random.uniform(100, 5000),
                    'optimization_strategy': np.random.choice(['URGENT: Place order immediately', 'Monitor: Consider ordering within 3 days', 'Sufficient stock'])
                })
        inventory_df = pd.DataFrame(inventory_data)
        inventory_df.to_csv(inventory_path, index=False)
        print(f"   Created {len(inventory_data)} inventory records")
    else:
        inventory_df = pd.read_csv(inventory_path)
        inventory_data = inventory_df.to_dict('records')
        print(f"✅ Using existing inventory data ({len(inventory_data)} records)")
    
    # Create drift config
    drift_config_path = 'data/processed/drift_config.json'
    drift_config = {
        'drift_detected': False,
        'drift_threshold': 0.05,
        'monitoring_frequency': 'weekly',
        'reference_period': {'start': '2023-01-01', 'end': '2023-06-30'},
        'current_period': {'start': '2024-01-01', 'end': '2024-03-31'},
        'results': {
            'TotalPrice': {'ks_p_value': 0.32, 'psi_value': 0.05, 'severity': 'No significant drift', 'drift_detected': False},
            'Quantity': {'ks_p_value': 0.45, 'psi_value': 0.03, 'severity': 'No significant drift', 'drift_detected': False},
            'InvoiceNo': {'ks_p_value': 0.28, 'psi_value': 0.07, 'severity': 'No significant drift', 'drift_detected': False}
        }
    }
    
    with open(drift_config_path, 'w') as f:
        json.dump(drift_config, f, indent=2)
    print("✅ Drift config created")
    
    print("\n" + "="*50)
    print("✅ All data prepared for Streamlit Cloud deployment!")
    print("="*50)
    print("\n📊 Data Summary:")
    print(f"   - Sales records: {len(df):,}")
    print(f"   - Customers: {len(segments_data):,}")
    print(f"   - Products in inventory: {len(inventory_data):,}")
    print(f"   - At-risk customers: {len(at_risk_data):,}")
    print("\n📁 Files created/updated:")
    print(f"   - {customer_segments_path}")
    print(f"   - {forecast_path}")
    print(f"   - {at_risk_path}")
    print(f"   - {inventory_path}")
    print(f"   - {drift_config_path}")
    print("\n🚀 Ready to deploy to Streamlit Cloud!")
    print("   Next: git add . && git commit -m 'Ready for deployment' && git push origin main")

if __name__ == "__main__":
    prepare_demo_data()