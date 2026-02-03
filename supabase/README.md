# Supabase Setup Guide

This directory contains the database schema and migration files for the LinkedIn Personalization application.

## Database Schema

### Tables

#### `personalization_jobs`
Stores metadata about each personalization request.

| Column | Type | Description |
|--------|------|-------------|
| id | BIGSERIAL | Primary key (auto-increment) |
| created_at | TIMESTAMP | When the job was created |
| email | VARCHAR(255) | User's email address |
| domain | VARCHAR(255) | Extracted domain from email |
| cta | VARCHAR(50) | Call-to-action type (compare, learn, demo) |
| persona | VARCHAR(50) | Inferred user persona |
| buyer_stage | VARCHAR(50) | Buyer journey stage (Awareness, Evaluation, Decision) |
| company_name | VARCHAR(255) | Company name (enriched) |
| industry | VARCHAR(100) | Company industry |
| company_size | VARCHAR(50) | Company size category |
| status | VARCHAR(50) | Job status (pending, completed, failed) |

#### `personalization_outputs`
Stores the JSON output from Claude API.

| Column | Type | Description |
|--------|------|-------------|
| id | BIGSERIAL | Primary key (auto-increment) |
| job_id | BIGINT | Foreign key to personalization_jobs |
| created_at | TIMESTAMP | When the output was created |
| output_json | JSONB | Claude API response (structured JSON) |

## Setup Instructions

### Option 1: Using Supabase Dashboard

1. Go to your Supabase project dashboard
2. Navigate to the SQL Editor
3. Copy the contents of `migrations/001_create_personalization_tables.sql`
4. Paste and execute the SQL

### Option 2: Using Supabase CLI

```bash
# Install Supabase CLI (if not already installed)
npm install -g supabase

# Login to Supabase
supabase login

# Link to your project
supabase link --project-ref your-project-ref

# Run migrations
supabase db push
```

### Option 3: Using Deployment Script

```bash
# Set environment variables
export SUPABASE_ACCESS_TOKEN=your_token
export SUPABASE_PROJECT_REF=your_project_ref

# Run deployment script
./scripts/deploy-backend-supabase.sh
```

## Environment Variables Required

After creating the tables, you need to configure these environment variables:

```bash
NEXT_PUBLIC_SUPABASE_URL=https://your-project.supabase.co
NEXT_PUBLIC_SUPABASE_ANON_KEY=your_anon_key
SUPABASE_SERVICE_ROLE=your_service_role_key
```

Get these values from:
Supabase Dashboard → Settings → API

## Testing the Setup

After running the migration, verify the tables exist:

```sql
SELECT table_name
FROM information_schema.tables
WHERE table_schema = 'public'
AND table_name IN ('personalization_jobs', 'personalization_outputs');
```

## Security Notes

- Row Level Security (RLS) is enabled but set to allow all access for alpha
- In production, implement proper RLS policies
- Use service role key only on the server side
- Never expose service role key to clients
