"""
세션 관리 서비스 - Phase 8
Redis 기반으로 사용자별, 타로마스터별 만남 횟수 추적
"""

from typing import Optional, Dict, List
from datetime import datetime, timedelta
import json
import uuid
import logging

try:
    import redis
    REDIS_AVAILABLE = True
except ImportError:
    REDIS_AVAILABLE = False

from app.models.user_session import (
    UserSession,
    SessionStatus,
    SessionCreate,
    SessionUpdate,
    SessionResponse
)
from app.config import settings

logger = logging.getLogger(__name__)

# Log Redis availability status
if not REDIS_AVAILABLE:
    logger.warning("Redis module not installed. Using in-memory storage.")


class SessionService:
    """Redis 기반 세션 관리 서비스"""

    def __init__(self):
        """세션 서비스 초기화"""
        self.redis_client = None
        self.use_redis = REDIS_AVAILABLE

        if REDIS_AVAILABLE:
            try:
                # Redis 연결 시도 (환경변수 사용)
                redis_kwargs = {
                    'host': settings.REDIS_HOST,
                    'port': settings.REDIS_PORT,
                    'db': settings.REDIS_DB,
                    'decode_responses': True,
                    'socket_connect_timeout': 1
                }
                if settings.REDIS_PASSWORD:
                    redis_kwargs['password'] = settings.REDIS_PASSWORD

                self.redis_client = redis.Redis(**redis_kwargs)
                # 연결 테스트
                self.redis_client.ping()
                logger.info("Redis connection successful")
            except (redis.ConnectionError, redis.TimeoutError) as e:
                logger.warning(f"Could not connect to Redis server: {e}. Using in-memory storage.")
                self.use_redis = False
                self.redis_client = None

        # 메모리 기반 폴백 저장소
        if not self.use_redis:
            self.sessions: Dict[str, UserSession] = {}
            self.user_sessions: Dict[str, list] = {}
            # 타로마스터별 만남 횟수 저장
            self.master_meetings: Dict[str, Dict[str, int]] = {}

    # ========================================================================
    # Phase 8: 타로마스터별 만남 횟수 추적
    # ========================================================================

    def get_meeting_count(self, user_id: str, master_id: str) -> int:
        """
        특정 타로마스터와의 만남 횟수 조회

        Args:
            user_id: 사용자 ID
            master_id: 타로마스터 ID (master_1, master_2, master_3)

        Returns:
            만남 횟수 (정수)
        """
        if self.use_redis and self.redis_client:
            # Redis에서 조회
            key = f"user:{user_id}:master:{master_id}"
            data = self.redis_client.get(key)

            if data:
                session_data = json.loads(data)
                return session_data.get("meeting_count", 0)
            return 0
        else:
            # 메모리에서 조회
            key = f"{user_id}:{master_id}"
            if key in self.master_meetings:
                return self.master_meetings[key].get("meeting_count", 0)
            return 0

    async def increment_meeting_count(self, user_id: str, master_id: str) -> int:
        """
        특정 타로마스터와의 만남 횟수 증가

        Args:
            user_id: 사용자 ID
            master_id: 타로마스터 ID

        Returns:
            증가된 만남 횟수
        """
        now = datetime.now().isoformat()

        if self.use_redis and self.redis_client:
            # Redis 업데이트
            key = f"user:{user_id}:master:{master_id}"
            data = self.redis_client.get(key)

            if data:
                session_data = json.loads(data)
                session_data["meeting_count"] += 1
                session_data["last_met"] = now
                session_data["reading_history"] = session_data.get("reading_history", [])
            else:
                # 첫 만남
                session_data = {
                    "meeting_count": 1,
                    "first_met": now,
                    "last_met": now,
                    "reading_history": []
                }

            # Redis에 저장 (만료 시간: 90일)
            self.redis_client.setex(
                key,
                timedelta(days=90),
                json.dumps(session_data, ensure_ascii=False)
            )

            return session_data["meeting_count"]
        else:
            # 메모리 업데이트
            key = f"{user_id}:{master_id}"

            if key in self.master_meetings:
                self.master_meetings[key]["meeting_count"] += 1
                self.master_meetings[key]["last_met"] = now
            else:
                self.master_meetings[key] = {
                    "meeting_count": 1,
                    "first_met": now,
                    "last_met": now,
                    "reading_history": []
                }

            return self.master_meetings[key]["meeting_count"]

    def add_reading_to_history(self, user_id: str, master_id: str, reading_id: str):
        """
        리딩 기록 추가

        Args:
            user_id: 사용자 ID
            master_id: 타로마스터 ID
            reading_id: 리딩 ID
        """
        if self.use_redis and self.redis_client:
            key = f"user:{user_id}:master:{master_id}"
            data = self.redis_client.get(key)

            if data:
                session_data = json.loads(data)
            else:
                # 데이터가 없으면 초기화
                now = datetime.now().isoformat()
                session_data = {
                    "meeting_count": 0,
                    "first_met": now,
                    "last_met": now,
                    "reading_history": []
                }

            history = session_data.get("reading_history", [])
            history.append(reading_id)

            # 최근 100개만 유지
            if len(history) > 100:
                history = history[-100:]

            session_data["reading_history"] = history

            self.redis_client.setex(
                key,
                timedelta(days=90),
                json.dumps(session_data, ensure_ascii=False)
            )
        else:
            key = f"{user_id}:{master_id}"
            # 키가 없으면 초기화
            if key not in self.master_meetings:
                now = datetime.now().isoformat()
                self.master_meetings[key] = {
                    "meeting_count": 0,
                    "first_met": now,
                    "last_met": now,
                    "reading_history": []
                }

            history = self.master_meetings[key].get("reading_history", [])
            history.append(reading_id)

            # 최근 100개만 유지
            if len(history) > 100:
                history = history[-100:]

            self.master_meetings[key]["reading_history"] = history

    def get_relationship_level(self, meeting_count: int) -> str:
        """
        만남 횟수에 따른 관계 레벨 반환

        Args:
            meeting_count: 만남 횟수

        Returns:
            관계 레벨 문자열
            - "formal": 1회 (정중하고 격식있는)
            - "polite": 2-5회 (부드러운 존댓말)
            - "friendly": 6-10회 (친근한 존댓말)
            - "intimate": 11회 이상 (편안한 반말 혼용)
        """
        if meeting_count <= 1:
            return "formal"
        elif meeting_count <= 5:
            return "polite"
        elif meeting_count <= 10:
            return "friendly"
        else:
            return "intimate"

    def get_all_master_meetings(self, user_id: str) -> Dict[str, Dict]:
        """
        사용자의 모든 타로마스터별 만남 정보 조회

        Args:
            user_id: 사용자 ID

        Returns:
            타로마스터별 만남 정보 딕셔너리
        """
        result = {}

        master_ids = ["master_1", "master_2", "master_3"]

        for master_id in master_ids:
            if self.use_redis and self.redis_client:
                key = f"user:{user_id}:master:{master_id}"
                data = self.redis_client.get(key)

                if data:
                    result[master_id] = json.loads(data)
                else:
                    result[master_id] = {
                        "meeting_count": 0,
                        "first_met": None,
                        "last_met": None,
                        "reading_history": []
                    }
            else:
                key = f"{user_id}:{master_id}"
                if key in self.master_meetings:
                    result[master_id] = self.master_meetings[key]
                else:
                    result[master_id] = {
                        "meeting_count": 0,
                        "first_met": None,
                        "last_met": None,
                        "reading_history": []
                    }

        return result

    # ========================================================================
    # 기존 세션 관리 기능 (하위 호환성 유지)
    # ========================================================================

    async def create_session(self, user_id: str) -> UserSession:
        """
        새 세션 생성

        Args:
            user_id: 사용자 ID

        Returns:
            생성된 세션
        """
        session_id = f"session_{uuid.uuid4().hex}"

        # 전체 인터랙션 수 계산
        total_interactions = self._get_user_total_interactions(user_id)

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

        if self.use_redis and self.redis_client:
            # Redis에 저장
            key = f"session:{session_id}"
            self.redis_client.setex(
                key,
                timedelta(hours=settings.SESSION_EXPIRY_HOURS),
                json.dumps(session.dict(), default=str, ensure_ascii=False)
            )

            # 사용자 세션 목록 업데이트
            user_key = f"user:{user_id}:sessions"
            self.redis_client.rpush(user_key, session_id)
        else:
            # 메모리에 저장
            self.sessions[session_id] = session

            if user_id not in self.user_sessions:
                self.user_sessions[user_id] = []
            self.user_sessions[user_id].append(session_id)

        return session

    async def get_session(self, session_id: str) -> Optional[UserSession]:
        """
        세션 ID로 세션 조회

        Args:
            session_id: 세션 ID

        Returns:
            세션 객체 또는 None
        """
        if self.use_redis and self.redis_client:
            key = f"session:{session_id}"
            data = self.redis_client.get(key)

            if data:
                session_dict = json.loads(data)
                session = UserSession(**session_dict)

                # 만료 확인
                if datetime.now() > session.expires_at:
                    session.status = SessionStatus.EXPIRED
                    return None

                return session
            return None
        else:
            session = self.sessions.get(session_id)

            if not session:
                return None

            if datetime.now() > session.expires_at:
                session.status = SessionStatus.EXPIRED
                return None

            return session

    async def get_or_create_session(self, user_id: str) -> UserSession:
        """
        활성 세션 조회 또는 새 세션 생성

        Args:
            user_id: 사용자 ID

        Returns:
            활성 세션
        """
        if self.use_redis and self.redis_client:
            # Redis에서 사용자 세션 목록 조회
            user_key = f"user:{user_id}:sessions"
            session_ids = self.redis_client.lrange(user_key, -5, -1)  # 최근 5개

            # 역순으로 확인 (최신부터)
            for session_id in reversed(session_ids):
                session = await self.get_session(session_id)
                if session and session.status == SessionStatus.ACTIVE:
                    return session
        else:
            # 메모리에서 조회
            if user_id in self.user_sessions:
                for session_id in reversed(self.user_sessions[user_id]):
                    session = await self.get_session(session_id)
                    if session and session.status == SessionStatus.ACTIVE:
                        return session

        # 새 세션 생성
        return await self.create_session(user_id)

    async def increment_interaction(self, session_id: str) -> Optional[UserSession]:
        """
        인터랙션 카운트 증가

        Args:
            session_id: 세션 ID

        Returns:
            업데이트된 세션
        """
        session = await self.get_session(session_id)
        if not session:
            return None

        session.interaction_count += 1
        session.total_interactions += 1
        session.last_active = datetime.now()

        if self.use_redis and self.redis_client:
            key = f"session:{session_id}"
            self.redis_client.setex(
                key,
                timedelta(hours=settings.SESSION_EXPIRY_HOURS),
                json.dumps(session.dict(), default=str, ensure_ascii=False)
            )
        else:
            self.sessions[session_id] = session

        return session

    async def update_session(
        self,
        session_id: str,
        update: SessionUpdate
    ) -> Optional[UserSession]:
        """
        세션 업데이트

        Args:
            session_id: 세션 ID
            update: 업데이트 데이터

        Returns:
            업데이트된 세션
        """
        session = await self.get_session(session_id)
        if not session:
            return None

        if update.interaction_count is not None:
            session.interaction_count = update.interaction_count

        if update.preferred_tarot_master is not None:
            session.preferred_tarot_master = update.preferred_tarot_master

        if update.preferred_llm_provider is not None:
            session.preferred_llm_provider = update.preferred_llm_provider

        if update.user_preferences is not None:
            session.user_preferences.update(update.user_preferences)

        session.last_active = datetime.now()

        if self.use_redis and self.redis_client:
            key = f"session:{session_id}"
            self.redis_client.setex(
                key,
                timedelta(hours=settings.SESSION_EXPIRY_HOURS),
                json.dumps(session.dict(), default=str, ensure_ascii=False)
            )
        else:
            self.sessions[session_id] = session

        return session

    async def close_session(self, session_id: str) -> bool:
        """
        세션 종료

        Args:
            session_id: 세션 ID

        Returns:
            성공 여부
        """
        session = await self.get_session(session_id)
        if session:
            session.status = SessionStatus.CLOSED

            if self.use_redis and self.redis_client:
                key = f"session:{session_id}"
                self.redis_client.setex(
                    key,
                    timedelta(hours=1),  # 1시간 후 삭제
                    json.dumps(session.dict(), default=str, ensure_ascii=False)
                )
            else:
                self.sessions[session_id] = session

            return True
        return False

    async def get_session_response(self, user_id: str) -> SessionResponse:
        """
        관계 컨텍스트가 포함된 세션 응답

        Args:
            user_id: 사용자 ID

        Returns:
            세션 응답
        """
        session = await self.get_or_create_session(user_id)

        is_returning = session.total_interactions > 0

        context = self._build_relationship_context(session.total_interactions)

        return SessionResponse(
            session=session,
            is_returning_user=is_returning,
            relationship_context=context
        )

    def _get_user_total_interactions(self, user_id: str) -> int:
        """모든 세션의 총 인터랙션 수 계산"""
        if self.use_redis and self.redis_client:
            user_key = f"user:{user_id}:sessions"
            session_ids = self.redis_client.lrange(user_key, 0, -1)

            total = 0
            for session_id in session_ids:
                key = f"session:{session_id}"
                data = self.redis_client.get(key)
                if data:
                    session_dict = json.loads(data)
                    total += session_dict.get("interaction_count", 0)

            return total
        else:
            if user_id not in self.user_sessions:
                return 0

            total = 0
            for session_id in self.user_sessions[user_id]:
                session = self.sessions.get(session_id)
                if session:
                    total += session.interaction_count

            return total

    def _build_relationship_context(self, total_interactions: int) -> str:
        """인터랙션 수에 따른 관계 컨텍스트 생성"""
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
        """사용자의 모든 세션 조회"""
        if self.use_redis and self.redis_client:
            user_key = f"user:{user_id}:sessions"
            session_ids = self.redis_client.lrange(user_key, 0, -1)

            sessions = []
            for session_id in session_ids:
                session = await self.get_session(session_id)
                if session:
                    sessions.append(session)

            return sessions
        else:
            if user_id not in self.user_sessions:
                return []

            sessions = []
            for session_id in self.user_sessions[user_id]:
                session = self.sessions.get(session_id)
                if session:
                    sessions.append(session)

            return sessions


# 싱글톤 인스턴스
session_service = SessionService()
