"""
Marketo API client for OAuth authentication and lead management.
Handles:
  - OAuth 2.0 token management (2-legged flow)
  - Lead record updates
  - Smart Campaign triggering for transactional emails
"""

import httpx
import logging
from datetime import datetime, timedelta
from typing import Optional, Dict, Any, List

from app.config import settings

logger = logging.getLogger(__name__)


class MarketoService:
    """
    Client for Marketo REST API.

    Authentication: 2-legged OAuth 2.0
    Rate limits: 100 calls/20 seconds, 50,000 calls/day
    """

    def __init__(self):
        """Initialize Marketo client with credentials from settings."""
        self.base_url = settings.MARKETO_BASE_URL
        self.identity_url = settings.MARKETO_IDENTITY_URL or (
            f"{self.base_url}/identity" if self.base_url else None
        )
        self.client_id = settings.MARKETO_CLIENT_ID
        self.client_secret = settings.MARKETO_CLIENT_SECRET
        self._access_token: Optional[str] = None
        self._token_expires_at: Optional[datetime] = None

    def is_configured(self) -> bool:
        """Check if Marketo credentials are configured."""
        return bool(
            self.base_url and
            self.client_id and
            self.client_secret
        )

    async def _get_access_token(self) -> str:
        """
        Get or refresh OAuth access token.

        Tokens expire after ~3600 seconds. We refresh 5 minutes early
        to avoid mid-request expiration.

        Returns:
            Valid access token

        Raises:
            httpx.HTTPError: If token request fails
        """
        if self._access_token and self._token_expires_at:
            if datetime.utcnow() < self._token_expires_at - timedelta(minutes=5):
                return self._access_token

        if not self.is_configured():
            raise ValueError("Marketo credentials not configured")

        logger.info("Fetching new Marketo access token")

        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.get(
                f"{self.identity_url}/oauth/token",
                params={
                    "grant_type": "client_credentials",
                    "client_id": self.client_id,
                    "client_secret": self.client_secret
                }
            )
            response.raise_for_status()
            data = response.json()

            if "error" in data:
                logger.error(f"Marketo token error: {data}")
                raise ValueError(f"Marketo auth failed: {data.get('error_description', data.get('error'))}")

            self._access_token = data["access_token"]
            self._token_expires_at = datetime.utcnow() + timedelta(
                seconds=data.get("expires_in", 3600)
            )
            logger.info("Marketo access token obtained successfully")
            return self._access_token

    async def update_lead(self, lead_id: str, fields: Dict[str, Any]) -> Dict[str, Any]:
        """
        Update lead record with new field values.

        Args:
            lead_id: Marketo lead ID
            fields: Dictionary of field names to values

        Returns:
            Marketo API response

        Raises:
            httpx.HTTPError: If API call fails
        """
        token = await self._get_access_token()

        payload = {
            "action": "updateOnly",
            "lookupField": "id",
            "input": [{
                "id": int(lead_id),
                **fields
            }]
        }

        logger.info(f"Updating Marketo lead {lead_id} with fields: {list(fields.keys())}")

        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.post(
                f"{self.base_url}/rest/v1/leads.json",
                headers={
                    "Authorization": f"Bearer {token}",
                    "Content-Type": "application/json"
                },
                json=payload
            )
            response.raise_for_status()
            data = response.json()

            if not data.get("success"):
                errors = data.get("errors", [])
                logger.error(f"Marketo lead update failed: {errors}")
                raise ValueError(f"Marketo update failed: {errors}")

            logger.info(f"Successfully updated Marketo lead {lead_id}")
            return data

    async def trigger_campaign(
        self,
        campaign_id: str,
        lead_id: str,
        tokens: Optional[Dict[str, str]] = None
    ) -> Dict[str, Any]:
        """
        Trigger a Smart Campaign for a lead.

        The campaign must have a "Campaign is Requested" trigger
        with source set to "Web Service API".

        Args:
            campaign_id: Marketo campaign ID
            lead_id: Lead ID to add to campaign
            tokens: Optional dict of my.token overrides

        Returns:
            Marketo API response

        Raises:
            httpx.HTTPError: If API call fails
        """
        token = await self._get_access_token()

        payload: Dict[str, Any] = {
            "input": {
                "leads": [{"id": int(lead_id)}]
            }
        }

        if tokens:
            payload["input"]["tokens"] = [
                {"name": f"{{{{my.{k}}}}}", "value": v}
                for k, v in tokens.items()
            ]

        logger.info(f"Triggering Marketo campaign {campaign_id} for lead {lead_id}")

        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.post(
                f"{self.base_url}/rest/v1/campaigns/{campaign_id}/trigger.json",
                headers={
                    "Authorization": f"Bearer {token}",
                    "Content-Type": "application/json"
                },
                json=payload
            )
            response.raise_for_status()
            data = response.json()

            if not data.get("success"):
                errors = data.get("errors", [])
                logger.error(f"Marketo campaign trigger failed: {errors}")
                raise ValueError(f"Marketo campaign trigger failed: {errors}")

            logger.info(f"Successfully triggered campaign {campaign_id} for lead {lead_id}")
            return data

    async def get_lead(self, lead_id: str) -> Optional[Dict[str, Any]]:
        """
        Fetch lead record by ID.

        Args:
            lead_id: Marketo lead ID

        Returns:
            Lead record or None if not found
        """
        token = await self._get_access_token()

        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.get(
                f"{self.base_url}/rest/v1/lead/{lead_id}.json",
                headers={
                    "Authorization": f"Bearer {token}"
                }
            )
            response.raise_for_status()
            data = response.json()

            if data.get("success") and data.get("result"):
                return data["result"][0]
            return None


# Singleton instance for reuse
_marketo_service: Optional[MarketoService] = None


def get_marketo_service() -> MarketoService:
    """Get or create MarketoService instance."""
    global _marketo_service
    if _marketo_service is None:
        _marketo_service = MarketoService()
    return _marketo_service
