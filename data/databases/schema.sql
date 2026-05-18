-- KrishiQuery Database Schema for PostgreSQL

-- Enable UUID extension
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Farmers table
CREATE TABLE farmers (
    farmer_id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    phone VARCHAR(10) UNIQUE NOT NULL,
    village VARCHAR(100) NOT NULL,
    district VARCHAR(50) NOT NULL,
    state VARCHAR(50) DEFAULT 'Odisha',
    land_size DECIMAL(10,2),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Indexes for farmers
CREATE INDEX idx_farmers_phone ON farmers(phone);
CREATE INDEX idx_farmers_district ON farmers(district);
CREATE INDEX idx_farmers_village ON farmers(village);

-- PM-KISAN Payments table
CREATE TABLE pmkisan_payments (
    id SERIAL PRIMARY KEY,
    farmer_id INTEGER REFERENCES farmers(farmer_id) ON DELETE CASCADE,
    amount DECIMAL(10,2) NOT NULL,
    payment_date DATE NOT NULL,
    status VARCHAR(20) DEFAULT 'pending' CHECK (status IN ('pending', 'processed', 'completed', 'failed')),
    transaction_id VARCHAR(100),
    installment_number INTEGER CHECK (installment_number IN (1,2,3)),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Indexes for PM-KISAN
CREATE INDEX idx_pmkisan_farmer_id ON pmkisan_payments(farmer_id);
CREATE INDEX idx_pmkisan_payment_date ON pmkisan_payments(payment_date);

-- KALIA Payments table
CREATE TABLE kalia_payments (
    id SERIAL PRIMARY KEY,
    farmer_id INTEGER REFERENCES farmers(farmer_id) ON DELETE CASCADE,
    amount DECIMAL(10,2) NOT NULL,
    payment_date DATE NOT NULL,
    status VARCHAR(20) DEFAULT 'pending' CHECK (status IN ('pending', 'processed', 'completed', 'failed')),
    transaction_id VARCHAR(100),
    scheme_type VARCHAR(50) CHECK (scheme_type IN ('input_subsidy', 'livelihood_support', 'life_insurance')),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Indexes for KALIA
CREATE INDEX idx_kalia_farmer_id ON kalia_payments(farmer_id);
CREATE INDEX idx_kalia_payment_date ON kalia_payments(payment_date);

-- Soil Health table
CREATE TABLE soil_health (
    id SERIAL PRIMARY KEY,
    farmer_id INTEGER REFERENCES farmers(farmer_id) ON DELETE CASCADE,
    nitrogen DECIMAL(8,2),
    phosphorus DECIMAL(8,2),
    potassium DECIMAL(8,2),
    ph DECIMAL(4,2),
    organic_carbon DECIMAL(5,2),
    test_date DATE NOT NULL,
    recommendation TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Indexes for Soil Health
CREATE INDEX idx_soil_farmer_id ON soil_health(farmer_id);
CREATE INDEX idx_soil_test_date ON soil_health(test_date);

-- Mandi Prices table
CREATE TABLE mandi_prices (
    id SERIAL PRIMARY KEY,
    crop VARCHAR(50) NOT NULL,
    market VARCHAR(100) NOT NULL,
    district VARCHAR(50) NOT NULL,
    price DECIMAL(10,2) NOT NULL,
    date DATE NOT NULL,
    variety VARCHAR(50),
    grade VARCHAR(20),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Indexes for Mandi Prices
CREATE INDEX idx_mandi_crop ON mandi_prices(crop);
CREATE INDEX idx_mandi_market ON mandi_prices(market);
CREATE INDEX idx_mandi_district ON mandi_prices(district);
CREATE INDEX idx_mandi_date ON mandi_prices(date);

-- Weather table
CREATE TABLE weather (
    id SERIAL PRIMARY KEY,
    village VARCHAR(100) NOT NULL,
    district VARCHAR(50) NOT NULL,
    date DATE NOT NULL,
    rainfall DECIMAL(8,2),
    temperature DECIMAL(5,2),
    forecast TEXT,
    humidity DECIMAL(5,2),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Indexes for Weather
CREATE INDEX idx_weather_district ON weather(district);
CREATE INDEX idx_weather_village ON weather(village);
CREATE INDEX idx_weather_date ON weather(date);

-- Query Logs table
CREATE TABLE query_logs (
    log_id SERIAL PRIMARY KEY,
    phone_number VARCHAR(10) NOT NULL,
    question TEXT NOT NULL,
    intent VARCHAR(50),
    sql_generated TEXT,
    response TEXT,
    success BOOLEAN DEFAULT TRUE,
    processing_time_ms INTEGER,
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Indexes for Query Logs
CREATE INDEX idx_logs_phone ON query_logs(phone_number);
CREATE INDEX idx_logs_timestamp ON query_logs(timestamp);
CREATE INDEX idx_logs_intent ON query_logs(intent);

-- Farmer-Crop association table
CREATE TABLE farmer_crops (
    id SERIAL PRIMARY KEY,
    farmer_id INTEGER REFERENCES farmers(farmer_id) ON DELETE CASCADE,
    crop_name VARCHAR(50) NOT NULL,
    area_hectares DECIMAL(10,2),
    season VARCHAR(20) CHECK (season IN ('kharif', 'rabi', 'zaid')),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Feedback table
CREATE TABLE feedback (
    id SERIAL PRIMARY KEY,
    query_log_id INTEGER REFERENCES query_logs(log_id) ON DELETE SET NULL,
    rating INTEGER CHECK (rating BETWEEN 1 AND 5),
    comments TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Create a view for payment summary
CREATE VIEW farmer_payment_summary AS
SELECT 
    f.farmer_id,
    f.name,
    f.phone,
    COALESCE(SUM(p.amount), 0) as total_pmkisan,
    COUNT(p.id) as pmkisan_count,
    COALESCE(SUM(k.amount), 0) as total_kalia,
    COUNT(k.id) as kalia_count
FROM farmers f
LEFT JOIN pmkisan_payments p ON f.farmer_id = p.farmer_id AND p.status = 'completed'
LEFT JOIN kalia_payments k ON f.farmer_id = k.farmer_id AND k.status = 'completed'
GROUP BY f.farmer_id;

-- Function to update updated_at timestamp
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Trigger for farmers table
CREATE TRIGGER update_farmers_updated_at
    BEFORE UPDATE ON farmers
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

-- Grant permissions (adjust as needed)
-- GRANT SELECT, INSERT, UPDATE ON ALL TABLES IN SCHEMA public TO krishiquery_user;
-- GRANT USAGE, SELECT ON ALL SEQUENCES IN SCHEMA public TO krishiquery_user;