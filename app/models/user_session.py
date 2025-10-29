"""
User Session Data Models
Session management for tracking user interactions
"""

from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from datetime import datetime
from enum import Enum


class SessionStatus(str, Enum):
    """Session status"""
    ACTIVE = "active"
    EXPIRED = "expired"
    CLOSED = "closed"


class UserSession(BaseModel):
    """User session model for tracking interactions"""
    session_id: str = Field(..., description="Unique session identifier")
    user_id: str = Field(..., description="User identifier")
    created_at: datetime = Field(default_factory=datetime.now, description="Session creation time")
    last_active: datetime = Field(default_factory=datetime.now, description="Last activity time")
    expires_at: datetime = Field(..., description="Session expiration time")
    status: SessionStatus = Field(SessionStatus.ACTIVE, description="Session status")

    # Interaction tracking
    interaction_count: int = Field(0, description="Number of interactions in this session")
    total_interactions: int = Field(0, description="Total interactions across all sessions")

    # Tarot master preference
    preferred_tarot_master: Optional[int] = Field(None, description="Preferred tarot master ID")
    preferred_llm_provider: Optional[str] = Field(None, description="Preferred LLM provider")

    # Context and memory
    conversation_history: List[Dict[str, Any]] = Field(default_factory=list, description="Conversation history")
    user_preferences: Dict[str, Any] = Field(default_factory=dict, description="User preferences")

    class Config:
        json_schema_extra = {
            "example": {
                "session_id": "session_xyz789",
                "user_id": "user_12345",
                "created_at": "2024-01-15T10:00:00",
                "last_active": "2024-01-15T10:30:00",
                "expires_at": "2024-01-16T10:00:00",
                "status": "active",
                "interaction_count": 3,
                "total_interactions": 15,
                "preferred_tarot_master": 1,
                "preferred_llm_provider": "claude"
            }
        }


class SessionCreate(BaseModel):
    """Request to create a new session"""
    user_id: str = Field(..., description="User identifier")

    class Config:
        json_schema_extra = {
            "example": {
                "user_id": "user_12345"
            }
        }


class SessionUpdate(BaseModel):
    """Request to update session"""
    interaction_count: Optional[int] = None
    preferred_tarot_master: Optional[int] = None
    preferred_llm_provider: Optional[str] = None
    user_preferences: Optional[Dict[str, Any]] = None


class SessionResponse(BaseModel):
    """Session response with user relationship context"""
    session: UserSession
    is_returning_user: bool = Field(..., description="Whether user has previous sessions")
    relationship_context: str = Field(..., description="Context about user relationship (first time, returning, etc.)")

    class Config:
        json_schema_extra = {
            "example": {
                "session": {},
                "is_returning_user": True,
                "relationship_context": "You've met 15 times. Your bond grows stronger."
            }
        }
