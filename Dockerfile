# =============================================================================
# Unwoldam Tarot LLM API - Dockerfile
# Phase 12: 프로덕션 배포
# =============================================================================

# -----------------------------------------------------------------------------
# Stage 1: Builder - 의존성 설치
# -----------------------------------------------------------------------------
FROM python:3.11-slim as builder

WORKDIR /app

# 시스템 패키지 업데이트 및 필수 패키지 설치
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Python 패키지 설치를 위한 requirements.txt 복사
COPY requirements.txt .

# Python 패키지 설치 (gunicorn 추가)
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt && \
    pip install --no-cache-dir gunicorn

# -----------------------------------------------------------------------------
# Stage 2: Runtime - 최종 이미지
# -----------------------------------------------------------------------------
FROM python:3.11-slim

WORKDIR /app

# 필수 런타임 패키지만 설치
RUN apt-get update && apt-get install -y \
    curl \
    && rm -rf /var/lib/apt/lists/* \
    && apt-get clean

# Non-root 사용자 생성 (보안 강화)
RUN groupadd -r tarot && useradd -r -g tarot tarot

# Builder에서 Python 패키지 복사
COPY --from=builder /usr/local/lib/python3.11/site-packages /usr/local/lib/python3.11/site-packages
COPY --from=builder /usr/local/bin /usr/local/bin

# 애플리케이션 코드 복사
COPY --chown=tarot:tarot . .

# 로그 및 데이터 디렉토리 생성
RUN mkdir -p logs data/vector_store && \
    chown -R tarot:tarot logs data

# Non-root 사용자로 전환
USER tarot

# 포트 노출
EXPOSE 8000

# 헬스체크
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

# 애플리케이션 실행 (Gunicorn with Uvicorn workers)
CMD ["gunicorn", "app.main:app", \
     "--workers", "4", \
     "--worker-class", "uvicorn.workers.UvicornWorker", \
     "--bind", "0.0.0.0:8000", \
     "--timeout", "120", \
     "--graceful-timeout", "30", \
     "--keep-alive", "5", \
     "--access-logfile", "-", \
     "--error-logfile", "-", \
     "--log-level", "info"]
