-- Initialize database for RetailPulse
CREATE TABLE IF NOT EXISTS sales (
    id SERIAL PRIMARY KEY,
    invoice_no VARCHAR(20),
    stock_code VARCHAR(20),
    description TEXT,
    quantity INTEGER,
    invoice_date TIMESTAMP,
    price DECIMAL(10,2),
    customer_id INTEGER,
    country VARCHAR(100),
    total_price DECIMAL(10,2)
);

CREATE TABLE IF NOT EXISTS customers (
    customer_id INTEGER PRIMARY KEY,
    segment INTEGER,
    recency INTEGER,
    frequency INTEGER,
    monetary DECIMAL(10,2),
    clv DECIMAL(10,2),
    churn_probability DECIMAL(5,4),
    last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS forecasts (
    id SERIAL PRIMARY KEY,
    forecast_date DATE,
    forecast_value DECIMAL(10,2),
    lower_bound DECIMAL(10,2),
    upper_bound DECIMAL(10,2),
    model_version VARCHAR(50),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS inventory (
    stock_code VARCHAR(20) PRIMARY KEY,
    description TEXT,
    current_stock INTEGER,
    reorder_point INTEGER,
    reorder_quantity INTEGER,
    stockout_risk VARCHAR(10),
    last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Create indexes for performance
CREATE INDEX idx_sales_date ON sales(invoice_date);
CREATE INDEX idx_sales_customer ON sales(customer_id);
CREATE INDEX idx_forecast_date ON forecasts(forecast_date);