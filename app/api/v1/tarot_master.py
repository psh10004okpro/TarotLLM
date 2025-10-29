"""
Tarot Master API Endpoints
Endpoints for managing tarot master personas and sessions
"""

from fastapi import APIRouter, HTTPException, status
from typing import List
from app.models.user_session import SessionCreate, SessionResponse, UserSession
from app.services.tarot_master_service import tarot_master_service
from app.services.session_service import session_service

router = APIRouter()


@router.get("/masters")
async def list_tarot_masters():
    """
    List available tarot master personas

    Returns:
        List of tarot master personas
    """
    personas = tarot_master_service.list_personas()
    return {"personas": personas}


@router.get("/masters/{master_id}")
async def get_tarot_master(master_id: int):
    """
    Get details of a specific tarot master

    Args:
        master_id: Tarot master ID

    Returns:
        Tarot master details
    """
    try:
        persona = tarot_master_service.get_persona(master_id)
        return {
            "id": master_id,
            "name": persona.name,
            "description": persona.description,
            "style": persona.style
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Tarot master not found: {str(e)}"
        )


@router.post("/session", response_model=SessionResponse)
async def create_session(request: SessionCreate):
    """
    Create a new user session

    Args:
        request: Session creation request

    Returns:
        Created session with relationship context
    """
    try:
        session_response = await session_service.get_session_response(request.user_id)
        return session_response
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create session: {str(e)}"
        )


@router.get("/session/{session_id}", response_model=UserSession)
async def get_session(session_id: str):
    """
    Get session details

    Args:
        session_id: Session identifier

    Returns:
        Session details
    """
    session = await session_service.get_session(session_id)

    if not session:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Session not found or expired"
        )

    return session


@router.get("/session/user/{user_id}/history")
async def get_user_sessions(user_id: str):
    """
    Get all sessions for a user

    Args:
        user_id: User identifier

    Returns:
        List of user sessions
    """
    sessions = await session_service.get_user_history(user_id)
    return {"user_id": user_id, "sessions": sessions, "total": len(sessions)}


@router.delete("/session/{session_id}")
async def close_session(session_id: str):
    """
    Close a session

    Args:
        session_id: Session identifier

    Returns:
        Success status
    """
    success = await session_service.close_session(session_id)

    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Session not found"
        )

    return {"status": "closed", "session_id": session_id}
