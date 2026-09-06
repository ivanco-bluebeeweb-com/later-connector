"""Connection lifecycle handlers for Later Connector."""
from __future__ import annotations
import uuid
from typing import Any
from imperal_sdk import ActionResult
from app import chat
from schemas import (
    ConnectParams, ConnectionIdParams, ConnectionRecord, ConnectionList, DeleteResult, NoParams
)
from later_client import LaterClient

CONNECTIONS_KEY = "later_connections"
ACTIVE_KEY = "later_active_connection"

def _mask(s: str) -> str:
    if len(s) <= 8:
        return "..." + s[-4:] if len(s) >= 4 else "..."
    return s[:4] + "..." + s[-4:]

async def resolve_client(ctx, connection_id: str = "") -> LaterClient:
    conns = await ctx.store.get(CONNECTIONS_KEY) or {}
    if not conns:
        raise ValueError("No Later connections found. Connect an account first.")
    cid = connection_id.strip() if connection_id else (await ctx.store.get(ACTIVE_KEY) or "")
    if not cid or cid not in conns:
        cid = next(iter(conns))
    rec = conns[cid]
    secret = await ctx.secrets.get(f"later_{cid}")
    if not secret:
        raise ValueError(f"Secret for connection {cid} not found.")
    return LaterClient(secret, rec.get("base_url", ""))

@chat.function("connect_later", "Connect your Later account with an OAuth 2.0 access token.", action_type="write", chain_callable=True, event="later-connector.connect_later", effects=["create:connection"], data_model=ConnectionRecord)
async def connect_later(ctx, params: ConnectParams) -> ActionResult:
    client = LaterClient(params.access_token, params.base_url)
    res = await client.verify_auth()
    if res.get("status") == "error":
        return ActionResult.error(f"Failed to connect to Later: {res.get('error')}")

    cid = str(uuid.uuid4())[:8]
    lbl = params.label.strip() or f"Later ({cid})"
    await ctx.secrets.set(f"later_{cid}", params.access_token.strip())

    conns = await ctx.store.get(CONNECTIONS_KEY) or {}
    conns[cid] = {
        "id": cid,
        "label": lbl,
        "masked_key": _mask(params.access_token),
        "base_url": params.base_url.strip(),
        "is_active": True
    }
    for c in conns:
        if c != cid:
            conns[c]["is_active"] = False
    await ctx.store.set(CONNECTIONS_KEY, conns)
    await ctx.store.set(ACTIVE_KEY, cid)

    rec = ConnectionRecord(**conns[cid])
    return ActionResult.ok(rec, summary=f"Connected to Later ({lbl}).")

@chat.function("list_connections", "List connected Later accounts.", action_type="read", chain_callable=True, event="later-connector.list_connections", effects=["read:connections"], data_model=ConnectionList)
async def list_connections(ctx, params: NoParams) -> ActionResult:
    conns = await ctx.store.get(CONNECTIONS_KEY) or {}
    records = [ConnectionRecord(**c) for c in conns.values()]
    return ActionResult.ok(ConnectionList(connections=records, total=len(records)), summary=f"Found {len(records)} Later connections.")

@chat.function("disconnect_later", "Disconnect a Later account and remove stored credentials.", action_type="destructive", chain_callable=False, event="later-connector.disconnect_later", effects=["delete:connection"], data_model=DeleteResult)
async def disconnect_later(ctx, params: ConnectionIdParams) -> ActionResult:
    conns = await ctx.store.get(CONNECTIONS_KEY) or {}
    cid = params.connection_id.strip() if params.connection_id else (await ctx.store.get(ACTIVE_KEY) or "")
    if not cid or cid not in conns:
        return ActionResult.error(f"Connection {cid} not found.")

    await ctx.secrets.delete(f"later_{cid}")
    del conns[cid]
    await ctx.store.set(CONNECTIONS_KEY, conns)
    if (await ctx.store.get(ACTIVE_KEY)) == cid:
        new_active = next(iter(conns)) if conns else ""
        await ctx.store.set(ACTIVE_KEY, new_active)

    return ActionResult.ok(DeleteResult(success=True, message=f"Disconnected Later connection {cid}."), summary=f"Disconnected Later account {cid}.")
