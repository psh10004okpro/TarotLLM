# 🎴 Unwoldam Tarot LLM API

AI-powered Tarot Card Reading API with multiple LLM providers and diverse tarot master personas.

**Phase 1-12 완료** ✅ | Version 1.2.0 | [API Documentation](http://localhost:8000/docs)

[![Tests](https://img.shields.io/badge/tests-70%2F70%20passing-success)](docs/TESTING.md)
[![Security](https://img.shields.io/badge/security-rate%20limiting%20%7C%20CORS%20%7C%20sanitization-blue)](docs/SECURITY.md)
[![Python](https://img.shields.io/badge/python-3.11%2B-blue)]()
[![FastAPI](https://img.shields.io/badge/FastAPI-latest-green)]()

## 📚 Documentation

- [🚀 프로덕션 배포 가이드](docs/DEPLOYMENT.md) - Docker, 클라우드, CI/CD, 모니터링
- [🛡️ 보안 및 품질 가이드](docs/SECURITY.md) - 보안 기능, 테스트, 의존성 관리
- [🧪 테스트 가이드](docs/TESTING.md) - 70개 단위 테스트 상세 설명
- [📖 API 문서](http://localhost:8000/docs) - 대화형 Swagger UI
- [🤖 LLM Provider 가이드](docs/LLM_PROVIDER_GUIDE_KR.md) - LLM 프로바이더 사용법
- [📚 RAG 시스템 가이드](docs/RAG_SYSTEM_GUIDE_KR.md) - 벡터 검색 상세 가이드
- [🎭 Persona 시스템 가이드](docs/PERSONA_SYSTEM_GUIDE_KR.md) - 타로마스터 페르소나

## ✨ Features

### 🔮 3명의 타로마스터 페르소나
- **달빛의 현자** (Claude Sonnet 4.5): 심리학적 깊이 있는 해석 | 역방향 ✓
- **별빛의 안내자** (GPT-4 Turbo): 따뜻한 격려와 희망 | 정방향 전용
- **운명의 해석자** (Gemini Pro): 신비로운 스토리텔링 | 역방향 ✓

### 🤖 Multi-LLM 지원
- Anthropic Claude (Sonnet 4.5)
- OpenAI GPT-4 Turbo
- Google Gemini Pro

### 📚 RAG 기반 타로카드 시스템
- 78장 완전한 타로카드 데이터베이스
- 사랑, 재정, 직업, 건강 분야별 의미
- 벡터 검색으로 컨텍스트 제공

### 💬 관계 발전 시스템 (4단계)
- **Formal** (1회): 정중하고 격식있는
- **Polite** (2-5회): 부드러운 존댓말
- **Friendly** (6-10회): 친근한 존댓말
- **Intimate** (11+회): 편안한 반말 혼용

### 🎯 고급 기능
- 🔄 세션 관리 및 히스토리 추적
- 🎲 정방향/역방향 설정 (마스터별)
- ⚡ 2단계 프롬프트 최적화 (40-50% 토큰 절약)
- 🃏 5가지 스프레드 타입 지원
- 🔐 RESTful API with Swagger 문서

### 🛡️ 보안 및 품질 (Phase 11)
- ✅ **Rate Limiting**: API 남용 방지 (10-20 req/min)
- ✅ **CORS 제한**: 허용된 origin만 접근
- ✅ **Input Sanitization**: Prompt injection, XSS 방어
- ✅ **프로덕션 로깅**: 구조화된 로깅 시스템
- ✅ **테스트 Coverage**: 70개 단위 테스트 (100% 통과)
- ✅ **최신 의존성**: chromadb 1.2.1, sentence-transformers 5.1.2

### 🚀 프로덕션 배포 (Phase 12)
- ✅ **Docker 최적화**: 멀티스테이지 빌드, Non-root 사용자
- ✅ **Gunicorn + Uvicorn**: 프로덕션급 ASGI 서버 (4 workers)
- ✅ **CI/CD**: GitHub Actions (테스트, 빌드, 배포 자동화)
- ✅ **환경별 설정**: Development, Production 분리
- ✅ **성능 테스트**: Locust 부하 테스트 준비
- ✅ **클라우드 배포 가이드**: AWS, GCP, Azure 지원

📖 **자세한 내용**: [배포 가이드](docs/DEPLOYMENT.md) | [보안 가이드](docs/SECURITY.md) | [테스트 가이드](docs/TESTING.md)

## Project Structure

```
unwoldam-api/
├── app/
│   ├── main.py                 # FastAPI application entry point
│   ├── config.py               # Configuration and settings
│   ├── models/                 # Pydantic data models
│   │   ├── tarot_card.py
│   │   ├── reading.py
│   │   └── user_session.py
│   ├── services/               # Business logic
│   │   ├── llm_service.py
│   │   ├── rag_service.py
│   │   ├── tarot_master_service.py
│   │   └── session_service.py
│   ├── api/v1/                 # API endpoints
│   │   ├── tarot_reading.py
│   │   └── tarot_master.py
│   ├── core/
│   │   ├── llm_providers/      # LLM provider implementations
│   │   │   ├── base.py
│   │   │   ├── claude_provider.py
│   │   │   ├── openai_provider.py
│   │   │   └── gemini_provider.py
│   │   └── personas/           # Tarot master personas
│   │       ├── tarot_master_1.py
│   │       ├── tarot_master_2.py
│   │       └── tarot_master_3.py
│   └── data/                   # Tarot card data
│       ├── tarot_cards.json
│       └── card_meanings.json
├── requirements.txt
├── .env.example
└── README.md
```

## 🚀 Quick Start

### Option 1: Docker (권장)

```bash
# 1. 환경변수 설정
cp .env.example .env
# .env 파일을 열어 API 키 설정

# 2. Docker Compose로 실행
docker-compose up -d

# 3. API 접속
open http://localhost:8000/docs
```

### Option 2: 로컬 개발

```bash
# 1. 저장소 클론
git clone <repository-url>
cd TarotLLM

# 2. 가상 환경 생성
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# 3. 의존성 설치
pip install -r requirements.txt

# 4. 환경변수 설정
cp .env.example .env
# .env 파일을 열어 API 키 설정

# 5. 서버 실행
python -m app.main
# 또는: uvicorn app.main:app --reload
```

### Option 3: Redis 없이 실행

Redis가 없어도 메모리 기반 세션 관리로 정상 작동합니다:

```bash
# .env에서 REDIS_URL 주석 처리
# REDIS_URL=redis://localhost:6379/0

python -m app.main
```

## 🔍 Vector Database Setup

벡터 검색 기능을 활성화하려면 ChromaDB 벡터 데이터베이스를 초기화해야 합니다:

### 1단계: 의존성 설치

```bash
# sentence-transformers는 requirements.txt에 포함되어 있습니다
pip install -r requirements.txt
```

### 2단계: 벡터 DB 초기화

```bash
# 기본 초기화 (인덱스가 없으면 생성)
python init_vector_db.py

# 강제 재인덱싱 (기존 데이터 삭제 후 재생성)
python init_vector_db.py --force-reindex

# 통계 정보만 출력
python init_vector_db.py --stats

# 검색 테스트
python init_vector_db.py --test-search

# 전체 파이프라인 (인덱싱 + 통계 + 테스트)
python init_vector_db.py --all
```

**예상 결과:**
```
🎴 Unwoldam Tarot - Vector Database Initialization
======================================================================

📋 Checking dependencies...

✓ 타로카드 데이터: 78장
✓ 임베딩 서비스: local
  - 모델 차원: 384
✓ ChromaDB 컬렉션: tarot_cards

🚀 Starting vector database indexing...
----------------------------------------------------------------------
📚 78장의 타로카드 인덱싱 시작...
📝 총 312개의 문서 생성됨
🔢 임베딩 생성 중... (차원: 384)
   ✓ 312/312 문서 인덱싱 완료

✅ 인덱싱 완료! 총 312개 문서
```

### 3단계: 벡터 검색 기능 테스트

```bash
# 종합 테스트 실행 (8가지 테스트 시나리오)
python test_vector_search.py
```

**테스트 항목:**
- ✅ Basic Initialization (서비스 초기화 확인)
- ✅ Vector Indexing (벡터 인덱싱 검증)
- ✅ Basic Search (기본 검색 기능)
- ✅ Context Filtering (컨텍스트별 필터링)
- ✅ Card-Specific Search (특정 카드 검색)
- ✅ Context Generation (리딩 컨텍스트 생성)
- ✅ Similarity Scores (유사도 점수 검증)
- ✅ Performance (성능 테스트)

### 벡터 검색 사용하기

벡터 검색을 활성화하면 LLM에게 더 정확한 카드 해석 컨텍스트를 제공할 수 있습니다:

```python
from app.services.rag_service import rag_service

# RAG 활성화된 컨텍스트 생성
context = rag_service.get_context_for_reading(
    cards=[0, 6, 19],  # The Fool, The Lovers, The Sun
    question="내 연애운은 어떻게 될까요?",
    context_type="love",
    use_vector_search=True  # ✨ 벡터 검색 활성화!
)

# 이제 context에는:
# - 선택된 카드들의 의미
# - 질문과 의미적으로 유사한 해석 사례 3개
# - 컨텍스트별(love, finance 등) 맞춤 정보
```

### 임베딩 프로바이더 변경

기본적으로 로컬 `sentence-transformers` 모델을 사용하지만, OpenAI 임베딩도 사용 가능합니다:

```python
# app/services/embedding_service.py 마지막 줄
embedding_service = EmbeddingService(provider="local")  # 기본
# embedding_service = EmbeddingService(provider="openai")  # OpenAI 사용 시
```

**장단점:**
- **Local (기본)**: 무료, 오프라인 가능, 다국어 지원 (384차원)
- **OpenAI**: 더 높은 정확도, API 키 필요, 비용 발생 (1536차원)

## Configuration

Edit the `.env` file with your API keys and preferences:

```env
# LLM Provider API Keys
ANTHROPIC_API_KEY=your_anthropic_api_key_here
OPENAI_API_KEY=your_openai_api_key_here
GOOGLE_API_KEY=your_google_api_key_here

# Default LLM Provider
DEFAULT_LLM_PROVIDER=claude
```

## Usage

1. Start the server:
```bash
python -m app.main
# Or using uvicorn directly:
uvicorn app.main:app --reload
```

2. Access the API documentation:
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## API Endpoints

### Tarot Reading

- `POST /api/v1/reading` - Create a new tarot reading
- `GET /api/v1/reading/{reading_id}` - Get reading by ID
- `GET /api/v1/reading/user/{user_id}/history` - Get user's reading history
- `GET /api/v1/spreads` - List available spread types

### Tarot Master & Sessions

- `GET /api/v1/masters` - List available tarot master personas
- `GET /api/v1/masters/{master_id}` - Get tarot master details
- `POST /api/v1/session` - Create user session
- `GET /api/v1/session/{session_id}` - Get session details
- `GET /api/v1/session/user/{user_id}/history` - Get user's session history
- `DELETE /api/v1/session/{session_id}` - Close session

## Example Usage

### Create a Tarot Reading

```bash
curl -X POST "http://localhost:8000/api/v1/reading" \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": "user_12345",
    "question": "What should I focus on in my career?",
    "spread_type": "three_card",
    "llm_provider": "claude",
    "tarot_master_id": 1
  }'
```

### List Tarot Masters

```bash
curl "http://localhost:8000/api/v1/masters"
```

## LLM Provider Configuration

The API supports multiple LLM providers that can be easily switched via configuration.

### Supported Providers

- **Claude** (Anthropic): `claude-sonnet-4-5-20250929`
- **GPT-4** (OpenAI): `gpt-4-turbo`
- **Gemini** (Google): `gemini-pro`

### Quick Start

1. **Set up API keys** in `.env`:
```bash
ANTHROPIC_API_KEY=your_key_here
OPENAI_API_KEY=your_key_here
GOOGLE_API_KEY=your_key_here

# Choose default provider
DEFAULT_LLM_PROVIDER=claude
```

2. **Use in code**:
```python
from app.services.llm_service import llm_service

# Use default provider
response = await llm_service.generate_response(
    prompt="Interpret this tarot card",
    system_prompt="You are a tarot master"
)

# Or specify provider
response = await llm_service.generate_response(
    prompt="Interpret this tarot card",
    provider_name="claude"  # or "openai", "gemini"
)
```

### Advanced Usage

See [LLM Provider Guide (Korean)](docs/LLM_PROVIDER_GUIDE_KR.md) for:
- Streaming responses
- RAG integration
- Provider fallback
- Error handling
- Performance optimization

## RAG System

The API includes a powerful RAG (Retrieval-Augmented Generation) system using ChromaDB for semantic search of tarot card meanings.

### Features

- **Vector Search**: ChromaDB-based semantic search
- **Embedding Support**: OpenAI or local sentence-transformers
- **Context-Aware**: Search by love, finance, career, health contexts
- **312 Documents**: 78 cards × 4 document types
- **Intelligent Matching**: Finds relevant card interpretations

### Quick Example

```python
from app.services.vector_store_service import vector_store
from app.services.rag_service import rag_service

# Index all cards (first time only)
vector_store.index_all_cards()

# Semantic search
results = vector_store.search(
    query="Will I find new love?",
    context_type="love",
    n_results=5
)

# Get RAG-enhanced context
context = rag_service.get_context_for_reading(
    cards=[0, 6, 19],  # The Fool, The Lovers, The Sun
    question="Will I find new love?",
    context_type="love",
    use_vector_search=True  # Enable RAG!
)
```

### Setup

```bash
# Install dependencies
pip install chromadb sentence-transformers

# Configure in .env
VECTOR_STORE_PATH=./data/vector_store
EMBEDDING_MODEL=text-embedding-3-small
```

See [RAG System Guide (Korean)](docs/RAG_SYSTEM_GUIDE_KR.md) for detailed documentation.

## Tarot Master Persona System

The API features 3 distinct tarot master personas with interaction-based relationship building.

### Three Unique Personas

#### 1. 달빛의 현자 (Sage of Moonlight)
- **Style**: Philosophical, psychological, profound
- **Recommended LLM**: Claude
- **Approach**: Deep analytical insights, Jungian psychology, explores conscious & unconscious
- **Reversed Cards**: ✓ Supported (interprets both upright and reversed)

#### 2. 별빛의 안내자 (Starlight Guide)
- **Style**: Warm, empathetic, encouraging, practical
- **Recommended LLM**: ChatGPT
- **Approach**: Supportive guidance, practical advice, positive energy, emotional comfort
- **Reversed Cards**: ✗ Upright only (focuses on positive perspectives)

#### 3. 운명의 해석자 (Destiny Interpreter)
- **Style**: Intuitive, mystical, poetic, storytelling
- **Recommended LLM**: Gemini
- **Approach**: Creative narratives, card connections, metaphorical language, cosmic perspective
- **Reversed Cards**: ⚙️ Configurable (can be enabled or disabled)

### Interaction-Based Relationships

Each persona evolves their speech patterns and relationship style based on meeting count:

| Meeting # | Relationship | Speech Style | Intimacy |
|-----------|--------------|--------------|----------|
| **1st (0)** | First meeting | Formal, respectful | Professional |
| **2-5th** | Trust building | Friendly honorifics | Warm |
| **6-10th** | Deep bond | Casual honorifics, uses name | Close friend |
| **11+** | Soul companion | May use informal speech | Deep intimacy |

### Quick Example

```python
from app.core.personas.tarot_master_1 import TarotMaster1

# Initialize persona
master = TarotMaster1()

# First meeting (formal)
greeting = master.get_greeting(interaction_count=0, user_name="민수")
# "안녕하세요, 민수님. 저는 '달빛의 현자'입니다..."

# 7th meeting (friendly)
greeting = master.get_greeting(interaction_count=6, user_name="민수")
# "민수님, 또 뵙게 되어 기쁩니다. 7번째 만남이네요..."

# Generate context-aware system prompt
system_prompt = master.get_system_prompt(
    interaction_count=6,
    user_name="민수"
)

# Use with LLM
response = await llm_service.generate(
    prompt=user_question,
    system_prompt=system_prompt,
    provider_name=master.recommended_llm  # "claude"
)
```

See [Persona System Guide (Korean)](docs/PERSONA_SYSTEM_GUIDE_KR.md) for detailed documentation.

## 📋 Development Roadmap

### ✅ Phase 1-10: 핵심 시스템 완료

#### Phase 1: 프로젝트 구조 설계 ✅
- [x] 프로젝트 아키텍처 설계
- [x] 기본 모델 및 서비스 구조
- [x] FastAPI 기반 API 설계

#### Phase 2: 78장 타로카드 데이터베이스 ✅
- [x] 메이저 아르카나 22장
- [x] 마이너 아르카나 56장
- [x] 한국어 의미 데이터베이스
- [x] 사랑, 재정, 직업, 건강별 의미

#### Phase 3: LLM 프로바이더 추상화 ✅
- [x] Base 추상 클래스
- [x] Claude (Sonnet 4.5)
- [x] OpenAI (GPT-4 Turbo)
- [x] Gemini (Pro)
- [x] 스트리밍 지원

#### Phase 4: RAG 시스템 구축 ✅ (100% 완료)
- [x] ChromaDB 벡터 데이터베이스
- [x] 임베딩 서비스 (OpenAI + Local)
- [x] sentence-transformers 통합
- [x] 312개 문서 인덱싱 (78장 × 4타입)
- [x] 시맨틱 벡터 검색
- [x] 컨텍스트 인식 검색
- [x] 자동 초기화 스크립트
- [x] 종합 테스트 스위트

#### Phase 5: 타로마스터 페르소나 시스템 ✅
- [x] 3명의 독특한 페르소나
- [x] 만남 횟수 기반 관계 발전 (4단계)
- [x] 말투 변화 시스템
- [x] LLM 프로바이더 추천

#### Phase 6: 2단계 프롬프트 최적화 시스템 ✅
- [x] SHORT/DETAILED 프롬프트
- [x] 40-50% 토큰 절약
- [x] 자동 복잡도 평가
- [x] 상황별 프롬프트 선택

#### Phase 7: API 엔드포인트 구현 ✅
- [x] POST /api/v1/tarot/reading
- [x] GET /api/v1/tarot/masters
- [x] POST /api/v1/tarot/session
- [x] GET /api/v1/tarot/session/{user_id}
- [x] GET /api/v1/tarot/spreads

#### Phase 8: 세션 관리 시스템 ✅
- [x] Redis 기반 세션 저장
- [x] 타로마스터별 만남 횟수 추적
- [x] 관계 레벨 시스템 (4단계)
- [x] 리딩 히스토리 관리
- [x] 메모리 폴백 시스템

#### Phase 9: 정방향/역방향 설정 관리 ✅
- [x] 타로마스터별 독립 설정
- [x] 자동 카드 뽑기 시 적용
- [x] 수동 카드 선택 시 적용
- [x] 역방향 미지원 시 정방향 강제 전환

#### Phase 10: 통합 및 테스트 ✅
- [x] FastAPI 애플리케이션 초기화
- [x] 환경변수 설정 (.env)
- [x] 통합 테스트 시나리오 (6가지)
- [x] Docker 컨테이너화
- [x] API 문서 자동 생성
- [x] README 완성

### 🔮 향후 계획

#### Phase 11: 보안 및 품질 개선 ✅
- [x] Rate limiting (slowapi)
- [x] CORS 설정
- [x] Input sanitization (prompt injection, XSS)
- [x] 프로덕션 로깅 시스템
- [x] 의존성 업데이트 (chromadb, sentence-transformers)
- [x] 70개 단위 테스트 작성
- [x] 문서화 개선

#### Phase 12: 프로덕션 배포 ✅
- [x] Docker 최적화 (멀티스테이지, Non-root)
- [x] Gunicorn + Uvicorn 프로덕션 서버
- [x] GitHub Actions CI/CD 파이프라인 (3개 워크플로우)
- [x] 환경별 설정 관리 (dev/prod)
- [x] 성능 테스트 준비 (Locust)
- [x] 클라우드 배포 가이드 (AWS, GCP, Azure)
- [x] 프로덕션 배포 문서 (DEPLOYMENT.md)

#### Phase 13: 고급 기능
- [ ] 커스텀 스프레드 빌더
- [ ] 리딩 인사이트 및 분석
- [ ] 다국어 지원 (영어, 일본어)
- [ ] 모바일 앱 통합

#### Phase 14: TTS/STT
- [ ] 음성 기반 리딩
- [ ] Text-to-Speech
- [ ] Speech-to-Text

## Technologies

- **Framework**: FastAPI
- **LLM Providers**: Anthropic Claude, OpenAI GPT, Google Gemini
- **Data Validation**: Pydantic
- **Async**: asyncio, aiofiles
- **Testing**: pytest

## License

[Add your license here]

## Contributing

[Add contribution guidelines here]

## Contact

[Add contact information here]
