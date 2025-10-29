"""
Tarot Card Data Models
"""

from pydantic import BaseModel, Field
from typing import Optional, List
from enum import Enum


class CardSuit(str, Enum):
    """Tarot card suits"""
    MAJOR_ARCANA = "major_arcana"
    WANDS = "wands"
    CUPS = "cups"
    SWORDS = "swords"
    PENTACLES = "pentacles"


class CardOrientation(str, Enum):
    """Card orientation"""
    UPRIGHT = "upright"
    REVERSED = "reversed"


class TarotCard(BaseModel):
    """Tarot card model"""
    id: int = Field(..., description="Card ID (0-77)")
    name: str = Field(..., description="Card name")
    name_ko: str = Field(..., description="Korean card name")
    suit: CardSuit = Field(..., description="Card suit")
    number: Optional[int] = Field(None, description="Card number in suit")
    keywords_upright: List[str] = Field(default_factory=list, description="Upright keywords")
    keywords_reversed: List[str] = Field(default_factory=list, description="Reversed keywords")
    description: str = Field(..., description="Card description")
    image_url: Optional[str] = Field(None, description="Card image URL")


class DrawnCard(BaseModel):
    """Drawn tarot card with orientation"""
    card: TarotCard
    orientation: CardOrientation
    position: Optional[str] = Field(None, description="Position in spread (e.g., 'past', 'present', 'future')")

    class Config:
        json_schema_extra = {
            "example": {
                "card": {
                    "id": 0,
                    "name": "The Fool",
                    "name_ko": "광대",
                    "suit": "major_arcana",
                    "keywords_upright": ["new beginnings", "innocence", "spontaneity"],
                    "keywords_reversed": ["recklessness", "fear", "bad decision"],
                    "description": "The Fool represents new beginnings and unlimited potential"
                },
                "orientation": "upright",
                "position": "present"
            }
        }
