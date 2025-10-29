"""
Pytest configuration and fixtures
"""

import pytest
import asyncio
from typing import AsyncGenerator, Generator
from fastapi.testclient import TestClient
from app.main import app
from app.services.session_service import SessionService
from app.models.user_session import UserSession


@pytest.fixture(scope="session")
def event_loop() -> Generator:
    """Create an instance of the default event loop for the test session."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture
def client() -> TestClient:
    """FastAPI test client fixture"""
    return TestClient(app)


@pytest.fixture
def mock_session() -> UserSession:
    """Mock user session for testing"""
    return UserSession(
        user_id="test_user_123",
        user_name="테스트사용자",
        total_readings=5,
        last_reading_time=None,
        interaction_count=10
    )


@pytest.fixture
async def session_service() -> AsyncGenerator[SessionService, None]:
    """Session service fixture with cleanup"""
    service = SessionService()
    yield service
    # Cleanup: clear all test sessions
    if hasattr(service, 'sessions'):
        service.sessions.clear()


@pytest.fixture
def sample_card_ids() -> list[int]:
    """Sample tarot card IDs for testing"""
    return [0, 21, 42]  # The Fool, The World, middle card


@pytest.fixture
def sample_concern() -> str:
    """Sample user concern for testing"""
    return "새로운 프로젝트를 시작하려고 합니다. 조언을 구합니다."
