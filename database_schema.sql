-- Database Schema for Reve Digital Platform
-- Supports both Digital Farming and Digital Healthcare domains
-- Compatible with MySQL 5.7+ and MariaDB 10.2+

-- Create database (uncomment when using in MySQL directly)
-- CREATE DATABASE IF NOT EXISTS reve_digital_platform CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
-- USE reve_digital_platform;

-- Set proper character set and collation for internationalization
SET NAMES utf8mb4;
SET FOREIGN_KEY_CHECKS = 0;

-- User authentication tables (will be created by Django automatically)
-- Shown here for reference only

/*
CREATE TABLE auth_user (
    id INT AUTO_INCREMENT PRIMARY KEY,
    password VARCHAR(128) NOT NULL,
    last_login DATETIME NULL,
    is_superuser BOOLEAN NOT NULL,
    username VARCHAR(150) NOT NULL UNIQUE,
    first_name VARCHAR(150) NOT NULL,
    last_name VARCHAR(150) NOT NULL,
    email VARCHAR(254) NOT NULL,
    is_staff BOOLEAN NOT NULL,
    is_active BOOLEAN NOT NULL,
    date_joined DATETIME NOT NULL
);
*/

-- Soil Data table for Digital Farming
CREATE TABLE soil_data (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    data_file VARCHAR(255) NOT NULL,
    data_type VARCHAR(20) NOT NULL,
    upload_date DATETIME NOT NULL,
    farm_name VARCHAR(100) NOT NULL,
    location VARCHAR(255) NOT NULL,
    notes TEXT,
    data_category VARCHAR(20) DEFAULT 'farming',
    FOREIGN KEY (user_id) REFERENCES auth_user(id) ON DELETE CASCADE,
    CONSTRAINT check_soil_data_type CHECK (data_type IN ('spectrometer', 'multi_param', 'moisture'))
);

-- Soil Analysis Results table
CREATE TABLE soil_analysis_result (
    id INT AUTO_INCREMENT PRIMARY KEY,
    soil_data_id INT NOT NULL,
    analysis_date DATETIME NOT NULL,
    moisture_content FLOAT,
    nutrient_levels JSON,
    organic_matter FLOAT,
    ph_level FLOAT,
    soil_health_score FLOAT,
    result_summary TEXT NOT NULL,
    recommendations TEXT NOT NULL,
    FOREIGN KEY (soil_data_id) REFERENCES soil_data(id) ON DELETE CASCADE
);

-- Healthcare Data table for Digital Healthcare
CREATE TABLE healthcare_data (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    data_file VARCHAR(255) NOT NULL,
    data_type VARCHAR(20) NOT NULL,
    cancer_type VARCHAR(20) NOT NULL,
    upload_date DATETIME NOT NULL,
    patient_id VARCHAR(100) NOT NULL,
    patient_age INT,
    patient_gender VARCHAR(10),
    notes TEXT,
    data_category VARCHAR(20) DEFAULT 'healthcare',
    FOREIGN KEY (user_id) REFERENCES auth_user(id) ON DELETE CASCADE,
    CONSTRAINT check_healthcare_data_type CHECK (data_type IN ('spectrometer', 'image')),
    CONSTRAINT check_cancer_type CHECK (cancer_type IN ('breast', 'throat', 'skin', 'other', 'screening'))
);

-- Healthcare Analysis Results table
CREATE TABLE healthcare_analysis_result (
    id INT AUTO_INCREMENT PRIMARY KEY,
    healthcare_data_id INT NOT NULL,
    analysis_date DATETIME NOT NULL,
    cancer_probability FLOAT,
    biomarkers JSON,
    spectral_signatures JSON,
    confidence_score FLOAT,
    result_summary TEXT NOT NULL,
    recommendations TEXT NOT NULL,
    FOREIGN KEY (healthcare_data_id) REFERENCES healthcare_data(id) ON DELETE CASCADE
);

-- Chatbot Conversations table to store user interaction history
CREATE TABLE chatbot_conversation (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    timestamp DATETIME NOT NULL,
    message TEXT NOT NULL,
    response TEXT NOT NULL,
    domain VARCHAR(20) NOT NULL,
    FOREIGN KEY (user_id) REFERENCES auth_user(id) ON DELETE CASCADE,
    CONSTRAINT check_chatbot_domain CHECK (domain IN ('farming', 'healthcare', 'general'))
);

-- AI Model Performance Metrics
CREATE TABLE ai_model_metrics (
    id INT AUTO_INCREMENT PRIMARY KEY,
    model_name VARCHAR(100) NOT NULL,
    timestamp DATETIME NOT NULL,
    domain VARCHAR(20) NOT NULL,
    accuracy FLOAT NOT NULL,
    precision_score FLOAT NOT NULL,
    recall_score FLOAT NOT NULL,
    f1_score FLOAT NOT NULL,
    training_data_size INT NOT NULL,
    notes TEXT,
    CONSTRAINT check_model_domain CHECK (domain IN ('farming', 'healthcare'))
);

-- Sample data insertion for demonstration (optional)
-- Uncomment and modify as needed for specific implementation

/*
-- Insert sample users (password is 'password')
INSERT INTO auth_user (password, is_superuser, username, first_name, last_name, email, is_staff, is_active, date_joined)
VALUES 
('pbkdf2_sha256$600000$tZPkl9CoMhKJcJ0tMFp1xL$B93+kBFcR2n8ysZK6HNWrist9+8X2t/mv79A5o9r1EM=', 0, 'farmer1', 'John', 'Farmer', 'farmer1@example.com', 0, 1, NOW()),
('pbkdf2_sha256$600000$tZPkl9CoMhKJcJ0tMFp1xL$B93+kBFcR2n8ysZK6HNWrist9+8X2t/mv79A5o9r1EM=', 0, 'doctor1', 'Jane', 'Doctor', 'doctor1@example.com', 0, 1, NOW()),
('pbkdf2_sha256$600000$tZPkl9CoMhKJcJ0tMFp1xL$B93+kBFcR2n8ysZK6HNWrist9+8X2t/mv79A5o9r1EM=', 1, 'admin', 'Admin', 'User', 'admin@example.com', 1, 1, NOW());

-- Insert sample soil data
INSERT INTO soil_data (user_id, data_file, data_type, upload_date, farm_name, location, notes, data_category)
VALUES 
(1, 'data_files/soil_sample1.csv', 'spectrometer', NOW(), 'Green Acres', 'Field 1, North Section', 'Sample taken after rainfall', 'farming'),
(1, 'data_files/soil_sample2.csv', 'multi_param', NOW(), 'Green Acres', 'Field 2, South Section', 'Clay soil area', 'farming'),
(1, 'data_files/soil_sample3.csv', 'moisture', NOW(), 'River Valley Farm', 'West Field', 'Irrigation test area', 'farming');

-- Insert sample healthcare data
INSERT INTO healthcare_data (user_id, data_file, data_type, cancer_type, upload_date, patient_id, patient_age, patient_gender, notes, data_category)
VALUES 
(2, 'data_files/patient001.csv', 'spectrometer', 'breast', NOW(), 'P001', 45, 'female', 'Regular screening', 'healthcare'),
(2, 'data_files/patient002.jpg', 'image', 'skin', NOW(), 'P002', 67, 'male', 'Suspicious mole on back', 'healthcare'),
(2, 'data_files/patient003.csv', 'spectrometer', 'throat', NOW(), 'P003', 52, 'male', 'History of smoking', 'healthcare');
*/

-- Create indexes for performance optimization
CREATE INDEX idx_soil_data_type ON soil_data(data_type);
CREATE INDEX idx_soil_upload_date ON soil_data(upload_date);
CREATE INDEX idx_healthcare_data_type ON healthcare_data(data_type);
CREATE INDEX idx_healthcare_cancer_type ON healthcare_data(cancer_type);
CREATE INDEX idx_healthcare_upload_date ON healthcare_data(upload_date);
CREATE INDEX idx_chatbot_domain ON chatbot_conversation(domain);
CREATE INDEX idx_chatbot_timestamp ON chatbot_conversation(timestamp);
CREATE INDEX idx_metrics_domain ON ai_model_metrics(domain);

-- Reset foreign key checks
SET FOREIGN_KEY_CHECKS = 1;