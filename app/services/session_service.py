"""
Session Service
Manages user sessions and interaction tracking
"""

from typing import Optional, Dict
from datetime import datetime, timedelta
import uuid
from app.models.user_session import (
    UserSession,
    SessionStatus,
    SessionCreate,
    SessionUpdate,
    SessionResponse
)
from app.config import settings


class SessionService:
    """Service for managing user sessions"""

    def __init__(self):
        """Initialize session service"""
        # In-memory storage (replace with database in production)
        self.sessions: Dict[str, UserSession] = {}
        self.user_sessions: Dict[str, list] = {}  # user_id -> [session_ids]

    async def create_session(self, user_id: str) -> UserSession:
        """
        Create a new session for user

        Args:
            user_id: User identifier

        Returns:
            Created session
        """
        session_id = f"session_{uuid.uuid4().hex}"

        # Calculate total interactions from previous sessions
        total_interactions = self._get_user_total_interactions(user_id)

        # Create session
        session = UserSession(
            session_id=session_id,
            user_id=user_id,
            created_at=datetime.now(),
            last_active=datetime.now(),
            expires_at=datetime.now() + timedelta(hours=settings.SESSION_EXPIRY_HOURS),
            status=SessionStatus.ACTIVE,
            interaction_count=0,
            total_interactions=total_interactions
        )

        # Store session
        self.sessions[session_id] = session

        # Track user's sessions
        if user_id not in self.user_sessions:
            self.user_sessions[user_id] = []
        self.user_sessions[user_id].append(session_id)

        return session

    async def get_session(self, session_id: str) -> Optional[UserSession]:
        """
        Get session by ID

        Args:
            session_id: Session identifier

        Returns:
            Session if found and active, None otherwise
        """
        session = self.sessions.get(session_id)

        if not session:
            return None

        # Check if expired
        if datetime.now() > session.expires_at:
            session.status = SessionStatus.EXPIRED
            return None

        return session

    async def get_or_create_session(self, user_id: str) -> UserSession:
        """
        Get active session or create new one

        Args:
            user_id: User identifier

        Returns:
            Active session
        """
        # Look for active session
        if user_id in self.user_sessions:
            for session_id in reversed(self.user_sessions[user_id]):
                session = await self.get_session(session_id)
                if session and session.status == SessionStatus.ACTIVE:
                    return session

        # Create new session
        return await self.create_session(user_id)

    async def update_session(
        self,
        session_id: str,
        update: SessionUpdate
    ) -> Optional[UserSession]:
        """
        Update session

        Args:
            session_id: Session identifier
            update: Update data

        Returns:
            Updated session
        """
        session = await self.get_session(session_id)
        if not session:
            return None

        # Update fields
        if update.interaction_count is not None:
            session.interaction_count = update.interaction_count

        if update.preferred_tarot_master is not None:
            session.preferred_tarot_master = update.preferred_tarot_master

        if update.preferred_llm_provider is not None:
            session.preferred_llm_provider = update.preferred_llm_provider

        if update.user_preferences is not None:
            session.user_preferences.update(update.user_preferences)

        session.last_active = datetime.now()

        return session

    async def update_interaction(self, session_id: str) -> Optional[UserSession]:
        """
        Increment interaction count

        Args:
            session_id: Session identifier

        Returns:
            Updated session
        """
        session = await self.get_session(session_id)
        if not session:
            return None

        session.interaction_count += 1
        session.total_interactions += 1
        session.last_active = datetime.now()

        return session

    async def close_session(self, session_id: str) -> bool:
        """
        Close a session

        Args:
            session_id: Session identifier

        Returns:
            True if closed successfully
        """
        session = self.sessions.get(session_id)
        if session:
            session.status = SessionStatus.CLOSED
            return True
        return False

    async def get_session_response(self, user_id: str) -> SessionResponse:
        """
        Get session with relationship context

        Args:
            user_id: User identifier

        Returns:
            Session response with context
        """
        session = await self.get_or_create_session(user_id)

        # Determine if returning user
        is_returning = session.total_interactions > 0

        # Build relationship context
        context = self._build_relationship_context(session.total_interactions)

        return SessionResponse(
            session=session,
            is_returning_user=is_returning,
            relationship_context=context
        )

    def _get_user_total_interactions(self, user_id: str) -> int:
        """Get total interactions for user across all sessions"""
        if user_id not in self.user_sessions:
            return 0

        total = 0
        for session_id in self.user_sessions[user_id]:
            session = self.sessions.get(session_id)
            if session:
                total += session.interaction_count

        return total

    def _build_relationship_context(self, total_interactions: int) -> str:
        """Build relationship context based on interaction count"""
        if total_interactions == 0:
            return "첫 만남입니다. 환영합니다."
        elif total_interactions < 5:
            return f"이번이 {total_interactions + 1}번째 만남입니다. 당신과의 인연이 시작되고 있습니다."
        elif total_interactions < 10:
            return f"{total_interactions + 1}번째 만남입니다. 우리의 유대가 깊어지고 있습니다."
        elif total_interactions < 20:
            return f"벌써 {total_interactions + 1}번째 만남이네요. 당신의 여정을 함께하게 되어 영광입니다."
        else:
            return f"{total_interactions + 1}번째 만남... 우리는 이제 오랜 친구입니다."

    async def get_user_history(self, user_id: str) -> list:
        """Get all sessions for a user"""
        if user_id not in self.user_sessions:
            return []

        sessions = []
        for session_id in self.user_sessions[user_id]:
            session = self.sessions.get(session_id)
            if session:
                sessions.append(session)

        return sessions


# Singleton instance
session_service = SessionService()
