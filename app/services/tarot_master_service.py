"""
Tarot Master Service
Manages tarot master personas and reading generation with optimized prompt system
"""

from typing import List, Optional, Dict
import random
from datetime import datetime
from app.models.tarot_card import DrawnCard, TarotCard, CardOrientation
from app.models.reading import ReadingRequest, ReadingResponse, SpreadType
from app.core.personas.tarot_master_1 import TarotMaster1
from app.core.personas.tarot_master_2 import TarotMaster2
from app.core.personas.tarot_master_3 import TarotMaster3
from app.core.personas.prompt_manager import (
    TarotMasterPrompts,
    PromptLevel,
    get_master_prompt,
    assess_question
)
from app.services.llm_service import llm_service
from app.services.rag_service import rag_service
from app.services.session_service import session_service
from app.config import TAROT_MASTERS
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

    def draw_cards(
        self,
        spread_type: SpreadType,
        master_id: Optional[str] = None
    ) -> List[DrawnCard]:
        """
        Draw cards for a reading (Phase 9: 역방향 설정 적용)

        Args:
            spread_type: Type of spread
            master_id: Tarot master ID (e.g., "master_1", "master_2", "master_3")

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

        # Phase 9: Check if this tarot master interprets reversed cards
        interpret_reversed = True  # Default
        if master_id and master_id in TAROT_MASTERS:
            interpret_reversed = TAROT_MASTERS[master_id].get("interpret_reversed", True)

        # Assign orientations and positions
        drawn_cards = []
        positions = self._get_positions_for_spread(spread_type)

        for i, card in enumerate(selected_cards):
            # Phase 9: Only allow reversed cards if master supports it
            if interpret_reversed:
                # Master supports reversed interpretation
                orientation = random.choice([CardOrientation.UPRIGHT, CardOrientation.REVERSED])
            else:
                # Master only uses upright (positive) interpretation
                orientation = CardOrientation.UPRIGHT

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

    async def generate_reading(
        self,
        request: ReadingRequest,
        use_optimized_prompts: bool = True
    ) -> ReadingResponse:
        """
        Generate a complete tarot reading with optimized prompt system

        Args:
            request: Reading request
            use_optimized_prompts: Use new 2-stage prompt system (default: True)

        Returns:
            Complete reading response with prompt metadata
        """
        # Get or create session
        session = await session_service.get_or_create_session(request.user_id)

        # Get persona
        persona_id = request.tarot_master_id or session.preferred_tarot_master or self.default_persona_id
        persona = self.get_persona(persona_id)

        # Map persona_id to master_id (Phase 9)
        master_id = f"master_{persona_id}"

        # Draw cards (Phase 9: Pass master_id for reversed card settings)
        drawn_cards = self.draw_cards(request.spread_type, master_id=master_id)

        # Get card context from RAG
        card_ids = [dc.card.id for dc in drawn_cards]
        card_context = rag_service.get_context_for_reading(card_ids, request.question)

        # Determine LLM provider
        llm_provider = request.llm_provider or session.preferred_llm_provider or "claude"

        # Generate system prompt using new prompt manager
        if use_optimized_prompts:
            system_prompt, prompt_level, tokens = self._get_optimized_prompt(
                persona_id=persona_id,
                session=session,
                request=request,
                drawn_cards=drawn_cards,
                card_context=card_context
            )
        else:
            # Fallback to old system
            system_prompt = persona.get_system_prompt(session.interaction_count)
            prompt_level = PromptLevel.SHORT
            tokens = TarotMasterPrompts.estimate_tokens(system_prompt)

        # Build reading prompt
        reading_prompt = self._build_reading_prompt(
            drawn_cards,
            request.question,
            request.spread_type,
            session.interaction_count,
            card_context
        )

        # Generate interpretation using LLM
        interpretation = await llm_service.generate_with_context(
            prompt=reading_prompt,
            context=card_context,
            system_prompt=system_prompt,
            provider_name=llm_provider
        )

        # Update session
        await session_service.increment_interaction(session.session_id)

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

        # Add prompt metadata if available
        if hasattr(reading_response, 'metadata'):
            reading_response.metadata = {
                "prompt_level": prompt_level.value if isinstance(prompt_level, PromptLevel) else prompt_level,
                "prompt_tokens": tokens,
                "optimized_prompts": use_optimized_prompts
            }

        return reading_response

    def _get_optimized_prompt(
        self,
        persona_id: int,
        session,
        request: ReadingRequest,
        drawn_cards: List[DrawnCard],
        card_context: str
    ) -> tuple[str, PromptLevel, int]:
        """
        Get optimized system prompt using 2-stage prompt system

        Args:
            persona_id: Tarot master persona ID
            session: User session
            request: Reading request
            drawn_cards: Drawn cards
            card_context: RAG context

        Returns:
            (system_prompt, prompt_level, estimated_tokens) tuple
        """
        # Map persona ID to master_id
        master_id = f"master_{persona_id}"

        # Assess question complexity
        question = request.question or "타로 리딩을 해주세요"
        analysis = assess_question(question, drawn_cards)

        # Determine if first message
        is_first_message = (session.interaction_count == 0)

        # Get user name from session
        user_name = getattr(session, 'user_name', None) or "내담자"

        # Determine prompt level
        prompt_level = TarotMasterPrompts.should_use_detailed(
            is_first_message=is_first_message,
            message_count=session.interaction_count,
            complexity=analysis["complexity"],
            card_count=analysis["card_count"],
            has_specific_context=analysis["has_specific_context"]
        )

        # Prepare context for prompt
        persona = self.get_persona(persona_id)
        context = {
            "meeting_count": session.interaction_count + 1,
            "user_name": user_name,
            "interpret_reversed": getattr(persona, 'supports_reversed', True)
        }

        # Get prompt
        system_prompt = TarotMasterPrompts.get_prompt(
            master_id=master_id,
            level=prompt_level,
            context=context
        )

        # Estimate tokens
        tokens = TarotMasterPrompts.estimate_tokens(system_prompt)

        return system_prompt, prompt_level, tokens

    def _build_reading_prompt(
        self,
        cards: List[DrawnCard],
        question: Optional[str],
        spread_type: SpreadType,
        interaction_count: int,
        card_context: Optional[str] = None
    ) -> str:
        """Build prompt for reading interpretation"""
        prompt = f"Tarot Reading - {spread_type.value.replace('_', ' ').title()}\n\n"

        if question:
            prompt += f"Question: {question}\n\n"

        prompt += "Cards drawn:\n"
        for card in cards:
            position_str = f" ({card.position})" if card.position else ""
            prompt += f"- {card.card.name} ({card.card.name_ko}){position_str} - {card.orientation.value}\n"

        if card_context:
            prompt += f"\n\nCard Meanings (RAG Context):\n{card_context}\n"

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
