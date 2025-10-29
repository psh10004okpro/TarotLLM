# 🔒 보안 및 품질

## 최근 업데이트 (2025-01)

### 🛡️ 보안 개선
- ✅ **Rate Limiting**: 10 req/min (리딩), 20 req/min (세션)
- ✅ **CORS 제한**: localhost 포트만 허용 (프로덕션은 도메인 추가 필요)
- ✅ **Input Sanitization**: Prompt injection 방어, XSS 방지
- ✅ **Logging**: 프로덕션급 로깅 시스템 (모든 서비스)

### 📦 의존성 업데이트
- ✅ **chromadb**: 0.4.22 → 1.2.1 (성능 향상, 버그 수정)
- ✅ **sentence-transformers**: 2.2.2 → 5.1.2 (Python 3.11 완벽 지원)

### ✅ 테스트 Coverage
```
Unit Tests: 70/70 passing (100%)
├── Security:        19/19 ✓
├── Session Service: 20/20 ✓
└── RAG Service:     31/31 ✓
```

## 🔐 보안 기능

### 1. Rate Limiting
API 남용을 방지하기 위한 엔드포인트별 제한:

```python
# Tarot Reading: 10 requests/minute
POST /api/v1/reading

# Session Management: 20 requests/minute
GET /api/v1/session/{user_id}
```

### 2. CORS 설정
개발 환경에서는 로컬호스트 포트만 허용:

```python
# app/config.py
ALLOWED_ORIGINS = [
    "http://localhost:3000",  # React/Next.js
    "http://localhost:5173",  # Vite
    "http://localhost:8080",  # Vue
]
```

**프로덕션 배포 시**: `.env`에서 실제 도메인 추가 필요

### 3. Input Sanitization
악의적인 입력으로부터 보호:

```python
# Prompt Injection 방어
sanitize_llm_prompt(user_input)
# - 코드 블록 제거 (```, ~~~)
# - 위험 패턴 필터링 (ignore instructions, system prompts)
# - 최대 길이 제한 (2000자)

# XSS 방지
sanitize_user_name(name)
# - 특수문자 제거
# - 스크립트 태그 제거
# - 최대 길이 제한 (50자)

# Card ID 검증
validate_card_id(card_id)
# - 유효 범위 확인 (0-77)
```

### 4. 프로덕션 로깅
모든 서비스에 구조화된 로깅 적용:

```python
import logging

logger = logging.getLogger(__name__)

# 성공 작업
logger.info("Loaded 78 tarot cards")

# 경고 (복구 가능)
logger.warning("Redis unavailable, using in-memory storage")

# 에러 (스택 트레이스 포함)
logger.error("Failed to initialize client", exc_info=True)
```

**로그 레벨 설정**:
```bash
# .env
LOG_LEVEL=INFO  # DEBUG, INFO, WARNING, ERROR, CRITICAL
```

## 🧪 테스트 실행

### 전체 테스트
```bash
pytest tests/
```

### 특정 카테고리
```bash
# 보안 테스트만
pytest tests/unit/test_security.py -v

# 세션 서비스 테스트만
pytest tests/unit/test_session_service.py -v

# RAG 서비스 테스트만
pytest tests/unit/test_rag_service.py -v
```

### Coverage 리포트
```bash
pytest --cov=app --cov-report=html
open htmlcov/index.html
```

## 📊 성능 최적화

### 1. 2단계 프롬프트 시스템
- SHORT 프롬프트: 간단한 질문 (40-50% 토큰 절약)
- DETAILED 프롬프트: 복잡한 질문 (전체 컨텍스트)

### 2. 벡터 검색 캐싱
- ChromaDB persistent storage
- 임베딩 재사용

### 3. 세션 관리 최적화
- Redis 캐싱 (가능 시)
- 메모리 폴백 (Redis 없을 때)

## 🚨 알려진 제한사항

### Pydantic V2 경고
현재 Pydantic v2의 deprecated `Config` 클래스를 사용 중:
```
PydanticDeprecatedSince20: Support for class-based config is deprecated
```

**영향**: 없음 (v3까지 지원)
**수정 예정**: Pydantic v2 `ConfigDict`로 마이그레이션 예정

### Redis 연결 실패
Redis가 없어도 정상 작동 (메모리 폴백):
```
WARNING: Could not connect to Redis. Using in-memory storage.
```

**영향**: 서버 재시작 시 세션 데이터 손실
**해결**: Redis 서버 실행 또는 영구 저장소 연결

## 🔄 의존성 관리

### 최신 버전 유지
```bash
# 의존성 확인
pip list --outdated

# 업데이트 (주의: 호환성 확인 필요)
pip install --upgrade chromadb sentence-transformers
```

### 보안 취약점 스캔
```bash
# safety 설치
pip install safety

# 취약점 스캔
safety check
```

## 📝 체크리스트: 프로덕션 배포 전

- [ ] API 키가 `.env`에 안전하게 저장되어 있는가?
- [ ] CORS 설정에 프로덕션 도메인이 추가되었는가?
- [ ] Rate limiting 설정이 적절한가?
- [ ] 로그 레벨이 `INFO` 이상으로 설정되었는가?
- [ ] Redis 또는 영구 세션 저장소가 연결되었는가?
- [ ] 모든 테스트가 통과하는가?
- [ ] 의존성에 알려진 취약점이 없는가?
- [ ] 환경변수가 버전 관리에 포함되지 않았는가?
