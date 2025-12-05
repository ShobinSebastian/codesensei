-- init.sql
-- Database initialization for CodeSensei

-- Create extensions
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Users table
CREATE TABLE IF NOT EXISTS users (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    email VARCHAR(255) UNIQUE NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    last_login TIMESTAMP
);

-- Analysis results table
CREATE TABLE IF NOT EXISTS analyses (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID REFERENCES users(id),
    code_hash VARCHAR(64) NOT NULL,
    code_length INTEGER,
    issues_count INTEGER,
    critical_count INTEGER,
    medium_count INTEGER,
    low_count INTEGER,
    llm_used BOOLEAN DEFAULT FALSE,
    execution_time FLOAT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    INDEX idx_code_hash (code_hash),
    INDEX idx_user_id (user_id),
    INDEX idx_created_at (created_at)
);

-- Issues table (detailed)
CREATE TABLE IF NOT EXISTS issues (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    analysis_id UUID REFERENCES analyses(id) ON DELETE CASCADE,
    issue_type VARCHAR(50),
    severity VARCHAR(20),
    line_number INTEGER,
    message TEXT,
    category VARCHAR(50),
    tool VARCHAR(50),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    INDEX idx_analysis_id (analysis_id),
    INDEX idx_severity (severity)
);

-- Cache table (for LLM responses)
CREATE TABLE IF NOT EXISTS cache (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    cache_key VARCHAR(255) UNIQUE NOT NULL,
    cache_value JSONB,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    expires_at TIMESTAMP,
    hit_count INTEGER DEFAULT 0,
    
    INDEX idx_cache_key (cache_key),
    INDEX idx_expires_at (expires_at)
);

-- Metrics table
CREATE TABLE IF NOT EXISTS metrics (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    metric_name VARCHAR(100),
    metric_value FLOAT,
    labels JSONB,
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    INDEX idx_metric_name (metric_name),
    INDEX idx_timestamp (timestamp)
);

-- Create sample user
INSERT INTO users (email) VALUES ('demo@codesensei.com')
ON CONFLICT (email) DO NOTHING;

-- Grant permissions
GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO codesensei;
GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA public TO codesensei;