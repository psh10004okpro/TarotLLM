"""
RAG (Retrieval-Augmented Generation) Service
Manages tarot card knowledge base and retrieval
Enhanced for comprehensive Korean tarot database
"""

from typing import List, Dict, Any, Optional
import json
from pathlib import Path
from app.models.tarot_card import TarotCard, CardSuit
from app.config import settings


class RAGService:
    """Service for managing tarot card knowledge and retrieval"""

    def __init__(self):
        """Initialize RAG service"""
        self.cards_data: List[TarotCard] = []
        self.vector_store = None  # 순환 import 방지를 위해 lazy loading
        self._load_data()

    def _load_data(self):
        """Load tarot cards data from JSON files"""
        try:
            # Load comprehensive tarot cards
            cards_path = Path("app/data/tarot_cards.json")
            if cards_path.exists():
                with open(cards_path, "r", encoding="utf-8") as f:
                    cards_json = json.load(f)
                    self.cards_data = [TarotCard(**card) for card in cards_json]
                    print(f"✓ Loaded {len(self.cards_data)} tarot cards")

        except Exception as e:
            print(f"Warning: Could not load tarot data: {e}")
            import traceback
            traceback.print_exc()

    def get_card_by_id(self, card_id: int) -> Optional[TarotCard]:
        """Get card by ID"""
        for card in self.cards_data:
            if card.id == card_id:
                return card
        return None

    def get_card_by_name(self, name: str) -> Optional[TarotCard]:
        """Get card by name (English or Korean)"""
        name_lower = name.lower()
        for card in self.cards_data:
            if name_lower in card.name.lower() or name in card.name_ko:
                return card
        return None

    def get_cards_by_suit(self, suit: CardSuit) -> List[TarotCard]:
        """Get all cards of a specific suit"""
        return [card for card in self.cards_data if card.suit == suit]

    def get_all_cards(self) -> List[TarotCard]:
        """Get all tarot cards"""
        return self.cards_data

    def get_card_meaning(
        self,
        card_id: int,
        orientation: str = "upright",
        context: Optional[str] = None
    ) -> str:
        """
        Get detailed meaning for a card

        Args:
            card_id: Card ID
            orientation: upright or reversed
            context: Additional context (e.g., love, finance, career)

        Returns:
            Detailed card meaning
        """
        card = self.get_card_by_id(card_id)
        if not card:
            return "Card not found"

        # Build comprehensive meaning
        meaning = f"【{card.name}】\n{card.name_ko}\n\n"

        # Add image description
        if card.image_description:
            meaning += f"이미지 설명:\n{card.image_description}\n\n"

        # Add keywords
        if card.keywords:
            meaning += f"키워드: {', '.join(card.keywords[:10])}\n\n"  # First 10 keywords

        # Add context-specific interpretation
        if context:
            context_meanings = {
                "love": ("연애", card.love),
                "relationship": ("인간관계", card.relationship),
                "finance": ("재물", card.finance),
                "career": ("직업/학업", card.education_career_business),
                "business": ("사업", card.education_career_business),
                "reunion": ("재회", card.reunion),
                "contract": ("계약", card.contract),
                "travel": ("여행/이사", card.travel_moving),
                "health": ("건강", card.health),
                "job_change": ("이직", card.job_change)
            }

            if context in context_meanings:
                ctx_name, ctx_meaning = context_meanings[context]
                if ctx_meaning:
                    meaning += f"[{ctx_name}]\n{ctx_meaning}\n\n"

        # Add symbolism if no specific context
        if not context and card.symbolism:
            meaning += f"상징:\n{card.symbolism[:300]}...\n\n"

        # Add advice
        if card.advice:
            meaning += f"조언:\n{card.advice}\n\n"

        # Add orientation note
        if orientation == "reversed":
            meaning += "\n[역방향] 카드의 에너지가 반전되거나 내면화됩니다.\n"
            if card.caution:
                meaning += f"주의사항:\n{card.caution}\n"

        return meaning

    def get_comprehensive_card_info(self, card_id: int) -> Dict[str, Any]:
        """
        Get all available information for a card

        Args:
            card_id: Card ID

        Returns:
            Dictionary with all card information
        """
        card = self.get_card_by_id(card_id)
        if not card:
            return {}

        return {
            "id": card.id,
            "name": card.name,
            "name_ko": card.name_ko,
            "suit": card.suit.value,
            "keywords": card.keywords,
            "image_description": card.image_description,
            "interpretations": {
                "love": card.love,
                "relationship": card.relationship,
                "finance": card.finance,
                "career": card.education_career_business,
                "reunion": card.reunion,
                "contract": card.contract,
                "travel_moving": card.travel_moving,
                "job_change": card.job_change,
                "health": card.health
            },
            "symbolic": {
                "places": card.places,
                "mood": card.mood,
                "numerology": card.numerology,
                "symbolism": card.symbolism
            },
            "guidance": {
                "advice": card.advice,
                "caution": card.caution
            }
        }

    def search_cards(self, query: str) -> List[TarotCard]:
        """
        Search cards by keyword or theme

        Args:
            query: Search query (Korean or English)

        Returns:
            List of matching cards
        """
        query_lower = query.lower()
        matching_cards = []

        for card in self.cards_data:
            # Search in card name
            if query_lower in card.card.lower():
                matching_cards.append(card)
                continue

            # Search in keywords
            if any(query in keyword for keyword in card.keywords):
                matching_cards.append(card)
                continue

            # Search in all text fields
            searchable_text = " ".join([
                card.love, card.relationship, card.finance,
                card.education_career_business, card.places,
                card.mood, card.advice
            ]).lower()

            if query_lower in searchable_text or query in searchable_text:
                matching_cards.append(card)

        return matching_cards

    def get_context_for_reading(
        self,
        cards: List[int],
        question: Optional[str] = None,
        context_type: Optional[str] = None,
        use_vector_search: bool = False
    ) -> str:
        """
        Get contextual information for a reading

        Args:
            cards: List of card IDs
            question: User's question
            context_type: Reading context (love, finance, career, etc.)
            use_vector_search: 벡터 검색을 사용할지 여부

        Returns:
            Context string for LLM
        """
        # 벡터 검색 사용 시
        if use_vector_search and question:
            # Lazy loading vector store to avoid circular import
            if self.vector_store is None:
                try:
                    from app.services.vector_store_service import vector_store
                    self.vector_store = vector_store
                except (ImportError, Exception):
                    # Vector store not available
                    pass

            if self.vector_store and self.vector_store.collection:
                return self.vector_store.get_context_for_cards(
                    card_ids=cards,
                    question=question,
                    context_type=context_type,
                    n_similar=3
                )

        # 기본 컨텍스트 생성 (벡터 검색 미사용 또는 실패 시)
        context = "타로 카드 정보:\n\n"

        for i, card_id in enumerate(cards, 1):
            card = self.get_card_by_id(card_id)
            if card:
                context += f"{i}. {card.name} ({card.name_ko})\n"
                context += f"   키워드: {', '.join(card.keywords[:5])}\n"

                # Add context-specific meaning if specified
                if context_type:
                    interpretation = ""
                    if context_type == "love":
                        interpretation = card.love
                    elif context_type == "finance":
                        interpretation = card.finance
                    elif context_type == "career":
                        interpretation = card.education_career_business
                    elif context_type == "health":
                        interpretation = card.health

                    if interpretation:
                        context += f"   해석: {interpretation[:150]}...\n"

                context += "\n"

        if question:
            context += f"\n질문: {question}\n"

        if context_type:
            context += f"상담 유형: {context_type}\n"

        return context

    def get_statistics(self) -> Dict[str, Any]:
        """Get statistics about loaded cards"""
        stats = {
            "total_cards": len(self.cards_data),
            "major_arcana": len(self.get_cards_by_suit(CardSuit.MAJOR_ARCANA)),
            "wands": len(self.get_cards_by_suit(CardSuit.WANDS)),
            "cups": len(self.get_cards_by_suit(CardSuit.CUPS)),
            "swords": len(self.get_cards_by_suit(CardSuit.SWORDS)),
            "pentacles": len(self.get_cards_by_suit(CardSuit.PENTACLES))
        }
        return stats

    def reload_data(self):
        """Reload tarot data from files"""
        self._load_data()


# Singleton instance
rag_service = RAGService()
