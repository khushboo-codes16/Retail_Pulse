"""
Locust load testing for RetailPulse API
Install: pip install locust
Run: locust -f tests/load_test.py --host=http://localhost:8000
"""

from locust import HttpUser, task, between
import random

class RetailPulseUser(HttpUser):
    wait_time = between(1, 3)
    
    def on_start(self):
        """Login or setup before test"""
        self.headers = {
            "Content-Type": "application/json"
        }
    
    @task(3)
    def get_dashboard_metrics(self):
        """Get dashboard metrics - high priority"""
        self.client.get("/api/metrics/dashboard")
    
    @task(2)
    def get_forecast(self):
        """Get demand forecast - medium priority"""
        self.client.get("/api/forecast/30days")
    
    @task(2)
    def get_customers(self):
        """Get customer segments - medium priority"""
        self.client.get("/api/customers/segments")
    
    @task(1)
    def get_churn_prediction(self):
        """Get churn prediction - low priority"""
        customer_id = random.randint(10000, 20000)
        self.client.get(f"/api/churn/predict/{customer_id}")
    
    @task(1)
    def get_inventory(self):
        """Get inventory recommendations - low priority"""
        self.client.get("/api/inventory/recommendations")

class APILoadTest(HttpUser):
    wait_time = between(0.5, 2)
    
    @task
    def health_check(self):
        """Health check endpoint"""
        self.client.get("/health")
    
    @task
    def get_models(self):
        """Get available models"""
        self.client.get("/api/models")
    
    @task
    def predict_sales(self):
        """Predict sales for a date range"""
        data = {
            "start_date": "2024-01-01",
            "end_date": "2024-01-31"
        }
        self.client.post("/api/predict/sales", json=data)