"""
Tarot Master Service
Manages tarot master personas and reading generation
"""

from typing import List, Optional
import random
from datetime import datetime
from app.models.tarot_card import DrawnCard, TarotCard, CardOrientation
from app.models.reading import ReadingRequest, ReadingResponse, SpreadType
from app.core.personas.tarot_master_1 import TarotMaster1
from app.core.personas.tarot_master_2 import TarotMaster2
from app.core.personas.tarot_master_3 import TarotMaster3
from app.services.llm_service import llm_service
from app.services.rag_service import rag_service
from app.services.session_service import session_service
import uuid


class TarotMasterService:
    """Service for managing tarot readings with different personas"""

    def __init__(self):
        """Initialize tarot master service"""
        self.personas = {
            1: TarotMaster1(),
            2: TarotMaster2(),
            3: TarotMaster3()
        }
        self.default_persona_id = 1

    def get_persona(self, persona_id: Optional[int] = None):
        """Get tarot master persona by ID"""
        pid = persona_id or self.default_persona_id
        if pid not in self.personas:
            pid = self.default_persona_id
        return self.personas[pid]

    def draw_cards(self, spread_type: SpreadType) -> List[DrawnCard]:
        """
        Draw cards for a reading

        Args:
            spread_type: Type of spread

        Returns:
            List of drawn cards with orientations
        """
        # Determine number of cards based on spread type
        num_cards = {
            SpreadType.SINGLE_CARD: 1,
            SpreadType.THREE_CARD: 3,
            SpreadType.CELTIC_CROSS: 10,
            SpreadType.RELATIONSHIP: 5,
            SpreadType.CAREER: 5,
            SpreadType.CUSTOM: 3
        }.get(spread_type, 3)

        # Get all available cards
        all_cards = rag_service.get_all_cards()

        if not all_cards:
            # Return empty list if no cards loaded
            return []

        # Randomly select cards without replacement
        selected_cards = random.sample(all_cards, min(num_cards, len(all_cards)))

        # Assign orientations and positions
        drawn_cards = []
        positions = self._get_positions_for_spread(spread_type)

        for i, card in enumerate(selected_cards):
            orientation = random.choice([CardOrientation.UPRIGHT, CardOrientation.REVERSED])
            position = positions[i] if i < len(positions) else None

            drawn_cards.append(DrawnCard(
                card=card,
                orientation=orientation,
                position=position
            ))

        return drawn_cards

    def _get_positions_for_spread(self, spread_type: SpreadType) -> List[str]:
        """Get position names for spread type"""
        positions = {
            SpreadType.SINGLE_CARD: ["present"],
            SpreadType.THREE_CARD: ["past", "present", "future"],
            SpreadType.CELTIC_CROSS: [
                "present", "challenge", "past", "future",
                "above", "below", "advice", "external",
                "hopes_fears", "outcome"
            ],
            SpreadType.RELATIONSHIP: ["you", "partner", "relationship", "challenge", "outcome"],
            SpreadType.CAREER: ["current", "challenge", "strength", "action", "outcome"],
            SpreadType.CUSTOM: ["card_1", "card_2", "card_3"]
        }
        return positions.get(spread_type, [])

    async def generate_reading(self, request: ReadingRequest) -> ReadingResponse:
        """
        Generate a complete tarot reading

        Args:
            request: Reading request

        Returns:
            Complete reading response
        """
        # Get or create session
        session = await session_service.get_or_create_session(request.user_id)

        # Get persona
        persona_id = request.tarot_master_id or session.preferred_tarot_master or self.default_persona_id
        persona = self.get_persona(persona_id)

        # Draw cards
        drawn_cards = self.draw_cards(request.spread_type)

        # Get card context from RAG
        card_ids = [dc.card.id for dc in drawn_cards]
        card_context = rag_service.get_context_for_reading(card_ids, request.question)

        # Build reading prompt
        reading_prompt = self._build_reading_prompt(
            drawn_cards,
            request.question,
            request.spread_type,
            session.interaction_count
        )

        # Get system prompt from persona
        system_prompt = persona.get_system_prompt(session.interaction_count)

        # Generate interpretation using LLM
        llm_provider = request.llm_provider or session.preferred_llm_provider or "claude"

        interpretation = await llm_service.generate_with_context(
            prompt=reading_prompt,
            context=card_context,
            system_prompt=system_prompt,
            provider_name=llm_provider
        )

        # Update session
        await session_service.update_interaction(session.session_id)

        # Create response
        reading_response = ReadingResponse(
            reading_id=f"reading_{uuid.uuid4().hex[:12]}",
            user_id=request.user_id,
            timestamp=datetime.now(),
            spread_type=request.spread_type,
            cards=drawn_cards,
            interpretation=interpretation,
            summary=self._generate_summary(drawn_cards),
            llm_provider_used=llm_provider,
            tarot_master_id=persona_id
        )

        return reading_response

    def _build_reading_prompt(
        self,
        cards: List[DrawnCard],
        question: Optional[str],
        spread_type: SpreadType,
        interaction_count: int
    ) -> str:
        """Build prompt for reading interpretation"""
        prompt = f"Tarot Reading - {spread_type.value.replace('_', ' ').title()}\n\n"

        if question:
            prompt += f"Question: {question}\n\n"

        prompt += "Cards drawn:\n"
        for card in cards:
            position_str = f" ({card.position})" if card.position else ""
            prompt += f"- {card.card.name} ({card.card.name_ko}){position_str} - {card.orientation.value}\n"

        prompt += "\nProvide a detailed, insightful interpretation of this reading."

        if interaction_count > 0:
            prompt += f"\n\nNote: This is interaction #{interaction_count + 1} with this seeker."

        return prompt

    def _generate_summary(self, cards: List[DrawnCard]) -> str:
        """Generate brief summary of reading"""
        if not cards:
            return "No cards drawn"

        card_names = [f"{card.card.name}" for card in cards[:3]]
        return f"Reading with {', '.join(card_names)}"

    def list_personas(self) -> List[dict]:
        """Get list of available personas"""
        return [
            {
                "id": pid,
                "name": persona.name,
                "description": persona.description
            }
            for pid, persona in self.personas.items()
        ]


# Singleton instance
tarot_master_service = TarotMasterService()
