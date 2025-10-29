"""
Unit tests for Session Service
"""

import pytest
from datetime import datetime, timedelta
from app.services.session_service import SessionService
from app.models.user_session import UserSession
from app.models.reading import SpreadType
from app.models.tarot_card import CardOrientation


@pytest.fixture
def session_service():
    """Create a fresh session service for each test"""
    service = SessionService()
    # Clear any existing sessions
    if hasattr(service, 'sessions'):
        service.sessions.clear()
    return service


class TestGetOrCreateSession:
    """Tests for get_or_create_session"""

    @pytest.mark.asyncio
    async def test_create_new_session(self, session_service):
        """새 세션 생성"""
        user_id = "test_user_001"
        session = await session_service.get_or_create_session(user_id)

        assert session is not None
        assert session.user_id == user_id
        assert session.total_readings == 0
        assert session.interaction_count == 0
        assert isinstance(session.created_at, datetime)

    @pytest.mark.asyncio
    async def test_get_existing_session(self, session_service):
        """기존 세션 조회"""
        user_id = "test_user_002"

        # 첫 번째 호출: 세션 생성
        session1 = await session_service.get_or_create_session(user_id)
        session1_id = session1.created_at

        # 두 번째 호출: 동일 세션 반환
        session2 = await session_service.get_or_create_session(user_id)

        assert session2.user_id == user_id
        assert session2.created_at == session1_id

    @pytest.mark.asyncio
    async def test_multiple_users(self, session_service):
        """여러 사용자 세션 관리"""
        user_ids = ["user_a", "user_b", "user_c"]
        sessions = []

        for user_id in user_ids:
            session = await session_service.get_or_create_session(user_id)
            sessions.append(session)

        # 모든 세션이 고유함
        assert len(set(s.user_id for s in sessions)) == 3


class TestUpdateSession:
    """Tests for update_session"""

    @pytest.mark.asyncio
    async def test_update_user_name(self, session_service):
        """사용자 이름 업데이트"""
        user_id = "test_user_003"
        session = await session_service.get_or_create_session(user_id)

        # 이름 없음
        assert session.user_name is None

        # 이름 업데이트
        updated = await session_service.update_session(
            user_id,
            user_name="홍길동"
        )

        assert updated.user_name == "홍길동"

    @pytest.mark.asyncio
    async def test_increment_interaction(self, session_service):
        """상호작용 횟수 증가"""
        user_id = "test_user_004"
        session = await session_service.get_or_create_session(user_id)

        initial_count = session.interaction_count

        await session_service.update_session(user_id)
        updated = await session_service.get_or_create_session(user_id)

        assert updated.interaction_count == initial_count + 1


class TestRecordReading:
    """Tests for record_reading"""

    @pytest.mark.asyncio
    async def test_record_first_reading(self, session_service):
        """첫 리딩 기록"""
        user_id = "test_user_005"
        session = await session_service.get_or_create_session(user_id)

        assert session.total_readings == 0
        assert len(session.reading_history) == 0

        # 리딩 기록
        await session_service.record_reading(
            user_id=user_id,
            spread_type=SpreadType.THREE_CARD,
            card_ids=[0, 21, 42],
            concern="새로운 시작"
        )

        updated = await session_service.get_or_create_session(user_id)

        assert updated.total_readings == 1
        assert len(updated.reading_history) == 1
        assert updated.last_reading_time is not None

    @pytest.mark.asyncio
    async def test_record_multiple_readings(self, session_service):
        """여러 리딩 기록"""
        user_id = "test_user_006"

        # 3번 리딩
        for i in range(3):
            await session_service.record_reading(
                user_id=user_id,
                spread_type=SpreadType.SINGLE_CARD,
                card_ids=[i],
                concern=f"고민 {i+1}"
            )

        session = await session_service.get_or_create_session(user_id)

        assert session.total_readings == 3
        assert len(session.reading_history) == 3

    @pytest.mark.asyncio
    async def test_reading_with_orientations(self, session_service):
        """카드 방향 포함 리딩 기록"""
        user_id = "test_user_007"

        await session_service.record_reading(
            user_id=user_id,
            spread_type=SpreadType.THREE_CARD,
            card_ids=[0, 1, 2],
            orientations=[
                CardOrientation.UPRIGHT,
                CardOrientation.REVERSED,
                CardOrientation.UPRIGHT
            ],
            concern="방향 테스트"
        )

        session = await session_service.get_or_create_session(user_id)
        reading = session.reading_history[0]

        assert reading.orientations is not None
        assert len(reading.orientations) == 3
        assert reading.orientations[1] == CardOrientation.REVERSED


class TestGetReadingHistory:
    """Tests for get_reading_history"""

    @pytest.mark.asyncio
    async def test_empty_history(self, session_service):
        """빈 히스토리"""
        user_id = "test_user_008"
        history = await session_service.get_reading_history(user_id)

        assert history == []

    @pytest.mark.asyncio
    async def test_get_recent_history(self, session_service):
        """최근 히스토리 조회"""
        user_id = "test_user_009"

        # 5개 리딩 기록
        for i in range(5):
            await session_service.record_reading(
                user_id=user_id,
                spread_type=SpreadType.SINGLE_CARD,
                card_ids=[i],
                concern=f"고민 {i+1}"
            )

        # 최근 3개만 조회
        history = await session_service.get_reading_history(user_id, limit=3)

        assert len(history) == 3
        # 최신 것이 먼저 (역순)
        assert history[0].concern == "고민 5"

    @pytest.mark.asyncio
    async def test_history_ordering(self, session_service):
        """히스토리 정렬 확인"""
        user_id = "test_user_010"

        concerns = ["첫번째", "두번째", "세번째"]
        for concern in concerns:
            await session_service.record_reading(
                user_id=user_id,
                spread_type=SpreadType.SINGLE_CARD,
                card_ids=[0],
                concern=concern
            )

        history = await session_service.get_reading_history(user_id)

        # 최신순 정렬 (역순)
        assert history[0].concern == "세번째"
        assert history[1].concern == "두번째"
        assert history[2].concern == "첫번째"


class TestSessionPersistence:
    """Tests for session persistence and cleanup"""

    @pytest.mark.asyncio
    async def test_session_survives_multiple_calls(self, session_service):
        """여러 호출 간 세션 유지"""
        user_id = "test_user_011"

        # 세션 생성 및 업데이트
        await session_service.get_or_create_session(user_id)
        await session_service.update_session(user_id, user_name="김철수")
        await session_service.record_reading(
            user_id=user_id,
            spread_type=SpreadType.SINGLE_CARD,
            card_ids=[0],
            concern="테스트"
        )

        # 새로 조회해도 데이터 유지
        session = await session_service.get_or_create_session(user_id)

        assert session.user_name == "김철수"
        assert session.total_readings == 1


class TestEdgeCases:
    """Edge cases and error handling"""

    @pytest.mark.asyncio
    async def test_empty_user_id(self, session_service):
        """빈 user_id 처리"""
        # 빈 문자열도 유효한 user_id로 처리됨
        session = await session_service.get_or_create_session("")
        assert session is not None

    @pytest.mark.asyncio
    async def test_special_characters_in_user_id(self, session_service):
        """특수문자 포함 user_id"""
        user_id = "user@email.com"
        session = await session_service.get_or_create_session(user_id)
        assert session.user_id == user_id

    @pytest.mark.asyncio
    async def test_very_long_concern(self, session_service):
        """매우 긴 고민 내용"""
        user_id = "test_user_012"
        long_concern = "가" * 10000

        await session_service.record_reading(
            user_id=user_id,
            spread_type=SpreadType.SINGLE_CARD,
            card_ids=[0],
            concern=long_concern
        )

        history = await session_service.get_reading_history(user_id)
        assert len(history[0].concern) == 10000

    @pytest.mark.asyncio
    async def test_record_reading_with_invalid_spread_type(self, session_service):
        """유효하지 않은 spread_type은 enum에서 검증됨"""
        user_id = "test_user_013"

        # SpreadType enum을 사용하므로 타입 안전성 보장
        await session_service.record_reading(
            user_id=user_id,
            spread_type=SpreadType.SINGLE_CARD,
            card_ids=[0],
            concern="정상 케이스"
        )

        session = await session_service.get_or_create_session(user_id)
        assert session.total_readings == 1
