"""
RAG (Retrieval-Augmented Generation) Service
Manages tarot card knowledge base and retrieval
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
        self.card_meanings: Dict[str, Any] = {}
        self.vector_store = None  # To be implemented with actual vector DB
        self._load_data()

    def _load_data(self):
        """Load tarot cards data from JSON files"""
        try:
            # Load tarot cards
            cards_path = Path("app/data/tarot_cards.json")
            if cards_path.exists():
                with open(cards_path, "r", encoding="utf-8") as f:
                    cards_json = json.load(f)
                    self.cards_data = [TarotCard(**card) for card in cards_json]

            # Load card meanings
            meanings_path = Path("app/data/card_meanings.json")
            if meanings_path.exists():
                with open(meanings_path, "r", encoding="utf-8") as f:
                    self.card_meanings = json.load(f)

        except Exception as e:
            print(f"Warning: Could not load tarot data: {e}")

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
            if card.name.lower() == name_lower or card.name_ko == name:
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
            context: Additional context (e.g., question type)

        Returns:
            Detailed card meaning
        """
        card = self.get_card_by_id(card_id)
        if not card:
            return "Card not found"

        # Get base meaning from card
        meaning = f"{card.name} ({card.name_ko})\n\n"
        meaning += f"Description: {card.description}\n\n"

        if orientation == "upright":
            meaning += f"Keywords: {', '.join(card.keywords_upright)}\n"
        else:
            meaning += f"Keywords (Reversed): {', '.join(card.keywords_reversed)}\n"

        # Add extended meanings if available
        if str(card_id) in self.card_meanings:
            card_detail = self.card_meanings[str(card_id)]
            meaning += f"\n{card_detail.get(orientation, {}).get('meaning', '')}"

        return meaning

    def search_cards(self, query: str) -> List[TarotCard]:
        """
        Search cards by keyword or theme

        Args:
            query: Search query

        Returns:
            List of matching cards
        """
        query_lower = query.lower()
        matching_cards = []

        for card in self.cards_data:
            # Search in name
            if query_lower in card.name.lower() or query_lower in card.name_ko:
                matching_cards.append(card)
                continue

            # Search in keywords
            if any(query_lower in keyword.lower() for keyword in card.keywords_upright):
                matching_cards.append(card)
                continue

            if any(query_lower in keyword.lower() for keyword in card.keywords_reversed):
                matching_cards.append(card)
                continue

            # Search in description
            if query_lower in card.description.lower():
                matching_cards.append(card)

        return matching_cards

    def get_context_for_reading(
        self,
        cards: List[int],
        question: Optional[str] = None
    ) -> str:
        """
        Get contextual information for a reading

        Args:
            cards: List of card IDs
            question: User's question

        Returns:
            Context string for LLM
        """
        context = "Tarot Card Context:\n\n"

        for card_id in cards:
            card = self.get_card_by_id(card_id)
            if card:
                context += f"- {card.name} ({card.name_ko}): {card.description}\n"
                context += f"  Upright: {', '.join(card.keywords_upright)}\n"
                context += f"  Reversed: {', '.join(card.keywords_reversed)}\n\n"

        if question:
            context += f"\nUser's Question: {question}\n"

        return context

    def reload_data(self):
        """Reload tarot data from files"""
        self._load_data()


# Singleton instance
rag_service = RAGService()
