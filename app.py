"""Extension declaration, capabilities, health check for Later Connector."""
from __future__ import annotations
import json
from imperal_sdk import ChatExtension, Extension

ext = Extension(
    "later-connector",
    version="0.1.0",
    display_name="Later",
    icon="icon.svg",
    capabilities=["later:manage"],
    description="Official Imperal connector for Later (C30. Email Marketing & Newsletter). Manage operations securely."
)

chat = ChatExtension(ext)

@ext.health_check
async def health_check(ctx) -> dict:
    raw = await ctx.secrets.get("later_connections")
    try:
        count = len(json.loads(raw)) if raw else 0
    except Exception:
        count = 0
    return {
        "healthy": True,
        "detail": f"{count} Later connection(s) configured." if count else "Not connected yet."
    }
