"""Pydantic schemas for Later Connector (C31. Social Media Management)."""
from __future__ import annotations
from typing import Any, Optional, List, Dict
from pydantic import BaseModel, Field

class NoParams(BaseModel):
    """Empty parameters model."""
    pass

class ConnectParams(BaseModel):
    label: str = Field(default="", description="Friendly connection label, e.g. Later Main.")
    access_token: str = Field(description="Later OAuth 2.0 Access Token.")
    base_url: str = Field(default="https://app.later.com/api/v2", description="Later API base URL.")

class ConnectionIdParams(BaseModel):
    connection_id: str = Field(default="", description="Connection identifier (empty uses active connection).")

class ConnectionRecord(BaseModel):
    id: str
    label: str
    masked_key: str
    base_url: str
    is_active: bool

class ConnectionList(BaseModel):
    connections: list[ConnectionRecord]
    total: int

class DeleteResult(BaseModel):
    success: bool
    message: str

class ProfileRecord(BaseModel):
    id: str
    platform: str
    username: str
    status: str
    raw: Dict[str, Any] = Field(default_factory=dict)

class ProfileList(BaseModel):
    profiles: list[ProfileRecord]
    total: int

class ListProfilesParams(BaseModel):
    connection_id: str = Field(default="", description="Optional connection ID.")

class MediaItem(BaseModel):
    id: str
    name: str
    url: Optional[str] = None
    media_type: str
    created_at: Optional[str] = None

class MediaList(BaseModel):
    media: list[MediaItem]
    total: int

class ListMediaParams(BaseModel):
    connection_id: str = Field(default="", description="Optional connection ID.")

class PostRecord(BaseModel):
    id: str
    profile_id: str
    text: str
    status: str
    scheduled_time: Optional[str] = None
    media_ids: List[str] = Field(default_factory=list)

class PostList(BaseModel):
    posts: list[PostRecord]
    total: int

class ListPostsParams(BaseModel):
    connection_id: str = Field(default="", description="Optional connection ID.")
    profile_id: Optional[str] = Field(default=None, description="Optional profile ID filter.")

class CreatePostParams(BaseModel):
    connection_id: str = Field(default="", description="Optional connection ID.")
    profile_id: str = Field(description="Target profile ID.")
    text: str = Field(description="Caption / text of the post.")
    scheduled_time: Optional[str] = Field(default=None, description="ISO datetime string for scheduled publication.")
    media_ids: List[str] = Field(default_factory=list, description="IDs of media items to attach.")

class DeletePostParams(BaseModel):
    connection_id: str = Field(default="", description="Optional connection ID.")
    post_id: str = Field(description="Later post ID to delete.")

class AuditHealthReport(BaseModel):
    status: str
    total_profiles: int
    media_items_count: int
    recommendations: List[str]
