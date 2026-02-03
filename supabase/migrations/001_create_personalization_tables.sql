-- Migration: Create personalization tables
-- Description: Create tables for storing personalization jobs and their outputs
-- Author: InterceptArcher
-- Date: 2026-01-27

-- Create personalization_jobs table
CREATE TABLE IF NOT EXISTS personalization_jobs (
    id BIGSERIAL PRIMARY KEY,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW() NOT NULL,
    email VARCHAR(255) NOT NULL,
    domain VARCHAR(255) NOT NULL,
    cta VARCHAR(50) NOT NULL,
    persona VARCHAR(50),
    buyer_stage VARCHAR(50),
    company_name VARCHAR(255),
    industry VARCHAR(100),
    company_size VARCHAR(50),
    status VARCHAR(50) DEFAULT 'pending' NOT NULL
);

-- Create index on email for faster lookups
CREATE INDEX IF NOT EXISTS idx_personalization_jobs_email
    ON personalization_jobs(email);

-- Create index on domain for analytics
CREATE INDEX IF NOT EXISTS idx_personalization_jobs_domain
    ON personalization_jobs(domain);

-- Create index on created_at for time-based queries
CREATE INDEX IF NOT EXISTS idx_personalization_jobs_created_at
    ON personalization_jobs(created_at DESC);

-- Create personalization_outputs table
CREATE TABLE IF NOT EXISTS personalization_outputs (
    id BIGSERIAL PRIMARY KEY,
    job_id BIGINT NOT NULL REFERENCES personalization_jobs(id) ON DELETE CASCADE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW() NOT NULL,
    output_json JSONB NOT NULL
);

-- Create index on job_id for faster joins
CREATE INDEX IF NOT EXISTS idx_personalization_outputs_job_id
    ON personalization_outputs(job_id);

-- Add comment to tables
COMMENT ON TABLE personalization_jobs IS 'Stores personalization job metadata including user info and company details';
COMMENT ON TABLE personalization_outputs IS 'Stores the JSON output from Claude API for each personalization job';

-- Enable Row Level Security (optional - can be configured later)
ALTER TABLE personalization_jobs ENABLE ROW LEVEL SECURITY;
ALTER TABLE personalization_outputs ENABLE ROW LEVEL SECURITY;

-- Create policy to allow anon access (for alpha - should be restricted in production)
CREATE POLICY "Allow anonymous access to personalization_jobs"
    ON personalization_jobs FOR ALL
    USING (true);

CREATE POLICY "Allow anonymous access to personalization_outputs"
    ON personalization_outputs FOR ALL
    USING (true);
