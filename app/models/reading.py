"""
Tarot Reading Data Models
"""

from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime
from enum import Enum
from app.models.tarot_card import DrawnCard


class SpreadType(str, Enum):
    """Types of tarot spreads"""
    SINGLE_CARD = "single_card"
    THREE_CARD = "three_card"  # Past, Present, Future
    CELTIC_CROSS = "celtic_cross"
    RELATIONSHIP = "relationship"
    CAREER = "career"
    CUSTOM = "custom"


class ReadingRequest(BaseModel):
    """Request for a tarot reading"""
    user_id: str = Field(..., description="User identifier")
    question: Optional[str] = Field(None, description="User's question")
    spread_type: SpreadType = Field(SpreadType.THREE_CARD, description="Type of spread")
    llm_provider: Optional[str] = Field(None, description="Preferred LLM provider (claude/openai/gemini)")
    tarot_master_id: Optional[int] = Field(None, description="Tarot master persona ID (1-3)")

    class Config:
        json_schema_extra = {
            "example": {
                "user_id": "user_12345",
                "question": "What should I focus on in my career?",
                "spread_type": "three_card",
                "llm_provider": "claude",
                "tarot_master_id": 1
            }
        }


class ReadingResponse(BaseModel):
    """Response from a tarot reading"""
    reading_id: str = Field(..., description="Unique reading identifier")
    user_id: str = Field(..., description="User identifier")
    timestamp: datetime = Field(default_factory=datetime.now, description="Reading timestamp")
    spread_type: SpreadType = Field(..., description="Type of spread used")
    cards: List[DrawnCard] = Field(..., description="Drawn cards")
    interpretation: str = Field(..., description="Full reading interpretation")
    summary: Optional[str] = Field(None, description="Brief summary")
    llm_provider_used: str = Field(..., description="LLM provider used")
    tarot_master_id: int = Field(..., description="Tarot master persona used")

    class Config:
        json_schema_extra = {
            "example": {
                "reading_id": "reading_abc123",
                "user_id": "user_12345",
                "timestamp": "2024-01-15T10:30:00",
                "spread_type": "three_card",
                "cards": [],
                "interpretation": "Based on your cards...",
                "summary": "Focus on new opportunities",
                "llm_provider_used": "claude",
                "tarot_master_id": 1
            }
        }


class ReadingHistory(BaseModel):
    """User's reading history"""
    user_id: str
    readings: List[ReadingResponse]
    total_readings: int
    first_reading_date: Optional[datetime] = None
    last_reading_date: Optional[datetime] = None
