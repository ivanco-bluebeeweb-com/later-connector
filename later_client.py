"""HTTP client for Later API v1."""
from __future__ import annotations
import httpx
from typing import Any, Optional

DEFAULT_BASE = "https://app.later.com/api/v2"

class LaterClient:
    def __init__(self, access_token: str, base_url: str = ""):
        self.token = access_token.strip()
        self.base_url = (base_url.strip() if base_url else DEFAULT_BASE).rstrip("/")
        self.headers = {
            "Authorization": f"Bearer {self.token}",
            "Content-Type": "application/json",
            "User-Agent": "Imperal-Later-Connector/1.0.0"
        }
        self.timeout = httpx.Timeout(30.0, connect=10.0)

    async def verify_auth(self) -> dict[str, Any]:
        async with httpx.AsyncClient(timeout=self.timeout) as client:
            try:
                resp = await client.get(f"{self.base_url}/users/me", headers=self.headers)
                if resp.status_code in (200, 201):
                    return {"status": "ok", "data": resp.json()}
                return {"status": "error", "error": f"HTTP {resp.status_code}: {resp.text}"}
            except Exception as e:
                return {"status": "error", "error": str(e)}

    async def list_profiles(self) -> list[dict[str, Any]]:
        async with httpx.AsyncClient(timeout=self.timeout) as client:
            resp = await client.get(f"{self.base_url}/users/me", headers=self.headers)
            resp.raise_for_status()
            data = resp.json()
            return data if isinstance(data, list) else data.get("profiles", [])

    async def list_media(self) -> list[dict[str, Any]]:
        async with httpx.AsyncClient(timeout=self.timeout) as client:
            resp = await client.get(f"{self.base_url}/media", headers=self.headers)
            resp.raise_for_status()
            data = resp.json()
            return data if isinstance(data, list) else data.get("media", [])

    async def list_posts(self, profile_id: Optional[str] = None) -> list[dict[str, Any]]:
        async with httpx.AsyncClient(timeout=self.timeout) as client:
            params = {}
            if profile_id:
                params["profile_id"] = profile_id
            resp = await client.get(f"{self.base_url}/posts", headers=self.headers, params=params)
            resp.raise_for_status()
            data = resp.json()
            return data if isinstance(data, list) else data.get("posts", [])

    async def create_post(self, profile_id: str, text: str, scheduled_time: Optional[str] = None, media_ids: Optional[list[str]] = None) -> dict[str, Any]:
        async with httpx.AsyncClient(timeout=self.timeout) as client:
            payload = {
                "profile_id": profile_id,
                "text": text,
                "scheduled_time": scheduled_time,
                "media_ids": media_ids or []
            }
            resp = await client.post(f"{self.base_url}/posts", headers=self.headers, json=payload)
            resp.raise_for_status()
            return resp.json()

    async def delete_post(self, post_id: str) -> bool:
        async with httpx.AsyncClient(timeout=self.timeout) as client:
            resp = await client.delete(f"{self.base_url}/posts/{post_id}", headers=self.headers)
            resp.raise_for_status()
            return True
