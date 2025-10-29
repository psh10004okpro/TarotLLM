# LLM 프로바이더 사용 가이드

Unwoldam 타로 API는 여러 LLM 제공자를 쉽게 전환할 수 있는 추상화 레이어를 제공합니다.

## 📋 목차

1. [지원하는 LLM 프로바이더](#지원하는-llm-프로바이더)
2. [설정 방법](#설정-방법)
3. [기본 사용법](#기본-사용법)
4. [고급 사용법](#고급-사용법)
5. [프로바이더 전환](#프로바이더-전환)
6. [에러 처리](#에러-처리)

---

## 지원하는 LLM 프로바이더

### 1. Claude (Anthropic) ✨
- **모델**: `claude-sonnet-4-5-20250929`
- **특징**: 가장 뛰어난 한국어 이해력과 타로 해석 품질
- **추천 용도**: 프리미엄 타로 리딩, 깊이 있는 해석
- **비용**: 중간~높음

### 2. GPT-4 (OpenAI) 🔥
- **모델**: `gpt-4-turbo`
- **특징**: 안정적이고 범용적인 성능
- **추천 용도**: 일반적인 타로 리딩, 대화형 상담
- **비용**: 중간

### 3. Gemini (Google) 💎
- **모델**: `gemini-pro`
- **특징**: 빠른 응답 속도, 합리적인 가격
- **추천 용도**: 대량 처리, 빠른 응답이 필요한 경우
- **비용**: 낮음~중간

---

## 설정 방법

### 1. API 키 설정

`.env` 파일을 생성하고 API 키를 설정하세요:

```bash
# .env 파일
ANTHROPIC_API_KEY=your_anthropic_api_key_here
OPENAI_API_KEY=your_openai_api_key_here
GOOGLE_API_KEY=your_google_api_key_here

# 기본 프로바이더 선택
DEFAULT_LLM_PROVIDER=claude
```

### 2. 모델 설정 (선택사항)

특정 모델을 사용하고 싶다면:

```bash
CLAUDE_MODEL=claude-sonnet-4-5-20250929
OPENAI_MODEL=gpt-4-turbo
GEMINI_MODEL=gemini-pro
```

---

## 기본 사용법

### 방법 1: 기본 프로바이더 사용

```python
from app.services.llm_service import llm_service

# 기본 프로바이더(config에서 설정한)를 사용
response = await llm_service.generate_response(
    prompt="타로 카드 '광대'의 의미를 설명해주세요",
    system_prompt="당신은 전문 타로 마스터입니다."
)

print(response)
```

### 방법 2: 특정 프로바이더 지정

```python
# Claude 사용
response = await llm_service.generate_response(
    prompt="타로 카드 '광대'의 의미를 설명해주세요",
    system_prompt="당신은 전문 타로 마스터입니다.",
    provider_name="claude"
)

# GPT-4 사용
response = await llm_service.generate_response(
    prompt="타로 카드 '광대'의 의미를 설명해주세요",
    system_prompt="당신은 전문 타로 마스터입니다.",
    provider_name="openai"
)

# Gemini 사용
response = await llm_service.generate_response(
    prompt="타로 카드 '광대'의 의미를 설명해주세요",
    system_prompt="당신은 전문 타로 마스터입니다.",
    provider_name="gemini"
)
```

---

## 고급 사용법

### 1. 스트리밍 응답

실시간으로 응답을 받아보세요:

```python
async for chunk in llm_service.generate_streaming(
    prompt="3장의 카드를 해석해주세요",
    system_prompt="당신은 타로 마스터입니다.",
    provider_name="claude"
):
    print(chunk, end="", flush=True)
```

### 2. RAG와 함께 사용

타로 카드 데이터베이스의 정보를 활용:

```python
from app.services.rag_service import rag_service

# 카드 정보 가져오기
card = rag_service.get_card_by_id(0)  # 광대 카드
context = f"{card.name}: {card.image_description}\n키워드: {', '.join(card.keywords[:5])}"

# 컨텍스트와 함께 해석 생성
response = await llm_service.generate_with_context(
    prompt="이 카드가 연애 운세에서 나왔을 때의 의미는?",
    context=context,
    provider_name="claude"
)

print(response)
```

### 3. 타로 마스터 페르소나와 함께 사용

```python
from app.core.personas.tarot_master_1 import TarotMaster1

# 타로 마스터 페르소나 초기화
master = TarotMaster1()
system_prompt = master.get_system_prompt(interaction_count=5)

# 페르소나의 스타일로 해석 생성
response = await llm_service.generate_response(
    prompt="광대 카드가 나왔습니다. 해석해주세요.",
    system_prompt=system_prompt,
    provider_name="claude"
)

print(response)
```

### 4. 프로바이더별 파라미터 커스터마이징

```python
# Claude - 창의성 조절
response = await llm_service.generate_response(
    prompt="타로 카드 해석",
    provider_name="claude",
    temperature=0.8,  # 0.0 (정확) ~ 1.0 (창의적)
    max_tokens=2000
)

# OpenAI - 응답 형식 제어
response = await llm_service.generate_response(
    prompt="타로 카드 해석",
    provider_name="openai",
    temperature=0.7,
    top_p=0.9
)

# Gemini - 안전 설정
response = await llm_service.generate_response(
    prompt="타로 카드 해석",
    provider_name="gemini",
    temperature=0.7
)
```

---

## 프로바이더 전환

### 설정 파일에서 전환

`app/config.py` 또는 `.env` 파일 수정:

```python
# 방법 1: config.py
DEFAULT_LLM_PROVIDER = "claude"  # 또는 "openai", "gemini"

# 방법 2: .env 파일
DEFAULT_LLM_PROVIDER=claude
```

### 런타임에서 전환

```python
# 프로바이더 정보 확인
providers = llm_service.list_providers()
print(f"사용 가능한 프로바이더: {providers}")

# 특정 프로바이더 정보
info = llm_service.get_provider_info("claude")
print(f"모델: {info['model']}")
print(f"사용 가능: {info['available']}")

# 프로바이더 가져오기
provider = llm_service.get_provider("claude")
if provider.is_available():
    response = await provider.generate(
        prompt="타로 카드 해석",
        system_prompt="당신은 타로 마스터입니다."
    )
```

### 자동 Fallback 구현

```python
async def generate_with_fallback(prompt: str, system_prompt: str):
    """프로바이더 Fallback 예제"""
    providers = ["claude", "openai", "gemini"]

    for provider_name in providers:
        try:
            provider = llm_service.get_provider(provider_name)
            if provider.is_available():
                return await llm_service.generate_response(
                    prompt=prompt,
                    system_prompt=system_prompt,
                    provider_name=provider_name
                )
        except Exception as e:
            print(f"{provider_name} 실패: {e}, 다음 프로바이더 시도...")
            continue

    raise Exception("모든 프로바이더 사용 불가")

# 사용
response = await generate_with_fallback(
    prompt="타로 카드 해석",
    system_prompt="당신은 타로 마스터입니다."
)
```

---

## 에러 처리

### 일반적인 에러와 해결 방법

```python
from app.services.llm_service import llm_service

async def safe_generate(prompt: str, provider_name: str = None):
    """안전한 LLM 응답 생성"""
    try:
        # 프로바이더 가져오기
        provider = llm_service.get_provider(provider_name)

        # API 키 확인
        if not provider.is_available():
            return {
                "success": False,
                "error": "API 키가 설정되지 않았습니다.",
                "solution": f".env 파일에 {provider_name.upper()}_API_KEY를 설정하세요."
            }

        # 응답 생성
        response = await llm_service.generate_response(
            prompt=prompt,
            provider_name=provider_name
        )

        return {
            "success": True,
            "response": response
        }

    except ValueError as e:
        # 잘못된 프로바이더 이름
        return {
            "success": False,
            "error": f"프로바이더를 찾을 수 없습니다: {e}",
            "solution": "claude, openai, gemini 중 하나를 선택하세요."
        }

    except RuntimeError as e:
        # API 호출 에러
        return {
            "success": False,
            "error": f"API 호출 실패: {e}",
            "solution": "API 키가 유효한지 확인하고, 요청 제한을 확인하세요."
        }

    except Exception as e:
        # 기타 에러
        return {
            "success": False,
            "error": f"알 수 없는 에러: {e}",
            "solution": "로그를 확인하고 개발자에게 문의하세요."
        }

# 사용 예제
result = await safe_generate(
    prompt="타로 카드 해석",
    provider_name="claude"
)

if result["success"]:
    print(result["response"])
else:
    print(f"❌ 에러: {result['error']}")
    print(f"💡 해결: {result['solution']}")
```

---

## 실전 예제

### 타로 리딩 서비스 구현

```python
from app.services.llm_service import llm_service
from app.services.rag_service import rag_service
from app.core.personas.tarot_master_1 import TarotMaster1

async def create_tarot_reading(
    card_ids: list[int],
    question: str,
    user_id: str,
    provider: str = "claude"
):
    """
    완전한 타로 리딩 생성

    Args:
        card_ids: 뽑힌 카드 ID 리스트
        question: 사용자 질문
        user_id: 사용자 ID
        provider: LLM 프로바이더

    Returns:
        타로 리딩 결과
    """
    # 1. 카드 정보 가져오기
    cards = [rag_service.get_card_by_id(cid) for cid in card_ids]

    # 2. 컨텍스트 구성
    context = "뽑힌 카드:\n"
    for i, card in enumerate(cards, 1):
        context += f"{i}. {card.name} ({card.name_ko})\n"
        context += f"   키워드: {', '.join(card.keywords[:5])}\n"
        context += f"   의미: {card.love[:100]}...\n\n"

    # 3. 타로 마스터 페르소나
    master = TarotMaster1()
    system_prompt = master.get_system_prompt()

    # 4. 프롬프트 작성
    prompt = f"""
질문: {question}

{context}

위 카드들을 바탕으로 깊이 있고 통찰력 있는 타로 리딩을 제공해주세요.
각 카드의 의미를 설명하고, 카드들 간의 관계를 분석하며,
질문자에게 필요한 조언을 전달해주세요.
    """

    # 5. LLM으로 해석 생성
    interpretation = await llm_service.generate_with_context(
        prompt=prompt,
        context=context,
        system_prompt=system_prompt,
        provider_name=provider
    )

    return {
        "user_id": user_id,
        "question": question,
        "cards": [{"id": c.id, "name": c.name, "name_ko": c.name_ko} for c in cards],
        "interpretation": interpretation,
        "provider": provider
    }

# 사용
reading = await create_tarot_reading(
    card_ids=[0, 1, 13],  # 광대, 마법사, 죽음
    question="내 연애운은 어떤가요?",
    user_id="user_123",
    provider="claude"
)

print(reading["interpretation"])
```

---

## 성능 최적화 팁

### 1. 적절한 프로바이더 선택

```python
# 짧은 응답 필요: Gemini (빠르고 저렴)
quick_response = await llm_service.generate_response(
    prompt="한 줄로 요약해주세요",
    provider_name="gemini",
    max_tokens=100
)

# 깊이 있는 해석 필요: Claude (고품질)
detailed_reading = await llm_service.generate_response(
    prompt="상세하게 해석해주세요",
    provider_name="claude",
    max_tokens=2000
)
```

### 2. 캐싱 활용

```python
from functools import lru_cache

@lru_cache(maxsize=100)
def get_card_context(card_id: int) -> str:
    """카드 정보 캐싱"""
    card = rag_service.get_card_by_id(card_id)
    return f"{card.name}: {card.image_description}"

# 반복적인 카드 조회 시 캐시 사용
context = get_card_context(0)
```

### 3. 배치 처리

```python
import asyncio

async def batch_readings(questions: list[str], provider: str = "gemini"):
    """여러 질문을 배치로 처리"""
    tasks = [
        llm_service.generate_response(
            prompt=q,
            provider_name=provider
        )
        for q in questions
    ]

    return await asyncio.gather(*tasks)

# 사용
questions = [
    "오늘의 운세는?",
    "연애운은?",
    "재물운은?"
]

results = await batch_readings(questions, provider="gemini")
```

---

## 문제 해결

### Q: "Provider not found" 에러가 발생해요
**A**: 프로바이더 이름을 확인하세요. `claude`, `openai`, `gemini` 중 하나여야 합니다.

### Q: "API key not configured" 에러가 발생해요
**A**: `.env` 파일에 해당 프로바이더의 API 키를 설정했는지 확인하세요.

### Q: 응답이 너무 느려요
**A**: Gemini 프로바이더를 사용하거나, `max_tokens`를 줄여보세요.

### Q: 한국어 응답 품질이 좋지 않아요
**A**: Claude 프로바이더를 사용하고, system_prompt에 "한국어로 답변해주세요"를 추가하세요.

### Q: 여러 프로바이더를 동시에 사용할 수 있나요?
**A**: 네! 각 요청마다 다른 프로바이더를 지정할 수 있습니다.

---

## 추가 리소스

- [FastAPI 공식 문서](https://fastapi.tiangolo.com/)
- [Anthropic Claude API](https://docs.anthropic.com/)
- [OpenAI API](https://platform.openai.com/docs/)
- [Google Gemini API](https://ai.google.dev/docs)

---

**문의사항이 있으시면 이슈를 등록해주세요!** 🎴✨
