"""
Tarot Card Data Models
Enhanced structure for comprehensive tarot readings
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
    """
    Comprehensive tarot card model with detailed interpretations

    This model supports the full Korean tarot card database structure
    with context-specific meanings for various life situations.
    """
    # Basic identification
    card: str = Field(..., description="Card identifier (e.g., '0. THE FOOL / 바보(광대) / 메이저 아르카나')")

    # Visual description
    image_description: str = Field(..., description="Detailed visual description of the card imagery")

    # Keywords (mixed upright and reversed)
    keywords: List[str] = Field(default_factory=list, description="Keywords representing card meanings")

    # Context-specific interpretations
    love: str = Field("", description="Love and romance interpretation")
    relationship: str = Field("", description="Relationships and social connections")
    finance: str = Field("", description="Financial and material matters")
    education_career_business: str = Field("", description="Career, education, and business matters")
    reunion: str = Field("", description="Reunion and reconciliation interpretation")
    contract: str = Field("", description="Contracts and agreements")
    travel_moving: str = Field("", description="Travel and relocation matters")
    job_change: str = Field("", description="Job change and career transitions")
    health: str = Field("", description="Health and wellness interpretation")

    # Symbolic meanings
    places: str = Field("", description="Associated places and locations")
    mood: str = Field("", description="Emotional and psychological state")
    numerology: str = Field("", description="Numerological significance")
    symbolism: str = Field("", description="Visual symbolism and imagery meanings")

    # Guidance
    advice: str = Field("", description="Advice and positive guidance")
    caution: str = Field("", description="Warnings and cautions")

    # Helper properties for backward compatibility
    @property
    def id(self) -> int:
        """Extract card ID from card string"""
        try:
            # Extract number from card string like "0. THE FOOL" or "ACE of CUPS"
            card_str = self.card.split("/")[0].strip()

            # Major Arcana (0-21)
            if card_str[0].isdigit():
                return int(card_str.split(".")[0])

            # Minor Arcana - assign IDs 22-77
            suit_order = ["CUPS", "SWORDS", "WANDS", "PENTACLES"]
            rank_order = ["ACE", "TWO", "THREE", "FOUR", "FIVE", "SIX", "SEVEN",
                         "EIGHT", "NINE", "TEN", "PAGE", "KNIGHT", "QUEEN", "KING"]

            for suit_idx, suit in enumerate(suit_order):
                if suit in card_str:
                    for rank_idx, rank in enumerate(rank_order):
                        if rank in card_str:
                            return 22 + (suit_idx * 14) + rank_idx

            return 0  # Fallback
        except Exception:
            return 0

    @property
    def name(self) -> str:
        """Extract English name from card string"""
        try:
            parts = self.card.split("/")
            if len(parts) >= 1:
                name = parts[0].strip()
                # Remove number prefix for Major Arcana
                if name[0].isdigit():
                    name = name.split(".", 1)[1].strip()
                return name
            return self.card
        except Exception:
            return self.card

    @property
    def name_ko(self) -> str:
        """Extract Korean name from card string"""
        try:
            parts = self.card.split("/")
            if len(parts) >= 2:
                return parts[1].strip()
            return ""
        except Exception:
            return ""

    @property
    def suit(self) -> CardSuit:
        """Determine card suit from card string"""
        card_upper = self.card.upper()

        if "메이저 아르카나" in self.card or "MAJOR" in card_upper:
            return CardSuit.MAJOR_ARCANA
        elif "WANDS" in card_upper or "완드" in self.card:
            return CardSuit.WANDS
        elif "CUPS" in card_upper or "컵" in self.card:
            return CardSuit.CUPS
        elif "SWORDS" in card_upper or "소드" in self.card:
            return CardSuit.SWORDS
        elif "PENTACLES" in card_upper or "펜타클" in self.card:
            return CardSuit.PENTACLES

        return CardSuit.MAJOR_ARCANA

    class Config:
        json_schema_extra = {
            "example": {
                "card": "0. THE FOOL / 바보(광대) / 메이저 아르카나",
                "image_description": "그림 속 남자는 화려한 옷을 입고...",
                "keywords": ["자유로운", "새로운 출발", "순수함"],
                "love": "자유로운 연애를 추구하는 성향...",
                "relationship": "가벼운 사이, 함께하면 즐거운 만남...",
                "finance": "돈욕심이 없는, 계획성 없는소비...",
                "advice": "조금 더 집착을 놓아줄 필요가 있습니다.",
                "caution": "현재너무계획성이 없을지 모릅니다."
            }
        }


class DrawnCard(BaseModel):
    """Drawn tarot card with orientation"""
    card: TarotCard
    orientation: CardOrientation
    position: Optional[str] = Field(None, description="Position in spread (e.g., 'past', 'present', 'future')")

    def get_interpretation(self, context: str = "general") -> str:
        """
        Get context-specific interpretation

        Args:
            context: Context type (love, finance, career, etc.)

        Returns:
            Relevant interpretation text
        """
        context_map = {
            "love": self.card.love,
            "relationship": self.card.relationship,
            "finance": self.card.finance,
            "career": self.card.education_career_business,
            "business": self.card.education_career_business,
            "reunion": self.card.reunion,
            "contract": self.card.contract,
            "travel": self.card.travel_moving,
            "health": self.card.health,
            "job_change": self.card.job_change
        }

        interpretation = context_map.get(context, "")

        # Add orientation context
        if self.orientation == CardOrientation.REVERSED:
            interpretation += "\n\n[역방향] 이 카드의 에너지가 반전되거나 내면화되어 있습니다."

        return interpretation or self.card.image_description

    class Config:
        json_schema_extra = {
            "example": {
                "card": {
                    "card": "0. THE FOOL / 바보(광대) / 메이저 아르카나",
                    "keywords": ["자유로운", "새로운 출발", "순수함"]
                },
                "orientation": "upright",
                "position": "present"
            }
        }
