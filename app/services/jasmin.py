"""Jasmin SMS Gateway REST API client."""

from __future__ import annotations

import logging
import httpx
from app.core.config import settings

logger = logging.getLogger("jasmin")

class JasminService:
    def __init__(self):
        self.base_url = settings.JASMIN_API_URL.rstrip("/")
        self.auth = (settings.JASMIN_USER, settings.JASMIN_PASSWORD)

    async def send_sms(
        self,
        to_phone: str,
        message: str,
        from_id: str | None = None,
    ) -> dict:
        """Send an SMS via Jasmin REST API."""
        url = f"{self.base_url}/send"
        
        # Standard Jasmin REST API parameters
        params = {
            "to": to_phone,
            "content": message,
        }
        if from_id:
            params["from"] = from_id

        try:
            async with httpx.AsyncClient() as client:
                resp = await client.post(
                    url, 
                    params=params, 
                    auth=self.auth, 
                    timeout=30.0
                )
                resp.raise_for_status()
                data = resp.json()
                logger.info(f"Jasmin SMS sent to {to_phone}")
                return {"success": True, "data": data}
        except Exception as exc:
            logger.error(f"[JASMIN ERROR] {exc}")
            return {"success": False, "error": str(exc)}

    async def get_balance(self) -> dict:
        """Check user account balance/quota."""
        url = f"{self.base_url}/balance"
        try:
            async with httpx.AsyncClient() as client:
                resp = await client.get(url, auth=self.auth, timeout=15.0)
                resp.raise_for_status()
                return resp.json()
        except Exception as exc:
            logger.error(f"[JASMIN BALANCE ERROR] {exc}")
            return {"success": False, "error": str(exc)}

jasmin_svc = JasminService()
