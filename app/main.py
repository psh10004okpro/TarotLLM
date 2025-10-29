"""
Unwoldam Tarot Card LLM API
Main FastAPI application entry point
Phase 10: 통합 및 테스트
"""

from fastapi import FastAPI, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from contextlib import asynccontextmanager
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded
from slowapi.util import get_remote_address
from app.config import settings
from app.api.v1 import tarot_reading, tarot_master
from app.services.rag_service import rag_service
from app.services.session_service import session_service
import logging

# 로깅 설정
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Rate limiter 설정
limiter = Limiter(key_func=get_remote_address)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    애플리케이션 생명주기 관리
    Phase 10: 시작/종료 시 초기화 및 정리 작업
    """
    # 시작 시
    logger.info("🚀 Unwoldam Tarot API 시작 중...")

    # RAG 시스템 초기화
    try:
        logger.info("📚 RAG 시스템 초기화 중...")
        card_count = len(rag_service.get_all_cards())
        logger.info(f"✓ {card_count}장의 타로카드 로드 완료")
    except Exception as e:
        logger.error(f"✗ RAG 시스템 초기화 실패: {str(e)}")

    # 세션 서비스 초기화
    try:
        logger.info("🔄 세션 관리 시스템 초기화 중...")
        if session_service.use_redis:
            logger.info("✓ Redis 연결 성공")
        else:
            logger.info("✓ 메모리 기반 세션 저장소 사용")
    except Exception as e:
        logger.error(f"✗ 세션 서비스 초기화 실패: {str(e)}")

    # 환경 설정 확인 및 검증
    logger.info("⚙️ 환경 설정 확인:")

    # API 키 검증
    api_keys_status = {
        "Claude (ANTHROPIC_API_KEY)": "✓" if settings.ANTHROPIC_API_KEY else "✗ Missing",
        "OpenAI (OPENAI_API_KEY)": "✓" if settings.OPENAI_API_KEY else "✗ Missing",
        "Gemini (GOOGLE_API_KEY)": "✓" if settings.GOOGLE_API_KEY else "✗ Missing"
    }

    for provider, status in api_keys_status.items():
        if "Missing" in status:
            logger.warning(f"  - {provider}: {status}")
        else:
            logger.info(f"  - {provider}: {status}")

    # 최소 하나의 API 키는 필수
    if not any([settings.ANTHROPIC_API_KEY, settings.OPENAI_API_KEY, settings.GOOGLE_API_KEY]):
        logger.error("❌ 오류: 최소 하나의 LLM API 키가 필요합니다!")
        logger.error("   .env 파일에 ANTHROPIC_API_KEY, OPENAI_API_KEY 또는 GOOGLE_API_KEY를 설정하세요.")

    logger.info(f"  - Tarot Masters: 3명 (달빛의 현자, 별빛의 안내자, 운명의 해석자)")
    logger.info(f"  - 역방향 설정: Master 1 ✓, Master 2 ✗, Master 3 ✓")

    logger.info("✅ Unwoldam Tarot API 준비 완료!")
    logger.info(f"📖 API 문서: http://localhost:8000/docs")

    yield  # 애플리케이션 실행

    # 종료 시
    logger.info("🛑 Unwoldam Tarot API 종료 중...")

    # Redis 연결 종료
    try:
        if session_service.use_redis and session_service.redis_client:
            session_service.redis_client.close()
            logger.info("✓ Redis 연결 종료")
    except Exception as e:
        logger.error(f"✗ Redis 연결 종료 실패: {str(e)}")

    logger.info("✅ 정상 종료 완료")


app = FastAPI(
    title="Unwoldam Tarot API",
    description="""
    🎴 AI 기반 타로 카드 리딩 API

    ## 주요 기능
    - 🔮 3명의 독특한 타로마스터 페르소나
    - 🤖 Multi-LLM 지원 (Claude, OpenAI, Gemini)
    - 📚 RAG 기반 타로카드 의미 검색
    - 💬 만남 횟수에 따른 관계 발전 시스템
    - 🎯 정방향/역방향 해석 설정
    - 🔄 세션 관리 및 히스토리 추적

    ## 타로마스터
    1. **달빛의 현자** (Claude) - 심리학적 깊이 있는 해석
    2. **별빛의 안내자** (OpenAI) - 따뜻한 격려와 희망
    3. **운명의 해석자** (Gemini) - 신비로운 스토리텔링

    ## Phase 완료 현황
    - ✅ Phase 1-9: 모든 핵심 기능 구현 완료
    - ✅ Phase 10: 통합 및 테스트
    """,
    version="1.0.0",
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc"
)

# Rate limiter 설정
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

# Global exception handler
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """
    글로벌 예외 핸들러 - 내부 에러를 숨기고 일반적인 메시지 반환
    """
    # 서버 로그에는 상세한 에러 기록
    logger.error(f"Unhandled exception: {str(exc)}", exc_info=True)

    # 클라이언트에는 일반적인 메시지만 반환
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "error": "Internal server error",
            "message": "An unexpected error occurred. Please try again later.",
            "status_code": 500
        }
    )


# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(tarot_reading.router, prefix="/api/v1/tarot", tags=["Tarot Reading"])
app.include_router(tarot_master.router, prefix="/api/v1/tarot", tags=["Tarot Master"])


@app.get("/", tags=["Health"])
async def root():
    """
    루트 엔드포인트 - API 상태 확인
    """
    return {
        "status": "active",
        "service": "Unwoldam Tarot API",
        "version": "1.0.0",
        "docs": "/docs",
        "message": "Welcome to Unwoldam Tarot API! Visit /docs for API documentation."
    }


@app.get("/health", tags=["Health"])
async def health_check():
    """
    상세한 헬스 체크 엔드포인트
    """
    # 타로카드 로드 상태 확인
    try:
        card_count = len(rag_service.get_all_cards())
        rag_status = "healthy"
    except Exception as e:
        card_count = 0
        rag_status = "error"

    # 세션 서비스 상태 확인
    session_status = "healthy" if session_service else "error"
    session_type = "redis" if session_service.use_redis else "memory"

    return {
        "status": "healthy",
        "version": "1.0.0",
        "services": {
            "llm_providers": {
                "status": "available",
                "providers": ["claude", "openai", "gemini"]
            },
            "rag": {
                "status": rag_status,
                "cards_loaded": card_count
            },
            "session": {
                "status": session_status,
                "storage_type": session_type
            }
        },
        "features": [
            "tarot_reading",
            "tarot_master_personas",
            "rag_search",
            "session_management",
            "reversed_card_settings",
            "relationship_progression"
        ],
        "tarot_masters": [
            {"id": "master_1", "name": "달빛의 현자", "reversed": True},
            {"id": "master_2", "name": "별빛의 안내자", "reversed": False},
            {"id": "master_3", "name": "운명의 해석자", "reversed": True}
        ]
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )

