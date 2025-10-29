"""
Tarot Reading API Endpoints - Phase 7
Complete implementation with optimized prompt system
"""

from fastapi import APIRouter, HTTPException, status
from typing import List, Dict, Any, Optional
from datetime import datetime
import uuid

from app.models.reading import (
    ReadingRequest,
    ReadingResponse,
    TarotMasterInfo,
    SessionRequest,
    SessionResponse,
    CardInput,
    SpreadType
)
from app.models.tarot_card import DrawnCard, CardOrientation, TarotCard
from app.services.tarot_master_service import tarot_master_service
from app.services.session_service import session_service
from app.services.rag_service import rag_service
from app.services.llm_service import llm_service
from app.core.personas.prompt_manager import get_master_prompt, assess_question
from app.config import TAROT_MASTERS

router = APIRouter()


@router.post("/reading", response_model=ReadingResponse, status_code=status.HTTP_200_OK)
async def create_tarot_reading(request: ReadingRequest):
    """
    Create a new tarot reading with optimized prompt system

    This endpoint:
    - Accepts manual card selection or auto-draws cards
    - Uses 2-stage prompt system for token optimization
    - Tracks meeting count for relationship building
    - Supports all 3 tarot master personas

    Args:
        request: Tarot reading request with user info, concern, and optional cards

    Returns:
        Complete reading with interpretation and metadata

    Example:
        POST /api/v1/tarot/reading
        {
            "user_id": "user123",
            "tarot_master": "master_1",
            "concern": "새로운 일을 시작하려고 하는데 잘 될지 궁금합니다",
            "spread_type": "three_card",
            "cards": [
                {"card_id": "major_00_fool", "position": "past", "orientation": "upright"},
                {"card_id": "wands_ace", "position": "present", "orientation": "upright"},
                {"card_id": "cups_02", "position": "future", "orientation": "reversed"}
            ],
            "settings": {"interpret_reversed": true}
        }
    """
    try:
        # 1. Validate tarot master
        if request.tarot_master not in TAROT_MASTERS:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid tarot_master. Must be one of: {list(TAROT_MASTERS.keys())}"
            )

        # 2. Get or create session
        session = await session_service.get_or_create_session(request.user_id)

        # 3. Get meeting count for this specific tarot master (Phase 8)
        master_id = request.tarot_master
        meeting_count = session_service.get_meeting_count(request.user_id, master_id)

        # 4. Process cards (manual selection or auto-draw)
        if request.cards:
            # Manual card selection (Phase 9: Pass master_id for reversed settings)
            drawn_cards = await _process_manual_cards(request.cards, request.spread_type, master_id=master_id)
        else:
            # Auto-draw cards (Phase 9: Pass master_id for reversed settings)
            drawn_cards = tarot_master_service.draw_cards(request.spread_type, master_id=master_id)

        # 5. Get card context from RAG
        card_ids = [dc.card.id for dc in drawn_cards]
        concern = request.concern or "타로 리딩을 해주세요"

        # Assess question complexity
        analysis = assess_question(concern, drawn_cards)

        # Get RAG context
        card_context = rag_service.get_context_for_reading(
            card_ids,
            concern,
            context_type=analysis.get("context_type"),
            use_vector_search=True
        )

        # 6. Generate optimized prompt
        is_first_message = (meeting_count == 0)
        user_name = getattr(session, 'user_name', None) or "내담자"

        system_prompt, prompt_level = get_master_prompt(
            master_id=master_id,
            meeting_count=meeting_count + 1,  # Next meeting
            user_name=user_name,
            is_first_message=is_first_message,
            complexity=analysis["complexity"],
            card_count=len(drawn_cards),
            interpret_reversed=request.settings.interpret_reversed if request.settings else True
        )

        # 7. Build user message
        user_message = _build_user_message(
            concern=concern,
            cards=drawn_cards,
            spread_type=request.spread_type,
            card_context=card_context
        )

        # 8. Get LLM provider from config
        master_config = TAROT_MASTERS[master_id]
        llm_provider = master_config["llm_provider"]

        # 9. Generate interpretation
        interpretation = await llm_service.generate_response(
            prompt=user_message,
            system_prompt=system_prompt,
            provider_name=llm_provider,
            temperature=0.7,
            max_tokens=2000
        )

        # 10. Update session (Phase 8: Track per-master meeting count)
        await session_service.increment_interaction(session.session_id)
        await session_service.increment_meeting_count(request.user_id, master_id)

        # 11. Build response
        reading_id = f"reading_{uuid.uuid4().hex[:12]}"

        # 12. Add reading to history (Phase 8)
        session_service.add_reading_to_history(request.user_id, master_id, reading_id)

        tarot_master_info = TarotMasterInfo(
            id=master_id,
            name=master_config["name"],
            name_en=master_config["name_en"],
            meeting_count=meeting_count + 1
        )

        metadata = {
            "prompt_level": prompt_level.value,
            "llm_provider": llm_provider,
            "complexity": analysis["complexity"],
            "context_type": analysis.get("context_type"),
            "auto_drawn": request.cards is None
        }

        response = ReadingResponse(
            reading_id=reading_id,
            tarot_master=tarot_master_info,
            interpretation=interpretation,
            cards_analyzed=drawn_cards,
            timestamp=datetime.now(),
            metadata=metadata
        )

        return response

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to generate reading: {str(e)}"
        )


@router.get("/masters", response_model=List[Dict[str, Any]])
async def list_tarot_masters():
    """
    Get list of available tarot masters

    Returns information about all 3 tarot master personas:
    - 달빛의 현자 (Sage of Moonlight)
    - 별빛의 안내자 (Starlight Guide)
    - 운명의 해석자 (Destiny Interpreter)

    Returns:
        List of tarot master configurations

    Example:
        GET /api/v1/tarot/masters
    """
    masters_list = []

    for master_id, config in TAROT_MASTERS.items():
        masters_list.append({
            "id": master_id,
            "name": config["name"],
            "name_en": config["name_en"],
            "description": config["description"],
            "style": config["style"],
            "recommended_llm": config["llm_provider"],
            "supports_reversed": config["interpret_reversed"]
        })

    return masters_list


@router.post("/session", response_model=SessionResponse, status_code=status.HTTP_201_CREATED)
async def create_session(request: SessionRequest):
    """
    Create or get user session for tracking meetings

    Sessions track:
    - Meeting count per tarot master
    - User preferences (name, preferred master)
    - Total interactions

    Args:
        request: Session creation request with user_id and optional preferences

    Returns:
        Session information with meeting counts

    Example:
        POST /api/v1/tarot/session
        {
            "user_id": "user123",
            "tarot_master": "master_1",
            "user_name": "민수"
        }
    """
    try:
        # Get or create session
        session = await session_service.get_or_create_session(request.user_id)

        # Update user preferences if provided
        if request.user_name:
            session.user_name = request.user_name
        if request.tarot_master:
            session.preferred_tarot_master = request.tarot_master

        # Build meeting count dict (Phase 8: Use session service)
        tarot_master_meetings = {
            "master_1": session_service.get_meeting_count(request.user_id, "master_1"),
            "master_2": session_service.get_meeting_count(request.user_id, "master_2"),
            "master_3": session_service.get_meeting_count(request.user_id, "master_3")
        }

        response = SessionResponse(
            session_id=session.session_id,
            user_id=session.user_id,
            user_name=getattr(session, 'user_name', None),
            tarot_master_meetings=tarot_master_meetings,
            total_interactions=session.interaction_count,
            created_at=session.created_at,
            last_interaction=getattr(session, 'last_interaction', None)
        )

        return response

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create/get session: {str(e)}"
        )


@router.get("/session/{user_id}", response_model=SessionResponse)
async def get_session(user_id: str):
    """
    Get existing session information

    Args:
        user_id: User identifier

    Returns:
        Session information

    Example:
        GET /api/v1/tarot/session/user123
    """
    try:
        session = await session_service.get_session(user_id)

        if not session:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Session not found for user: {user_id}"
            )

        # Get meeting counts (Phase 8: Use session service)
        tarot_master_meetings = {
            "master_1": session_service.get_meeting_count(user_id, "master_1"),
            "master_2": session_service.get_meeting_count(user_id, "master_2"),
            "master_3": session_service.get_meeting_count(user_id, "master_3")
        }

        response = SessionResponse(
            session_id=session.session_id,
            user_id=session.user_id,
            user_name=getattr(session, 'user_name', None),
            tarot_master_meetings=tarot_master_meetings,
            total_interactions=session.interaction_count,
            created_at=session.created_at,
            last_interaction=getattr(session, 'last_interaction', None)
        )

        return response

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get session: {str(e)}"
        )


@router.get("/spreads", response_model=Dict[str, Dict[str, Any]])
async def list_spread_types():
    """
    List available tarot spread types

    Returns:
        Dictionary of spread types with descriptions

    Example:
        GET /api/v1/tarot/spreads
    """
    spreads = {
        "one_card": {
            "name": "One Card",
            "name_ko": "원카드",
            "description": "Simple one-card reading for quick insight",
            "description_ko": "빠른 통찰을 위한 간단한 한 장 리딩",
            "cards": 1,
            "positions": ["present"]
        },
        "three_card": {
            "name": "Three Card Spread",
            "name_ko": "쓰리카드",
            "description": "Past, Present, Future reading",
            "description_ko": "과거, 현재, 미래 리딩",
            "cards": 3,
            "positions": ["past", "present", "future"]
        },
        "celtic_cross": {
            "name": "Celtic Cross",
            "name_ko": "켈틱 크로스",
            "description": "Comprehensive 10-card reading",
            "description_ko": "종합적인 10장 카드 리딩",
            "cards": 10,
            "positions": [
                "present", "challenge", "past", "future",
                "above", "below", "advice", "external",
                "hopes_fears", "outcome"
            ]
        },
        "relationship": {
            "name": "Relationship Spread",
            "name_ko": "관계 스프레드",
            "description": "5-card reading focused on relationships",
            "description_ko": "관계에 초점을 맞춘 5장 카드 리딩",
            "cards": 5,
            "positions": ["you", "partner", "relationship", "challenge", "outcome"]
        },
        "career": {
            "name": "Career Spread",
            "name_ko": "커리어 스프레드",
            "description": "5-card reading focused on career and work",
            "description_ko": "커리어와 일에 초점을 맞춘 5장 카드 리딩",
            "cards": 5,
            "positions": ["current", "challenge", "strength", "action", "outcome"]
        }
    }

    return spreads


# Helper functions

async def _process_manual_cards(
    card_inputs: List[CardInput],
    spread_type: SpreadType,
    master_id: Optional[str] = None
) -> List[DrawnCard]:
    """
    Process manually selected cards into DrawnCard objects
    Phase 9: Respect master's interpret_reversed setting
    """
    drawn_cards = []

    # Phase 9: Check if this tarot master interprets reversed cards
    interpret_reversed = True  # Default
    if master_id and master_id in TAROT_MASTERS:
        interpret_reversed = TAROT_MASTERS[master_id].get("interpret_reversed", True)

    # Get all available cards
    all_cards = rag_service.get_all_cards()
    card_map = {card.card: card for card in all_cards}

    for card_input in card_inputs:
        # Find card by ID
        card = card_map.get(card_input.card_id)

        if not card:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid card_id: {card_input.card_id}"
            )

        # Parse orientation
        try:
            orientation = CardOrientation(card_input.orientation.lower())
        except ValueError:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid orientation: {card_input.orientation}. Must be 'upright' or 'reversed'"
            )

        # Phase 9: Force upright if master doesn't interpret reversed
        if not interpret_reversed and orientation == CardOrientation.REVERSED:
            orientation = CardOrientation.UPRIGHT

        drawn_cards.append(DrawnCard(
            card=card,
            orientation=orientation,
            position=card_input.position
        ))

    return drawn_cards


def _build_user_message(
    concern: str,
    cards: List[DrawnCard],
    spread_type: SpreadType,
    card_context: str
) -> str:
    """Build formatted user message for LLM"""
    message = f"""【타로 리딩 요청】

**상담자의 고민:**
{concern}

**스프레드 타입:** {spread_type.value}

**뽑은 카드:**
"""

    for card in cards:
        position_str = f" ({card.position})" if card.position else ""
        message += f"- {card.card.name} ({card.card.name_ko}){position_str} - {card.orientation.value}\n"

    message += f"""
**카드 의미 (RAG 컨텍스트):**
{card_context}

위 정보를 바탕으로 타로 리딩을 해주세요.
"""

    return message
