#!/bin/bash
set -euo pipefail

##############################################################################
# Supabase Backend Deployment Script
#
# This script deploys database migrations to Supabase.
# It reads credentials from environment variables and fails fast on errors.
#
# REQUIRED ENVIRONMENT VARIABLES:
# - SUPABASE_ACCESS_TOKEN: Supabase authentication token
# - SUPABASE_PROJECT_REF: Supabase project reference ID
#
# USAGE:
#   ./scripts/deploy-backend-supabase.sh
##############################################################################

echo "=== Supabase Backend Deployment ==="
echo

# Check for required environment variables
if [ -z "${SUPABASE_ACCESS_TOKEN:-}" ]; then
  echo "ERROR: SUPABASE_ACCESS_TOKEN environment variable is not set."
  echo "This value must be provided via environment variables."
  exit 1
fi

if [ -z "${SUPABASE_PROJECT_REF:-}" ]; then
  echo "ERROR: SUPABASE_PROJECT_REF environment variable is not set."
  echo "Get this from your Supabase project settings."
  exit 1
fi

# Install Supabase CLI if not present
if ! command -v supabase &> /dev/null; then
  echo "Installing Supabase CLI..."
  npm install -g supabase
  echo
fi

# Login to Supabase
echo "Authenticating with Supabase..."
supabase login --token "${SUPABASE_ACCESS_TOKEN}"
echo

# Link to project
echo "Linking to Supabase project: ${SUPABASE_PROJECT_REF}..."
supabase link --project-ref "${SUPABASE_PROJECT_REF}"
echo

# Run migrations
echo "Running database migrations..."
if [ -d "supabase/migrations" ]; then
  supabase db push
  echo
  echo "Migrations applied successfully!"
else
  echo "No migrations directory found. Skipping migrations."
  echo "Expected directory: supabase/migrations"
fi
echo

# Verify tables exist
echo "Verifying tables..."
supabase db remote list
echo

echo "=== Deployment Complete ==="
echo
echo "Database tables have been created/updated."
echo "Note: Credentials are NOT stored in this repository."
echo

# Exit successfully
exit 0
