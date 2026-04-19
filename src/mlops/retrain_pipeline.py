"""
Automated Retraining Pipeline with Airflow
"""

import pandas as pd
import numpy as np
import joblib
from datetime import datetime, timedelta
from sklearn.model_selection import train_test_split
import xgboost as xgb
from prophet import Prophet
import warnings
warnings.filterwarnings('ignore')

class RetrainingPipeline:
    def __init__(self, data_path='../data/processed/'):
        self.data_path = data_path
        self.models_path = '../src/models/'
        
    def load_new_data(self, days_back=30):
        """Load recent data for retraining"""
        df = pd.read_csv(f'{self.data_path}cleaned_sales.csv', parse_dates=['InvoiceDate'])
        cutoff_date = df['InvoiceDate'].max() - timedelta(days=days_back)
        new_data = df[df['InvoiceDate'] >= cutoff_date]
        print(f"Loaded {len(new_data)} rows from last {days_back} days")
        return new_data
    
    def retrain_churn_model(self):
        """Retrain churn prediction model with new data"""
        print("\n🔄 Retraining Churn Model...")
        
        df = pd.read_csv(f'{self.data_path}cleaned_sales.csv', parse_dates=['InvoiceDate'])
        rfm = pd.read_csv(f'{self.data_path}customer_segments.csv')
        
        # Calculate churn with updated date
        snapshot_date = df['InvoiceDate'].max()
        last_purchase = df.groupby('Customer ID')['InvoiceDate'].max().reset_index()
        last_purchase['days_since_last'] = (snapshot_date - last_purchase['InvoiceDate']).dt.days
        last_purchase['churn'] = (last_purchase['days_since_last'] > 90).astype(int)
        
        # Prepare features
        features = df.groupby('Customer ID').agg({
            'Quantity': ['mean', 'std', 'sum'],
            'Price': ['mean', 'std'],
            'TotalPrice': ['mean', 'std', 'sum'],
            'InvoiceDate': lambda x: (x.max() - x.min()).days,
            'StockCode': 'nunique'
        }).reset_index()
        
        features.columns = ['Customer ID', 'avg_quantity', 'std_quantity', 'total_quantity',
                           'avg_price', 'std_price', 'avg_order_value', 'std_order_value',
                           'total_spent', 'customer_lifespan', 'unique_products']
        
        features = features.merge(rfm[['Customer ID', 'Recency', 'Frequency', 'Monetary']], on='Customer ID')
        features = features.merge(last_purchase[['Customer ID', 'churn']], on='Customer ID')
        
        X = features.drop(['Customer ID', 'churn'], axis=1).fillna(0)
        y = features['churn']
        
        # Train new model
        model = xgb.XGBClassifier(
            n_estimators=200,
            max_depth=6,
            learning_rate=0.05,
            scale_pos_weight=(len(y) - y.sum()) / y.sum(),
            random_state=42
        )
        
        model.fit(X, y)
        
        # Save model with timestamp
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        model_path = f'{self.models_path}churn_xgboost_{timestamp}.pkl'
        joblib.dump(model, model_path)
        
        # Update latest model symlink
        latest_path = f'{self.models_path}churn_xgboost_latest.pkl'
        joblib.dump(model, latest_path)
        
        print(f"✅ Churn model retrained and saved to: {model_path}")
        return model
    
    def retrain_forecast_model(self):
        """Retrain demand forecast model with new data"""
        print("\n🔄 Retraining Forecast Model...")
        
        daily_sales = pd.read_csv(f'{self.data_path}daily_sales.csv')
        daily_sales.columns = ['ds', 'y']
        daily_sales['ds'] = pd.to_datetime(daily_sales['ds'])
        
        # Train Prophet with latest data
        model = Prophet(
            yearly_seasonality=True,
            weekly_seasonality=True,
            seasonality_mode='multiplicative'
        )
        model.fit(daily_sales)
        
        # Save model
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        model_path = f'{self.models_path}prophet_model_{timestamp}.pkl'
        joblib.dump(model, model_path)
        
        # Update latest
        latest_path = f'{self.models_path}prophet_model_latest.pkl'
        joblib.dump(model, latest_path)
        
        print(f"✅ Forecast model retrained and saved to: {model_path}")
        return model
    
    def update_segments(self):
        """Update customer segments with new data"""
        print("\n🔄 Updating Customer Segments...")
        
        from sklearn.preprocessing import StandardScaler
        from sklearn.cluster import KMeans
        
        df = pd.read_csv(f'{self.data_path}cleaned_sales.csv', parse_dates=['InvoiceDate'])
        
        # Calculate RFM
        snapshot_date = df['InvoiceDate'].max() + timedelta(days=1)
        rfm = df.groupby('Customer ID').agg({
            'InvoiceDate': lambda x: (snapshot_date - x.max()).days,
            'InvoiceNo': 'nunique',
            'TotalPrice': 'sum'
        }).rename(columns={
            'InvoiceDate': 'Recency',
            'InvoiceNo': 'Frequency',
            'TotalPrice': 'Monetary'
        })
        
        # Scale and cluster
        scaler = StandardScaler()
        rfm_scaled = scaler.fit_transform(rfm[['Recency', 'Frequency', 'Monetary']])
        
        kmeans = KMeans(n_clusters=6, random_state=42, n_init=10)
        rfm['Segment'] = kmeans.fit_predict(rfm_scaled)
        
        # Save updated segments
        rfm.to_csv(f'{self.data_path}customer_segments_updated.csv')
        
        # Save models
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        joblib.dump(kmeans, f'{self.models_path}kmeans_segmenter_{timestamp}.pkl')
        joblib.dump(scaler, f'{self.models_path}rfm_scaler_{timestamp}.pkl')
        
        print(f"✅ Customer segments updated: {len(rfm)} customers")
        return rfm
    
    def run_full_retraining(self):
        """Execute complete retraining pipeline"""
        print("="*60)
        print("STARTING AUTOMATED RETRAINING PIPELINE")
        print("="*60)
        print(f"Started at: {datetime.now()}")
        
        results = {
            'timestamp': datetime.now().isoformat(),
            'churn_model': None,
            'forecast_model': None,
            'segments_updated': False
        }
        
        try:
            results['churn_model'] = self.retrain_churn_model()
        except Exception as e:
            print(f"❌ Churn model retraining failed: {e}")
        
        try:
            results['forecast_model'] = self.retrain_forecast_model()
        except Exception as e:
            print(f"❌ Forecast model retraining failed: {e}")
        
        try:
            self.update_segments()
            results['segments_updated'] = True
        except Exception as e:
            print(f"❌ Segment update failed: {e}")
        
        print("\n" + "="*60)
        print("RETRAINING PIPELINE COMPLETE")
        print(f"Completed at: {datetime.now()}")
        print("="*60)
        
        return results

# Create Airflow DAG file
def create_airflow_dag():
    """Generate Airflow DAG configuration"""
    
    dag_content = '''
"""
Airflow DAG for RetailPulse Automated Retraining
"""

from datetime import datetime, timedelta
from airflow import DAG
from airflow.operators.python_operator import PythonOperator
from airflow.operators.email_operator import EmailOperator
from retrain_pipeline import RetrainingPipeline

default_args = {
    'owner': 'khushboo',
    'depends_on_past': False,
    'start_date': datetime(2026, 4, 1),
    'email_on_failure': True,
    'email_on_retry': False,
    'retries': 1,
    'retry_delay': timedelta(minutes=5)
}

def run_retraining():
    pipeline = RetrainingPipeline()
    results = pipeline.run_full_retraining()
    return results

dag = DAG(
    'retailpulse_weekly_retraining',
    default_args=default_args,
    description='Weekly retraining of RetailPulse models',
    schedule_interval='0 0 * * 1',  # Every Monday at midnight
    catchup=False
)

retrain_task = PythonOperator(
    task_id='run_model_retraining',
    python_callable=run_retraining,
    dag=dag
)

email_report = EmailOperator(
    task_id='send_retraining_report',
    to=['admin@retailpulse.com'],
    subject='RetailPulse Model Retraining Report',
    html_content='<p>Model retraining completed successfully!</p>',
    dag=dag
)

retrain_task >> email_report
'''
    
    with open('../airflow/dags/retailpulse_retraining.py', 'w') as f:
        f.write(dag_content)
    
    print("✅ Airflow DAG created at: ../airflow/dags/retailpulse_retraining.py")

if __name__ == "__main__":
    # Run pipeline
    pipeline = RetrainingPipeline()
    results = pipeline.run_full_retraining()
    
    # Create Airflow DAG
    create_airflow_dag()