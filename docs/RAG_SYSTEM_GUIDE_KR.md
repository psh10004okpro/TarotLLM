# RAG 시스템 사용 가이드

Unwoldam 타로 API의 RAG (Retrieval-Augmented Generation) 시스템은 ChromaDB를 활용하여 타로카드 데이터를 벡터화하고, 의미 기반 검색을 통해 더 정확하고 풍부한 타로 해석을 제공합니다.

## 📋 목차

1. [RAG 시스템이란?](#rag-시스템이란)
2. [시스템 구조](#시스템-구조)
3. [설치 및 설정](#설치-및-설정)
4. [기본 사용법](#기본-사용법)
5. [고급 기능](#고급-기능)
6. [실전 예제](#실전-예제)
7. [성능 최적화](#성능-최적화)
8. [문제 해결](#문제-해결)

---

## RAG 시스템이란?

### 개념

RAG (Retrieval-Augmented Generation)는 "검색 증강 생성"으로, LLM이 응답을 생성할 때 관련 정보를 먼저 검색하여 컨텍스트로 제공하는 기술입니다.

### 타로 리딩에서의 RAG

```
사용자 질문: "연애운을 알고 싶어요"
선택된 카드: 광대, 연인, 태양

[전통적 방식]
→ 3장 카드의 기본 의미만 제공

[RAG 방식]
→ 3장 카드의 의미
→ "연애"와 관련된 다른 카드의 해석
→ 카드 조합에 대한 유사 사례
→ 더 풍부하고 정확한 해석 생성
```

### 주요 이점

1. **🎯 의미 기반 검색**
   - 키워드가 아닌 의미로 검색
   - "연애"와 "사랑", "관계"를 동일하게 인식

2. **📚 컨텍스트 풍부화**
   - 선택된 카드 + 유사 해석 사례
   - LLM이 더 정확한 해석 생성

3. **💡 지능적 매칭**
   - 78장 × 4개 문서 = 312개 문서
   - 각 문서는 특정 상황에 최적화

4. **⚡ 빠른 검색**
   - 벡터 인덱스로 밀리초 단위 검색
   - 실시간 타로 리딩 가능

---

## 시스템 구조

### 1. 임베딩 서비스 (Embedding Service)

텍스트를 벡터로 변환합니다.

```python
# app/services/embedding_service.py

지원 프로바이더:
- OpenAI: text-embedding-3-small (1536차원)
- Local: sentence-transformers (384차원)
```

### 2. 벡터 저장소 (Vector Store)

ChromaDB를 사용한 벡터 데이터베이스입니다.

```python
# app/services/vector_store_service.py

기능:
- 타로카드 데이터 인덱싱
- 시맨틱 검색
- 컨텍스트 생성
```

### 3. RAG 서비스 통합

기존 RAG 서비스에 벡터 검색을 통합했습니다.

```python
# app/services/rag_service.py

get_context_for_reading(..., use_vector_search=True)
```

---

## 설치 및 설정

### 1. 의존성 설치

```bash
# requirements.txt에 포함된 패키지들
pip install chromadb sentence-transformers
```

### 2. 환경 설정

`.env` 파일에 설정 추가:

```bash
# 벡터 저장소 경로
VECTOR_STORE_PATH=./data/vector_store

# 임베딩 모델 (OpenAI 사용 시)
EMBEDDING_MODEL=text-embedding-3-small
OPENAI_API_KEY=your_openai_key_here
```

### 3. 초기 인덱싱

```python
from app.services.vector_store_service import vector_store

# 모든 타로카드 인덱싱
vector_store.index_all_cards(force_reindex=False)
```

---

## 기본 사용법

### 1. 시맨틱 검색

```python
from app.services.vector_store_service import vector_store

# 기본 검색
results = vector_store.search(
    query="연애운을 알고 싶어요",
    n_results=5
)

for result in results:
    print(f"{result['metadata']['card_name']}: {result['similarity']:.2f}")
```

### 2. 컨텍스트별 검색

```python
# 연애 관련 검색
results = vector_store.search(
    query="새로운 사랑이 찾아올까요?",
    context_type="love",  # love, finance, other
    n_results=5
)

# 재물 관련 검색
results = vector_store.search(
    query="사업이 성공할까요?",
    context_type="finance",
    n_results=5
)
```

### 3. 특정 카드로 필터링

```python
# 선택된 카드에서만 검색
selected_cards = [0, 6, 19]  # 광대, 연인, 태양

results = vector_store.search(
    query="새로운 시작과 사랑",
    filter_cards=selected_cards,
    n_results=3
)
```

### 4. RAG 컨텍스트 생성

```python
from app.services.rag_service import rag_service

context = rag_service.get_context_for_reading(
    cards=[0, 6, 19],
    question="새로운 연애를 시작할 수 있을까요?",
    context_type="love",
    use_vector_search=True  # RAG 활성화!
)

print(context)
```

---

## 고급 기능

### 1. 배치 임베딩

여러 텍스트를 한 번에 임베딩:

```python
from app.services.embedding_service import embedding_service

texts = [
    "타로 카드 광대의 의미",
    "연애운 해석",
    "새로운 시작"
]

embeddings = embedding_service.embed_batch(texts)
print(f"각 임베딩 차원: {len(embeddings[0])}")
```

### 2. 재인덱싱

데이터가 업데이트되었을 때:

```python
# 기존 데이터 삭제 후 재인덱싱
vector_store.index_all_cards(force_reindex=True)
```

### 3. 통계 조회

```python
stats = vector_store.get_statistics()

print(f"총 문서 수: {stats['total_documents']}")
print(f"임베딩 차원: {stats['embedding_dimension']}")
print(f"프로바이더: {stats['embedding_provider']}")
```

### 4. 유사도 임계값 설정

```python
# 컨텍스트 생성 시 유사도가 높은 것만 포함
context = vector_store.get_context_for_cards(
    card_ids=[0, 6, 19],
    question="연애운",
    context_type="love",
    n_similar=5  # 유사 문서 개수
)

# 내부적으로 similarity > 0.7인 것만 사용
```

---

## 실전 예제

### 예제 1: 연애운 타로 리딩

```python
from app.services.vector_store_service import vector_store
from app.services.rag_service import rag_service
from app.services.llm_service import llm_service
from app.core.personas.tarot_master_1 import TarotMaster1

async def love_reading(user_id: str, question: str):
    """연애운 타로 리딩 생성"""

    # 1. 카드 선택 (실제로는 랜덤으로)
    selected_cards = [0, 6, 19]  # 광대, 연인, 태양

    # 2. RAG 컨텍스트 생성
    context = rag_service.get_context_for_reading(
        cards=selected_cards,
        question=question,
        context_type="love",
        use_vector_search=True  # RAG 활성화
    )

    # 3. 타로 마스터 페르소나
    master = TarotMaster1()
    system_prompt = master.get_system_prompt()

    # 4. LLM으로 해석 생성
    interpretation = await llm_service.generate_with_context(
        prompt=f"다음 질문에 대해 타로 리딩을 해주세요: {question}",
        context=context,
        system_prompt=system_prompt,
        provider_name="claude"
    )

    return {
        "cards": selected_cards,
        "question": question,
        "interpretation": interpretation
    }

# 사용
result = await love_reading(
    user_id="user_123",
    question="새로운 연애를 시작할 수 있을까요?"
)

print(result["interpretation"])
```

### 예제 2: 재물운 타로 리딩

```python
async def finance_reading(user_id: str, question: str):
    """재물운 타로 리딩 생성"""

    selected_cards = [1, 10, 21]  # 마법사, 운명의 수레바퀴, 세계

    # RAG로 재물 관련 컨텍스트 생성
    context = rag_service.get_context_for_reading(
        cards=selected_cards,
        question=question,
        context_type="finance",
        use_vector_search=True
    )

    # 실용가 페르소나 사용
    from app.core.personas.tarot_master_2 import TarotMaster2
    master = TarotMaster2()

    interpretation = await llm_service.generate_with_context(
        prompt=question,
        context=context,
        system_prompt=master.get_system_prompt(),
        provider_name="claude"
    )

    return interpretation

# 사용
result = await finance_reading(
    user_id="user_123",
    question="이번 사업이 성공할 수 있을까요?"
)
```

### 예제 3: 유사 카드 검색

```python
def find_similar_cards(card_id: int, context_type: str = None):
    """특정 카드와 유사한 의미를 가진 카드 찾기"""

    # 카드 정보 가져오기
    card = rag_service.get_card_by_id(card_id)

    # 카드의 키워드로 검색
    search_query = f"{card.name} {' '.join(card.keywords[:5])}"

    if context_type:
        search_query += f" {context_type}"

    # 검색 (자신은 제외)
    results = vector_store.search(
        query=search_query,
        context_type=context_type,
        n_results=6  # 자신 포함 6개
    )

    # 자신을 제외한 유사 카드
    similar_cards = []
    for result in results:
        if result['metadata']['card_id'] != card_id:
            similar_cards.append({
                'card_id': result['metadata']['card_id'],
                'card_name': result['metadata']['card_name'],
                'card_name_ko': result['metadata']['card_name_ko'],
                'similarity': result['similarity']
            })

    return similar_cards[:5]

# 사용: 광대 카드와 유사한 카드 찾기
similar = find_similar_cards(0, context_type="love")
for card in similar:
    print(f"{card['card_name_ko']}: {card['similarity']:.2f}")
```

### 예제 4: 카드 조합 분석

```python
def analyze_card_combination(card_ids: List[int], theme: str):
    """카드 조합의 의미 분석"""

    # 각 카드의 주요 키워드 수집
    keywords = []
    for card_id in card_ids:
        card = rag_service.get_card_by_id(card_id)
        keywords.extend(card.keywords[:3])

    # 조합 키워드로 검색
    combined_query = f"{theme} {' '.join(keywords)}"

    results = vector_store.search(
        query=combined_query,
        n_results=10
    )

    # 카드별 등장 빈도 분석
    card_frequency = {}
    for result in results:
        card_id = result['metadata']['card_id']
        card_frequency[card_id] = card_frequency.get(card_id, 0) + 1

    return {
        'combination_keywords': keywords,
        'relevant_cards': card_frequency
    }

# 사용: 광대+연인+태양 조합 분석
analysis = analyze_card_combination(
    card_ids=[0, 6, 19],
    theme="새로운 사랑의 시작"
)
```

---

## 성능 최적화

### 1. 임베딩 프로바이더 선택

```python
# OpenAI: 높은 품질, API 비용 발생
embedding_service = EmbeddingService(provider="openai")

# Local: 무료, 약간 낮은 품질
embedding_service = EmbeddingService(provider="local")
```

**권장사항:**
- **개발/테스트**: 로컬 모델 사용
- **프로덕션**: OpenAI 또는 로컬 모델 (요구사항에 따라)

### 2. 캐싱 전략

```python
from functools import lru_cache

@lru_cache(maxsize=1000)
def cached_search(query: str, context_type: str, n_results: int):
    """검색 결과 캐싱"""
    return vector_store.search(
        query=query,
        context_type=context_type,
        n_results=n_results
    )
```

### 3. 배치 처리

```python
# 여러 질문을 한 번에 처리
queries = ["연애운", "재물운", "건강운"]
all_embeddings = embedding_service.embed_batch(queries)

# 각 임베딩으로 검색
for i, embedding in enumerate(all_embeddings):
    results = vector_store.collection.query(
        query_embeddings=[embedding],
        n_results=5
    )
```

### 4. 결과 개수 조정

```python
# 빠른 검색: 적은 결과
quick_results = vector_store.search(query, n_results=3)

# 정확한 검색: 많은 결과
detailed_results = vector_store.search(query, n_results=10)
```

---

## 문제 해결

### Q1: "No module named 'sentence_transformers'"

**문제:** 로컬 임베딩 모델을 사용할 수 없습니다.

**해결:**
```bash
pip install sentence-transformers
```

### Q2: 인덱싱이 너무 느립니다

**원인:** 처음 인덱싱 시 모델 다운로드 + 임베딩 생성

**해결:**
- 로컬 모델: 첫 실행 시 모델 다운로드 (2GB)
- 이후 실행은 빠름
- OpenAI 사용 시 API 호출로 더 빠를 수 있음

### Q3: 검색 결과가 관련 없음

**원인:** 임베딩 품질 또는 질의 문구

**해결:**
```python
# 더 구체적인 질의 사용
bad_query = "카드"
good_query = "새로운 사랑의 시작과 설레는 감정"

# 컨텍스트 타입 지정
results = vector_store.search(
    query=good_query,
    context_type="love"  # 컨텍스트 필터링
)
```

### Q4: ChromaDB 에러

**문제:** "PersistentClient" 관련 에러

**해결:**
```bash
# ChromaDB 재설치
pip install --upgrade chromadb

# 데이터 디렉토리 권한 확인
chmod -R 755 data/vector_store
```

### Q5: 메모리 부족

**원인:** sentence-transformers 모델이 메모리 많이 사용

**해결:**
```python
# 더 작은 모델 사용
from app.services.embedding_service import LocalEmbedding

embedding = LocalEmbedding(
    model_name="sentence-transformers/all-MiniLM-L6-v2"  # 더 작은 모델
)
```

---

## 벡터 검색의 작동 원리

### 1. 텍스트 → 벡터 변환

```
"타로 카드 광대는 새로운 시작을 의미합니다"
         ↓ (임베딩)
[0.23, -0.15, 0.47, ..., 0.31]  # 384차원 또는 1536차원
```

### 2. 유사도 계산

```python
# 코사인 유사도
similarity = 1 - cosine_distance(query_vector, document_vector)

# 0.0 ~ 1.0 사이 값
# 1.0에 가까울수록 더 유사
```

### 3. 타로카드 문서 구조

각 카드는 4개 문서로 분할:

```
광대 카드 (ID: 0)
├── 0_base: 기본 정보, 상징, 수비학
├── 0_love: 연애, 관계, 재회
├── 0_finance: 재물, 사업, 계약
└── 0_other: 건강, 여행, 주의사항
```

---

## 추가 리소스

- [ChromaDB 공식 문서](https://docs.trychroma.com/)
- [Sentence Transformers](https://www.sbert.net/)
- [OpenAI Embeddings](https://platform.openai.com/docs/guides/embeddings)

---

**RAG 시스템으로 더 정확하고 풍부한 타로 리딩을 제공하세요!** 🎴✨
