"""
Unwoldam Tarot API - Performance Testing with Locust
Phase 12: 프로덕션 배포

Usage:
    # Web UI
    locust -f tests/performance/locustfile.py

    # Headless mode
    locust -f tests/performance/locustfile.py --headless -u 100 -r 10 --run-time 5m

    # Specific host
    locust -f tests/performance/locustfile.py --host http://localhost:8000
"""

from locust import HttpUser, task, between
import random
import json


class TarotAPIUser(HttpUser):
    """
    타로 API 사용자 시뮬레이션

    시나리오:
    1. Health check (10%)
    2. 마스터 목록 조회 (20%)
    3. 타로 리딩 요청 (50%)
    4. 세션 생성 및 조회 (20%)
    """

    # 요청 간 대기 시간 (1-5초)
    wait_time = between(1, 5)

    def on_start(self):
        """테스트 시작 시 실행"""
        self.user_id = f"perf_user_{random.randint(1, 10000)}"
        self.master_ids = ["master_1", "master_2", "master_3"]
        self.spread_types = ["single_card", "three_card", "love_triangle"]
        self.questions = [
            "What does the future hold for me?",
            "내 연애운은 어떻게 될까요?",
            "사업이 잘 될까요?",
            "Will I find success in my career?",
            "건강은 어떻게 관리해야 하나요?"
        ]

    @task(1)
    def health_check(self):
        """Health check (10% of requests)"""
        with self.client.get(
            "/health",
            catch_response=True,
            name="/health"
        ) as response:
            if response.status_code == 200:
                data = response.json()
                if data.get("status") == "healthy":
                    response.success()
                else:
                    response.failure("Health status not healthy")
            else:
                response.failure(f"Status code: {response.status_code}")

    @task(2)
    def get_tarot_masters(self):
        """타로 마스터 목록 조회 (20% of requests)"""
        with self.client.get(
            "/api/v1/tarot/masters",
            catch_response=True,
            name="/api/v1/tarot/masters"
        ) as response:
            if response.status_code == 200:
                data = response.json()
                if len(data.get("masters", [])) == 3:
                    response.success()
                else:
                    response.failure("Expected 3 masters")
            else:
                response.failure(f"Status code: {response.status_code}")

    @task(5)
    def create_tarot_reading(self):
        """타로 리딩 생성 (50% of requests)"""
        payload = {
            "user_id": self.user_id,
            "question": random.choice(self.questions),
            "spread_type": random.choice(self.spread_types),
            "llm_provider": "claude",
            "tarot_master_id": random.choice(self.master_ids),
            "draw_cards": True
        }

        with self.client.post(
            "/api/v1/tarot/reading",
            json=payload,
            catch_response=True,
            name="/api/v1/tarot/reading"
        ) as response:
            if response.status_code == 200:
                data = response.json()
                if data.get("reading_id"):
                    response.success()
                else:
                    response.failure("No reading_id in response")
            elif response.status_code == 429:
                # Rate limit - 정상적인 동작
                response.success()
            else:
                response.failure(f"Status code: {response.status_code}")

    @task(2)
    def create_and_get_session(self):
        """세션 생성 및 조회 (20% of requests)"""
        # 세션 생성
        session_payload = {
            "user_id": self.user_id,
            "user_name": f"PerfUser_{random.randint(1, 100)}",
            "tarot_master_id": random.choice(self.master_ids)
        }

        with self.client.post(
            "/api/v1/tarot/session",
            json=session_payload,
            catch_response=True,
            name="/api/v1/tarot/session [POST]"
        ) as response:
            if response.status_code == 200:
                data = response.json()
                session_id = data.get("session_id")
                if session_id:
                    response.success()

                    # 생성된 세션 조회
                    self.get_session(session_id)
                else:
                    response.failure("No session_id in response")
            else:
                response.failure(f"Status code: {response.status_code}")

    def get_session(self, session_id: str):
        """세션 조회"""
        with self.client.get(
            f"/api/v1/tarot/session/{session_id}",
            catch_response=True,
            name="/api/v1/tarot/session/{session_id} [GET]"
        ) as response:
            if response.status_code == 200:
                response.success()
            else:
                response.failure(f"Status code: {response.status_code}")


class StressTestUser(HttpUser):
    """
    스트레스 테스트 사용자

    높은 부하를 시뮬레이션하여 시스템 한계 테스트
    """

    wait_time = between(0.1, 0.5)  # 짧은 대기 시간

    def on_start(self):
        self.user_id = f"stress_user_{random.randint(1, 100000)}"

    @task
    def rapid_health_checks(self):
        """빠른 Health check 요청"""
        self.client.get("/health")

    @task
    def rapid_master_requests(self):
        """빠른 마스터 목록 요청"""
        self.client.get("/api/v1/tarot/masters")


class ReadOnlyUser(HttpUser):
    """
    읽기 전용 사용자

    실제 타로 리딩 없이 조회만 수행
    """

    wait_time = between(2, 5)

    @task(3)
    def get_masters(self):
        """마스터 목록 조회"""
        self.client.get("/api/v1/tarot/masters")

    @task(1)
    def get_spreads(self):
        """스프레드 목록 조회"""
        self.client.get("/api/v1/tarot/spreads")

    @task(1)
    def health_check(self):
        """Health check"""
        self.client.get("/health")
