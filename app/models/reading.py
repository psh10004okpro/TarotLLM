"""
Tarot Reading Data Models
"""

from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from datetime import datetime
from enum import Enum
from app.models.tarot_card import DrawnCard, CardOrientation


class SpreadType(str, Enum):
    """Types of tarot spreads"""
    SINGLE_CARD = "one_card"
    THREE_CARD = "three_card"  # Past, Present, Future
    CELTIC_CROSS = "celtic_cross"
    RELATIONSHIP = "relationship"
    CAREER = "career"
    CUSTOM = "custom"


class CardInput(BaseModel):
    """Input card for manual selection"""
    card_id: str = Field(..., description="Card identifier (e.g., 'major_00_fool', 'wands_ace')")
    position: Optional[str] = Field(None, description="Position in spread (e.g., 'past', 'present', 'future')")
    orientation: str = Field("upright", description="Card orientation: 'upright' or 'reversed'")

    class Config:
        json_schema_extra = {
            "example": {
                "card_id": "major_00_fool",
                "position": "past",
                "orientation": "upright"
            }
        }


class ReadingSettings(BaseModel):
    """Settings for tarot reading"""
    interpret_reversed: bool = Field(True, description="Whether to interpret reversed cards")
    use_optimized_prompts: bool = Field(True, description="Use 2-stage prompt system")
    include_card_images: bool = Field(False, description="Include card image URLs in response")

    class Config:
        json_schema_extra = {
            "example": {
                "interpret_reversed": True,
                "use_optimized_prompts": True,
                "include_card_images": False
            }
        }


class ReadingRequest(BaseModel):
    """Request for a tarot reading"""
    user_id: str = Field(..., description="User identifier")
    tarot_master: str = Field("master_1", description="Tarot master ID: master_1, master_2, or master_3")
    concern: Optional[str] = Field(None, description="User's concern or question")
    spread_type: SpreadType = Field(SpreadType.THREE_CARD, description="Type of spread")
    cards: Optional[List[CardInput]] = Field(None, description="Manually selected cards (optional, will be drawn if not provided)")
    settings: Optional[ReadingSettings] = Field(default_factory=ReadingSettings, description="Reading settings")

    class Config:
        json_schema_extra = {
            "example": {
                "user_id": "user123",
                "tarot_master": "master_1",
                "concern": "최근 새로운 일을 시작하려고 하는데 잘 될지 궁금합니다",
                "spread_type": "three_card",
                "cards": [
                    {"card_id": "major_00_fool", "position": "past", "orientation": "upright"},
                    {"card_id": "wands_ace", "position": "present", "orientation": "upright"},
                    {"card_id": "cups_02", "position": "future", "orientation": "reversed"}
                ],
                "settings": {
                    "interpret_reversed": True
                }
            }
        }


class TarotMasterInfo(BaseModel):
    """Tarot master information in response"""
    id: str = Field(..., description="Tarot master ID (master_1, master_2, master_3)")
    name: str = Field(..., description="Tarot master name in Korean")
    name_en: str = Field(..., description="Tarot master name in English")
    meeting_count: int = Field(..., description="Number of meetings with this user")

    class Config:
        json_schema_extra = {
            "example": {
                "id": "master_1",
                "name": "달빛의 현자",
                "name_en": "Sage of Moonlight",
                "meeting_count": 3
            }
        }


class ReadingResponse(BaseModel):
    """Response from a tarot reading"""
    reading_id: str = Field(..., description="Unique reading identifier")
    tarot_master: TarotMasterInfo = Field(..., description="Tarot master who performed the reading")
    interpretation: str = Field(..., description="Full reading interpretation")
    cards_analyzed: List[DrawnCard] = Field(..., description="Cards that were analyzed")
    timestamp: datetime = Field(default_factory=datetime.now, description="Reading timestamp")
    metadata: Optional[Dict[str, Any]] = Field(None, description="Additional metadata (prompt info, tokens, etc.)")

    class Config:
        json_schema_extra = {
            "example": {
                "reading_id": "reading_uuid",
                "tarot_master": {
                    "id": "master_1",
                    "name": "달빛의 현자",
                    "name_en": "Sage of Moonlight",
                    "meeting_count": 3
                },
                "interpretation": "안녕하세요, 다시 만나뵙게 되어 반갑습니다...",
                "cards_analyzed": [],
                "timestamp": "2025-10-29T10:30:00Z",
                "metadata": {
                    "prompt_level": "short",
                    "prompt_tokens": 181,
                    "llm_provider": "claude"
                }
            }
        }


class ReadingHistory(BaseModel):
    """User's reading history"""
    user_id: str
    readings: List[ReadingResponse]
    total_readings: int
    first_reading_date: Optional[datetime] = None
    last_reading_date: Optional[datetime] = None


class SessionRequest(BaseModel):
    """Request to create or get a session"""
    user_id: str = Field(..., description="User identifier")
    tarot_master: Optional[str] = Field(None, description="Preferred tarot master (master_1, master_2, master_3)")
    user_name: Optional[str] = Field(None, description="User's name for personalized readings")

    class Config:
        json_schema_extra = {
            "example": {
                "user_id": "user123",
                "tarot_master": "master_1",
                "user_name": "민수"
            }
        }


class SessionResponse(BaseModel):
    """Session information response"""
    session_id: str = Field(..., description="Session identifier")
    user_id: str = Field(..., description="User identifier")
    user_name: Optional[str] = Field(None, description="User's name")
    tarot_master_meetings: Dict[str, int] = Field(..., description="Meeting count per tarot master")
    total_interactions: int = Field(..., description="Total number of interactions")
    created_at: datetime = Field(..., description="Session creation timestamp")
    last_interaction: Optional[datetime] = Field(None, description="Last interaction timestamp")

    class Config:
        json_schema_extra = {
            "example": {
                "session_id": "session_abc123",
                "user_id": "user123",
                "user_name": "민수",
                "tarot_master_meetings": {
                    "master_1": 5,
                    "master_2": 2,
                    "master_3": 1
                },
                "total_interactions": 8,
                "created_at": "2025-10-20T10:00:00Z",
                "last_interaction": "2025-10-29T10:30:00Z"
            }
        }
