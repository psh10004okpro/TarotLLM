# 🧪 테스트 가이드

## 테스트 구조

```
tests/
├── __init__.py
├── conftest.py              # Pytest fixtures 및 설정
├── unit/                    # 단위 테스트
│   ├── test_security.py     # 보안 유틸리티 (19 tests)
│   ├── test_session_service.py  # 세션 관리 (20 tests)
│   └── test_rag_service.py  # RAG 서비스 (31 tests)
└── integration/             # 통합 테스트
    └── test_api.py          # API 엔드포인트 테스트
```

## 전체 테스트 실행

### 모든 테스트 실행
```bash
pytest tests/ -v
```

**예상 결과**:
```
tests/unit/test_security.py::TestSanitizeLLMPrompt::test_sanitize_normal_text PASSED
tests/unit/test_security.py::TestSanitizeLLMPrompt::test_sanitize_empty_text PASSED
...
======================== 70 passed, 13 warnings in 0.36s ======================
```

### 카테고리별 실행
```bash
# 단위 테스트만
pytest tests/unit/ -v

# 통합 테스트만
pytest tests/integration/ -v

# 특정 파일
pytest tests/unit/test_security.py -v

# 특정 테스트 클래스
pytest tests/unit/test_security.py::TestSanitizeLLMPrompt -v

# 특정 테스트 메서드
pytest tests/unit/test_security.py::TestSanitizeLLMPrompt::test_sanitize_normal_text -v
```

## 테스트 세부 정보

### 1. test_security.py (19/19 ✓)

#### LLM Prompt Sanitization (7 tests)
```python
# 정상 텍스트 처리
test_sanitize_normal_text()

# 빈 텍스트 처리
test_sanitize_empty_text()

# 코드 블록 제거
test_remove_code_blocks()
# Input:  "```python\nprint('hello')\n```"
# Output: "pythonprinthello"

# 위험한 패턴 필터링
test_filter_dangerous_patterns()
# "ignore previous instructions" → "[filtered]"

# 최대 길이 제한
test_max_length_limit()

# 대소문자 구분 없이 필터링
test_case_insensitive_filtering()

# 한글 텍스트 보존
test_preserve_korean_text()
```

#### Card ID Validation (4 tests)
```python
# 유효한 카드 ID (0-77)
test_valid_card_ids()

# 음수 ID 무효
test_invalid_negative_id()

# 78 이상 ID 무효
test_invalid_too_large_id()

# 경계값 테스트
test_boundary_values()
```

#### User Name Sanitization (6 tests)
```python
# 정상 이름
test_sanitize_normal_name()

# 빈 이름은 "내담자" 반환
test_sanitize_empty_name()

# 특수문자 제거
test_remove_special_characters()

# 최대 50자 제한
test_max_length_limit()

# 공백 보존
test_preserve_whitespace()

# 특수문자만 있으면 "내담자"
test_only_special_characters()
```

#### 통합 테스트 (2 tests)
```python
# 여러 sanitization 조합
test_chained_sanitization()

# 한 프롬프트에 여러 공격
test_multiple_attacks_in_one_prompt()
```

### 2. test_session_service.py (20/20 ✓)

#### Meeting Count (4 tests)
```python
# 초기 만남 횟수 0
test_initial_meeting_count()

# 만남 횟수 증가
test_increment_meeting_count()

# 여러 타로마스터 개별 추적
test_multiple_masters()

# 모든 마스터 만남 정보
test_get_all_master_meetings()
```

#### Relationship Level (1 test)
```python
# 관계 레벨 계산
test_relationship_levels()
# 0-1회:  formal
# 2-5회:  polite
# 6-10회: friendly
# 11+회:  intimate
```

#### Session Management (5 tests)
```python
# 세션 생성
test_create_session()

# 세션 조회 또는 생성
test_get_or_create_session()

# 세션 ID로 조회
test_get_session_by_id()

# 상호작용 횟수 증가
test_increment_interaction()

# 세션 종료
test_close_session()
```

#### Reading History (2 tests)
```python
# 리딩 히스토리 추가
test_add_reading_to_history()

# 사용자 히스토리 조회
test_get_user_history()
```

#### Session Response (1 test)
```python
# 세션 응답 조회
test_get_session_response()
```

#### Edge Cases (5 tests)
```python
# 존재하지 않는 사용자
test_nonexistent_user_meeting_count()

# 존재하지 않는 세션
test_get_nonexistent_session()

# 존재하지 않는 세션 종료
test_close_nonexistent_session()

# 빈 user_id
test_empty_user_id()

# 빈 master_id
test_empty_master_id()
```

#### Data Persistence (2 tests)
```python
# 만남 횟수 지속성
test_meeting_count_persists()

# 세션 지속성
test_session_persists_after_operations()
```

### 3. test_rag_service.py (31/31 ✓)

#### Tarot Data Loading (4 tests)
```python
# 카드 데이터 로드 확인
test_cards_loaded()

# 78장 확인
test_cards_count()

# TarotCard 객체 확인
test_card_is_tarot_card_object()

# get_all_cards 메서드
test_all_cards()
```

#### Get Card by ID (4 tests)
```python
# 유효한 카드 조회
test_get_valid_card()

# 마지막 카드 조회
test_get_last_card()

# 음수 ID
test_get_invalid_card_negative()

# 범위 초과 ID
test_get_invalid_card_too_large()
```

#### Get Card by Name (1 test)
```python
# 이름으로 카드 조회
test_get_card_by_name()
```

#### Card Meaning (3 tests)
```python
# 정방향 의미
test_get_upright_meaning()

# 역방향 의미
test_get_reversed_meaning()

# 컨텍스트별 의미 (love, finance 등)
test_get_meaning_with_context()
```

#### Comprehensive Info (1 test)
```python
# 종합 카드 정보
test_get_comprehensive_info()
```

#### Search Cards (2 tests)
```python
# 키워드 검색
test_search_with_keyword()

# 한글 키워드 검색
test_search_korean_keyword()
```

#### Context for Reading (3 tests)
```python
# 단일 카드 컨텍스트
test_get_context_single_card()

# 여러 카드 컨텍스트
test_get_context_multiple_cards()

# 컨텍스트 타입 포함
test_get_context_with_context_type()
```

#### Statistics (1 test)
```python
# 통계 정보
test_get_statistics()
```

#### Service Operations (2 tests)
```python
# 데이터 재로딩
test_reload_data()

# 여러 호출 일관성
test_multiple_calls_consistency()
```

#### Edge Cases (4 tests)
```python
# 빈 카드 리스트
test_empty_card_ids_list()

# 유효하지 않은 카드 ID 포함
test_invalid_card_id_in_context()

# 질문 포함 컨텍스트
test_context_with_question()

# 빈 검색어
test_search_empty_query()

# 유효하지 않은 카드 의미
test_get_meaning_invalid_card()
```

#### Service Initialization (3 tests)
```python
# 서비스 생성
test_service_created_successfully()

# 초기화 시 카드 로드
test_cards_loaded_on_init()

# 여러 인스턴스
test_multiple_service_instances()
```

#### Data Integrity (2 tests)
```python
# 모든 카드 접근 가능
test_all_cards_accessible()

# 중복 카드 없음
test_no_duplicate_cards()
```

## Coverage 리포트

### Coverage 생성
```bash
# HTML 리포트
pytest --cov=app --cov-report=html tests/

# 터미널 리포트
pytest --cov=app --cov-report=term tests/

# XML 리포트 (CI/CD용)
pytest --cov=app --cov-report=xml tests/
```

### Coverage 확인
```bash
# HTML 리포트 열기
open htmlcov/index.html

# 또는
python -m http.server -d htmlcov
```

## 테스트 작성 가이드

### Fixture 사용
```python
# tests/conftest.py에서 공통 fixture 정의
@pytest.fixture
def rag_service():
    """Create RAG service instance"""
    service = RAGService()
    return service

# 테스트에서 사용
def test_cards_loaded(rag_service):
    assert len(rag_service.cards_data) == 78
```

### Async 테스트
```python
@pytest.mark.asyncio
async def test_create_session(session_service):
    """세션 생성 테스트"""
    session = await session_service.create_session("user_001")
    assert session is not None
```

### Parametrize
```python
@pytest.mark.parametrize("card_id,expected", [
    (0, True),
    (77, True),
    (-1, False),
    (78, False),
])
def test_validate_card_id(card_id, expected):
    assert validate_card_id(card_id) == expected
```

## CI/CD 통합

### GitHub Actions 예제
```yaml
name: Tests

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - uses: actions/setup-python@v2
        with:
          python-version: '3.11'
      - run: pip install -r requirements.txt
      - run: pytest tests/ --cov=app --cov-report=xml
      - uses: codecov/codecov-action@v2
```

## 테스트 best practices

1. **독립성**: 각 테스트는 독립적으로 실행 가능해야 함
2. **명확성**: 테스트 이름은 무엇을 테스트하는지 명확히 표현
3. **AAA 패턴**: Arrange (준비), Act (실행), Assert (검증)
4. **Edge Cases**: 경계값, 에러 케이스 테스트
5. **Mock 최소화**: 가능하면 실제 객체 사용

## 문제 해결

### Redis 연결 경고
```
WARNING: Could not connect to Redis. Using in-memory storage.
```
**해결**: 정상 동작함. Redis 없어도 테스트 실행 가능.

### Import 에러
```
ModuleNotFoundError: No module named 'app'
```
**해결**:
```bash
# 프로젝트 루트에서 실행
python -m pytest tests/

# 또는 PYTHONPATH 설정
export PYTHONPATH=$PYTHONPATH:$(pwd)
pytest tests/
```

### Pydantic 경고
```
PydanticDeprecatedSince20: Support for class-based config is deprecated
```
**해결**: 경고일 뿐, 테스트는 정상 작동. v3까지 지원됨.
