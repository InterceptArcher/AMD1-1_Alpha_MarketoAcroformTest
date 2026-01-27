#!/bin/bash
set -euo pipefail

##############################################################################
# Vercel Frontend Deployment Script
#
# This script deploys the Next.js frontend to Vercel.
# It reads credentials from environment variables and fails fast on errors.
#
# REQUIRED ENVIRONMENT VARIABLES:
# - VERCEL_TOKEN: Vercel authentication token
# - VERCEL_ORG_ID: Vercel organization ID (optional, will be created if missing)
# - VERCEL_PROJECT_ID: Vercel project ID (optional, will be created if missing)
#
# USAGE:
#   ./scripts/deploy-frontend-vercel.sh [--production]
#
# OPTIONS:
#   --production    Deploy to production (default: preview)
##############################################################################

echo "=== Vercel Frontend Deployment ==="
echo

# Check for required environment variable
if [ -z "${VERCEL_TOKEN:-}" ]; then
  echo "ERROR: VERCEL_TOKEN environment variable is not set."
  echo "This value must be provided via environment variables."
  exit 1
fi

# Determine deployment target
PRODUCTION_FLAG=""
if [ "${1:-}" = "--production" ]; then
  PRODUCTION_FLAG="--prod"
  echo "Deployment target: PRODUCTION"
else
  echo "Deployment target: PREVIEW"
fi
echo

# Install Vercel CLI if not present
if ! command -v vercel &> /dev/null; then
  echo "Installing Vercel CLI..."
  npm install -g vercel@latest
  echo
fi

# Load existing project IDs from .env if they exist
if [ -f .env ]; then
  echo "Loading existing configuration from .env..."
  export $(grep -v '^#' .env | xargs)
  echo
fi

# Run build to ensure code compiles
echo "Building Next.js application..."
npm run build
echo

# Link or create Vercel project
echo "Linking to Vercel project..."
if [ -n "${VERCEL_PROJECT_ID:-}" ] && [ -n "${VERCEL_ORG_ID:-}" ]; then
  echo "Using existing project configuration:"
  echo "  Project ID: ${VERCEL_PROJECT_ID}"
  echo "  Org ID: ${VERCEL_ORG_ID}"
else
  echo "Creating new Vercel project..."

  # Create project and capture output
  VERCEL_OUTPUT=$(vercel --token="${VERCEL_TOKEN}" --yes 2>&1)

  # Extract project info from vercel.json or output
  if [ -f .vercel/project.json ]; then
    VERCEL_PROJECT_ID=$(jq -r '.projectId' .vercel/project.json)
    VERCEL_ORG_ID=$(jq -r '.orgId' .vercel/project.json)

    echo "New project created:"
    echo "  Project ID: ${VERCEL_PROJECT_ID}"
    echo "  Org ID: ${VERCEL_ORG_ID}"

    # Write to .env for future deployments
    {
      echo "VERCEL_PROJECT_ID=${VERCEL_PROJECT_ID}"
      echo "VERCEL_ORG_ID=${VERCEL_ORG_ID}"
    } >> .env

    echo
    echo "Project IDs saved to .env"
  fi
fi
echo

# Deploy to Vercel
echo "Deploying to Vercel..."
DEPLOYMENT_URL=$(vercel deploy --token="${VERCEL_TOKEN}" ${PRODUCTION_FLAG} --yes 2>&1 | grep -Eo 'https://[a-zA-Z0-9.-]+\.vercel\.app' | head -1)

echo
echo "=== Deployment Complete ==="
echo
echo "Deployed URL: ${DEPLOYMENT_URL}"
echo
echo "Note: This value must be provided via environment variables."
echo "      Credentials are NOT stored in this repository."
echo

# Exit successfully
exit 0
