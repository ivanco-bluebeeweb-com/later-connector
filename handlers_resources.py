"""Resource operational handlers for Later Connector (C31. Social Media Management)."""
from __future__ import annotations
from typing import Any
from imperal_sdk import ActionResult
from app import chat
from schemas import (
    ConnectionIdParams, ProfileRecord, ProfileList, ListProfilesParams,
    MediaItem, MediaList, ListMediaParams,
    PostRecord, PostList, ListPostsParams, CreatePostParams, DeletePostParams,
    DeleteResult, AuditHealthReport
)
from handlers_connection import resolve_client

@chat.function("list_profiles", "List social media profiles managed in Later.", action_type="read", chain_callable=True, event="later-connector.list_profiles", effects=["read:profiles"], data_model=ProfileList)
async def list_profiles(ctx, params: ListProfilesParams) -> ActionResult:
    client = await resolve_client(ctx, params.connection_id)
    try:
        raw_profiles = await client.list_profiles()
        profiles = []
        for p in raw_profiles:
            profiles.append(ProfileRecord(
                id=str(p.get("id", "")),
                platform=p.get("platform", "unknown"),
                username=p.get("username", "Unnamed"),
                status=p.get("status", "active"),
                raw=p
            ))
        return ActionResult.ok(ProfileList(profiles=profiles, total=len(profiles)), summary=f"Found {len(profiles)} social profiles.")
    except Exception as e:
        return ActionResult.error(f"Error fetching profiles: {e}")

@chat.function("list_media", "List media assets stored in Later library.", action_type="read", chain_callable=True, event="later-connector.list_media", effects=["read:media"], data_model=MediaList)
async def list_media(ctx, params: ListMediaParams) -> ActionResult:
    client = await resolve_client(ctx, params.connection_id)
    try:
        raw_media = await client.list_media()
        items = []
        for m in raw_media:
            items.append(MediaItem(
                id=str(m.get("id", "")),
                name=m.get("name", "Untitled"),
                url=m.get("url"),
                media_type=m.get("media_type", "image"),
                created_at=m.get("created_at")
            ))
        return ActionResult.ok(MediaList(media=items, total=len(items)), summary=f"Found {len(items)} media assets.")
    except Exception as e:
        return ActionResult.error(f"Error fetching media: {e}")

@chat.function("list_posts", "List scheduled or published posts in Later.", action_type="read", chain_callable=True, event="later-connector.list_posts", effects=["read:posts"], data_model=PostList)
async def list_posts(ctx, params: ListPostsParams) -> ActionResult:
    client = await resolve_client(ctx, params.connection_id)
    try:
        raw_posts = await client.list_posts(params.profile_id)
        posts = []
        for p in raw_posts:
            posts.append(PostRecord(
                id=str(p.get("id", "")),
                profile_id=str(p.get("profile_id", "")),
                text=p.get("text", ""),
                status=p.get("status", "scheduled"),
                scheduled_time=p.get("scheduled_time"),
                media_ids=p.get("media_ids", [])
            ))
        return ActionResult.ok(PostList(posts=posts, total=len(posts)), summary=f"Found {len(posts)} posts.")
    except Exception as e:
        return ActionResult.error(f"Error listing posts: {e}")

@chat.function("create_post", "Schedule a post in Later.", action_type="write", chain_callable=True, event="later-connector.create_post", effects=["create:post"], data_model=PostRecord)
async def create_post(ctx, params: CreatePostParams) -> ActionResult:
    client = await resolve_client(ctx, params.connection_id)
    try:
        res = await client.create_post(
            profile_id=params.profile_id,
            text=params.text,
            scheduled_time=params.scheduled_time,
            media_ids=params.media_ids
        )
        pid = str(res.get("id", "post-new"))
        rec = PostRecord(
            id=pid,
            profile_id=params.profile_id,
            text=params.text,
            status=res.get("status", "scheduled"),
            scheduled_time=params.scheduled_time,
            media_ids=params.media_ids
        )
        return ActionResult.ok(rec, summary=f"Scheduled post {pid}.")
    except Exception as e:
        return ActionResult.error(f"Error creating post: {e}")

@chat.function("delete_post", "Delete a scheduled post in Later.", action_type="destructive", chain_callable=True, event="later-connector.delete_post", effects=["delete:post"], data_model=DeleteResult)
async def delete_post(ctx, params: DeletePostParams) -> ActionResult:
    client = await resolve_client(ctx, params.connection_id)
    try:
        await client.delete_post(params.post_id)
        return ActionResult.ok(DeleteResult(success=True, message=f"Post {params.post_id} deleted."), summary=f"Deleted post {params.post_id}.")
    except Exception as e:
        return ActionResult.error(f"Error deleting post: {e}")

@chat.function("audit_social_health", "Audit Later social profiles and media queue health.", action_type="read", chain_callable=True, event="later-connector.audit_social_health", effects=["read:health"], data_model=AuditHealthReport)
async def audit_social_health(ctx, params: ConnectionIdParams) -> ActionResult:
    client = await resolve_client(ctx, params.connection_id)
    try:
        profiles = await client.list_profiles()
        media = await client.list_media()
        recs = []
        if not profiles:
            recs.append("No active social profiles found in Later.")
        if not media:
            recs.append("Media library is empty; upload visual assets before scheduling.")
        return ActionResult.ok(AuditHealthReport(
            status="healthy" if profiles else "warning",
            total_profiles=len(profiles),
            media_items_count=len(media),
            recommendations=recs
        ), summary=f"Later audit: {len(profiles)} profiles, {len(media)} media items.")
    except Exception as e:
        return ActionResult.error(f"Error auditing health: {e}")
