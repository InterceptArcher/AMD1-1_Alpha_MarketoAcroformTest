-- Migration: Add Marketo webhook tracking tables
-- Purpose: Track incoming webhooks from Marketo and API calls back to Marketo

-- ============================================================================
-- MARKETO WEBHOOKS TABLE
-- Tracks all incoming webhook requests from Marketo form submissions
-- ============================================================================

CREATE TABLE IF NOT EXISTS marketo_webhooks (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    lead_id VARCHAR(50) NOT NULL,
    email VARCHAR(255) NOT NULL,
    payload JSONB NOT NULL,
    status VARCHAR(20) DEFAULT 'received' CHECK (status IN ('received', 'processing', 'completed', 'failed')),
    pdf_url TEXT,
    error_message TEXT,
    processing_time_ms INTEGER,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    completed_at TIMESTAMPTZ
);

-- Indexes for common queries
CREATE INDEX IF NOT EXISTS idx_marketo_webhooks_email ON marketo_webhooks(email);
CREATE INDEX IF NOT EXISTS idx_marketo_webhooks_lead_id ON marketo_webhooks(lead_id);
CREATE INDEX IF NOT EXISTS idx_marketo_webhooks_status ON marketo_webhooks(status);
CREATE INDEX IF NOT EXISTS idx_marketo_webhooks_created_at ON marketo_webhooks(created_at DESC);

-- Comment for documentation
COMMENT ON TABLE marketo_webhooks IS 'Tracks incoming webhook requests from Marketo form submissions';
COMMENT ON COLUMN marketo_webhooks.lead_id IS 'Marketo lead ID from webhook payload';
COMMENT ON COLUMN marketo_webhooks.payload IS 'Full webhook payload as JSON';
COMMENT ON COLUMN marketo_webhooks.processing_time_ms IS 'Time taken to process webhook in milliseconds';

-- ============================================================================
-- MARKETO API CALLS TABLE
-- Tracks API calls made back to Marketo (lead updates, campaign triggers)
-- ============================================================================

CREATE TABLE IF NOT EXISTS marketo_api_calls (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    webhook_id UUID REFERENCES marketo_webhooks(id) ON DELETE CASCADE,
    endpoint VARCHAR(255) NOT NULL,
    method VARCHAR(10) NOT NULL,
    request_body JSONB,
    response_status INTEGER,
    response_body JSONB,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Index for joining with webhooks
CREATE INDEX IF NOT EXISTS idx_marketo_api_calls_webhook_id ON marketo_api_calls(webhook_id);

-- Comment for documentation
COMMENT ON TABLE marketo_api_calls IS 'Tracks API calls made back to Marketo REST API';
COMMENT ON COLUMN marketo_api_calls.endpoint IS 'Marketo API endpoint called';
COMMENT ON COLUMN marketo_api_calls.response_status IS 'HTTP status code from Marketo';

-- ============================================================================
-- ROW LEVEL SECURITY (RLS)
-- ============================================================================

-- Enable RLS on tables
ALTER TABLE marketo_webhooks ENABLE ROW LEVEL SECURITY;
ALTER TABLE marketo_api_calls ENABLE ROW LEVEL SECURITY;

-- Policy: Service role can do everything
CREATE POLICY "Service role full access to marketo_webhooks"
    ON marketo_webhooks
    FOR ALL
    TO service_role
    USING (true)
    WITH CHECK (true);

CREATE POLICY "Service role full access to marketo_api_calls"
    ON marketo_api_calls
    FOR ALL
    TO service_role
    USING (true)
    WITH CHECK (true);

-- Policy: Authenticated users can read their own webhook data (by email)
CREATE POLICY "Users can view their own webhooks"
    ON marketo_webhooks
    FOR SELECT
    TO authenticated
    USING (email = auth.jwt() ->> 'email');
