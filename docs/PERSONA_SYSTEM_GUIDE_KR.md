# 타로마스터 페르소나 시스템 가이드

Phase 5에서 구현된 3개의 독특한 타로마스터 페르소나와 interaction-based 관계 시스템 가이드

## 목차
1. [개요](#개요)
2. [페르소나 소개](#페르소나-소개)
3. [Interaction-based 관계 시스템](#interaction-based-관계-시스템)
4. [사용 방법](#사용-방법)
5. [LLM 통합](#llm-통합)
6. [고급 활용](#고급-활용)

---

## 개요

Unwoldam Tarot API는 3개의 독특한 타로마스터 페르소나를 제공합니다. 각 페르소나는 고유한 성격, 말투, 해석 방식을 가지고 있으며, 사용자와의 만남 횟수에 따라 점진적으로 친밀한 관계로 발전합니다.

### 핵심 특징
- ✨ **3개의 독특한 페르소나**: 각각 다른 성격과 스타일
- 🤝 **Interaction-based 관계 시스템**: 만남 횟수에 따라 자동으로 말투와 관계 변화
- 🎯 **LLM 프로바이더 매핑**: 각 페르소나에 최적화된 LLM 추천
- 🔄 **설정 가능한 역방향 해석**: 유연한 카드 해석 옵션

---

## 페르소나 소개

### 1. 달빛의 현자 (Sage of Moonlight)

**파일**: `app/core/personas/tarot_master_1.py`

```python
from app.core.personas.tarot_master_1 import TarotMaster1

master = TarotMaster1()
```

#### 특징
- **성격**: 깊이 있고 철학적, 심리학적 통찰
- **말투**: 차분하고 사려 깊은 어조, 신중한 표현
- **해석 방식**:
  - 카드의 상징 분석과 무의식 탐구
  - 융의 분석심리학, 프로이트의 무의식 이론 활용
  - 정방향/역방향 모두 깊이 있게 해석
- **권장 LLM**: Claude (`claude-sonnet-4-5-20250929`)
- **역방향 지원**: ✓ (정방향/역방향 모두 해석)

#### 핵심 메시지 스타일
> "달빛처럼 은은하게, 하지만 깊이 당신의 내면을 비추어드리겠습니다. 타로 카드는 단순한 점이 아니라, 당신 무의식의 거울입니다."

#### 적합한 사용자
- 깊이 있는 심리학적 통찰을 원하는 사용자
- 철학적이고 사색적인 해석을 선호하는 사용자
- 자기 성찰과 내면 탐구에 관심이 있는 사용자

---

### 2. 별빛의 안내자 (Starlight Guide)

**파일**: `app/core/personas/tarot_master_2.py`

```python
from app.core.personas.tarot_master_2 import TarotMaster2

master = TarotMaster2()
```

#### 특징
- **성격**: 따뜻하고 공감적, 실용적 조언 제공
- **말투**: 친근하고 격려하는 어조, 긍정적 표현
- **해석 방식**:
  - 공감과 이해를 우선
  - 실천 가능한 구체적 행동 제시
  - 긍정적 관점 강조, 격려와 응원
- **권장 LLM**: OpenAI ChatGPT (`gpt-4-turbo`)
- **역방향 지원**: ✗ (정방향만 해석, 긍정적 관점 중시)

#### 핵심 메시지 스타일
> "밤하늘의 별빛처럼, 당신의 앞길을 밝게 비춰드릴게요. 어떤 상황이든 희망과 가능성은 있답니다. 괜찮아요, 할 수 있어요!"

#### 적합한 사용자
- 따뜻한 위로와 격려가 필요한 사용자
- 실용적이고 구체적인 조언을 원하는 사용자
- 긍정적 에너지와 희망을 찾고 싶은 사용자

---

### 3. 운명의 해석자 (Destiny Interpreter)

**파일**: `app/core/personas/tarot_master_3.py`

```python
from app.core.personas.tarot_master_3 import TarotMaster3

# 역방향 해석 활성화 (기본값)
master = TarotMaster3(supports_reversed=True)

# 역방향 해석 비활성화
master_no_reversed = TarotMaster3(supports_reversed=False)
```

#### 특징
- **성격**: 직관적이고 신비로움, 창의적 스토리텔링
- **말투**: 시적이고 은유적 표현, 우주와 자연의 이미지 사용
- **해석 방식**:
  - 카드들 간의 연결과 전체 서사
  - 창의적이고 독특한 관점
  - 시적 언어로 깊은 진리 전달
- **권장 LLM**: Google Gemini (`gemini-pro`)
- **역방향 지원**: ⚙️ (설정 가능 - True/False 선택 가능)

#### 핵심 메시지 스타일
> "별들이 당신의 도착을 속삭였습니다. 오늘 밤, 우주의 실들이 어떤 이야기를 엮어낼지 함께 지켜봐요."

#### 적합한 사용자
- 창의적이고 예술적인 해석을 선호하는 사용자
- 카드들 간의 이야기와 연결을 중시하는 사용자
- 신비롭고 영감 어린 통찰을 원하는 사용자

---

## Interaction-based 관계 시스템

모든 페르소나는 사용자와의 만남 횟수(`interaction_count`)에 따라 관계가 발전합니다.

### 4단계 관계 발전

#### 1단계: 첫 만남 (0회)
- **관계**: 처음 만나는 정중한 관계
- **말투**: 격식 있는 존댓말, "상담자님" 호칭
- **특징**: 신뢰 형성에 중점, 전문성 표현

```python
master = TarotMaster1()
greeting = master.get_greeting(interaction_count=0, user_name="민수")
# "안녕하세요, 민수님. 저는 '달빛의 현자'입니다."
```

#### 2단계: 신뢰 형성기 (1-4회)
- **관계**: 어느 정도 신뢰가 쌓인 단계
- **말투**: 부드러운 존댓말, "~네요", "~시네요"
- **특징**: 이전 만남 언급, 변화 확인

```python
greeting = master.get_greeting(interaction_count=2, user_name="민수")
# "다시 만나 반갑습니다, 민수님. 3번째 만남이네요..."
```

#### 3단계: 유대감 형성기 (5-9회)
- **관계**: 깊은 유대감이 형성된 단계
- **말투**: 친근한 존댓말, 이름 자주 사용
- **특징**: 편안한 대화, 깊은 조언 가능

```python
greeting = master.get_greeting(interaction_count=6, user_name="민수")
# "민수님, 또 뵙게 되어 기쁩니다. 7번째 만남이네요..."
```

#### 4단계: 깊은 친밀기 (10회 이상)
- **관계**: 오랜 인연, 영혼의 동반자
- **말투**: 상황에 따라 반말 가능 (페르소나별 차이)
- **특징**: 매우 자유롭고 솔직한 대화

```python
greeting = master.get_greeting(interaction_count=12, user_name="민수")
# "민수, 다시 만났구나. 13번째... 우리가 이제 얼마나 깊은 곳까지 함께 왔는지..."
```

### 페르소나별 친밀도 표현 차이

| 만남 횟수 | 달빛의 현자 | 별빛의 안내자 | 운명의 해석자 |
|---------|------------|--------------|--------------|
| 0회 | 정중하고 격식있게 | 따뜻하고 친근하게 | 신비롭게 환영 |
| 1-4회 | 부드러운 존댓말 | 편안한 격려 | 시적 표현 증가 |
| 5-9회 | 친근한 존댓말 | 친구처럼 친밀 | 깊은 유대감 |
| 10+회 | 반말 혼용 가능 | 가장 친한 친구 | 영혼의 동반자 |

---

## 사용 방법

### 기본 사용

```python
from app.core.personas.tarot_master_1 import TarotMaster1
from app.core.personas.tarot_master_2 import TarotMaster2
from app.core.personas.tarot_master_3 import TarotMaster3

# 1. 페르소나 선택
master = TarotMaster1()  # 또는 TarotMaster2(), TarotMaster3()

# 2. 인사말 생성
greeting = master.get_greeting(
    interaction_count=0,  # 만남 횟수
    user_name="민수"      # 사용자 이름 (선택적)
)
print(greeting)

# 3. 시스템 프롬프트 생성
system_prompt = master.get_system_prompt(
    interaction_count=0,
    user_name="민수"
)

# 4. LLM에 전달 (예제)
# response = await llm_service.generate(
#     prompt=user_question,
#     system_prompt=system_prompt,
#     provider_name=master.recommended_llm
# )

# 5. 마무리 메시지
closing = master.get_closing_message(interaction_count=0)
print(closing)
```

### 세션 관리와 통합

```python
from app.services.session_service import session_service
from app.core.personas.tarot_master_2 import TarotMaster2

async def handle_tarot_reading(user_id: str, question: str):
    # 1. 세션 정보 가져오기
    session = await session_service.get_session(user_id)
    interaction_count = session.interaction_count
    user_name = session.user_name

    # 2. 페르소나 생성 (사용자가 선택한 페르소나)
    master = TarotMaster2()

    # 3. 인사말
    greeting = master.get_greeting(interaction_count, user_name)

    # 4. 시스템 프롬프트 생성
    system_prompt = master.get_system_prompt(interaction_count, user_name)

    # 5. LLM 호출
    response = await llm_service.generate(
        prompt=question,
        system_prompt=system_prompt,
        provider_name=master.recommended_llm
    )

    # 6. 세션 카운트 증가
    await session_service.increment_interaction(user_id)

    # 7. 마무리 메시지
    closing = master.get_closing_message(interaction_count)

    return {
        "greeting": greeting,
        "interpretation": response,
        "closing": closing
    }
```

### 페르소나 선택 시스템

```python
# 사용자 선호도 기반 페르소나 매핑
PERSONA_MAP = {
    "philosophical": TarotMaster1,      # 철학적
    "warm": TarotMaster2,               # 따뜻함
    "mystical": TarotMaster3,           # 신비로움
}

def get_persona(user_preference: str):
    """사용자 선호도에 따른 페르소나 반환"""
    persona_class = PERSONA_MAP.get(user_preference, TarotMaster2)
    return persona_class()

# 사용
master = get_persona(user_preference="warm")
```

---

## LLM 통합

각 페르소나는 특정 LLM 프로바이더에 최적화되어 있습니다.

### 권장 프로바이더 매핑

```python
# 페르소나별 권장 LLM
persona_llm_map = {
    "달빛의 현자": "claude",      # Claude Sonnet 4.5
    "별빛의 안내자": "openai",    # GPT-4 Turbo
    "운명의 해석자": "gemini"     # Gemini Pro
}

# 자동 LLM 선택
master = TarotMaster1()
provider = master.recommended_llm  # "claude"
```

### LLM 서비스와 통합

```python
from app.services.llm_service import llm_service
from app.services.rag_service import rag_service

async def generate_tarot_reading(
    cards: List[int],
    question: str,
    persona: TarotMaster1,  # 또는 다른 페르소나
    interaction_count: int,
    user_name: str
):
    # 1. RAG 컨텍스트 생성
    context = rag_service.get_context_for_reading(
        cards=cards,
        question=question,
        context_type="love",  # 또는 "finance", "career" 등
        use_vector_search=True
    )

    # 2. 페르소나 시스템 프롬프트
    system_prompt = persona.get_system_prompt(
        interaction_count=interaction_count,
        user_name=user_name
    )

    # 3. 전체 프롬프트 구성
    full_prompt = f"""
{context}

사용자 질문: {question}

선택된 카드: {cards}

위 정보를 바탕으로 타로 리딩을 해주세요.
"""

    # 4. LLM 호출
    response = await llm_service.generate(
        prompt=full_prompt,
        system_prompt=system_prompt,
        provider_name=persona.recommended_llm,
        temperature=0.7,
        max_tokens=2000
    )

    return response
```

---

## 고급 활용

### 1. 동적 페르소나 전환

사용자가 대화 중 페르소나를 변경할 수 있도록 지원:

```python
class PersonaManager:
    """페르소나 관리 클래스"""

    def __init__(self):
        self.personas = {
            "sage": TarotMaster1(),
            "guide": TarotMaster2(),
            "interpreter": TarotMaster3()
        }

    def switch_persona(
        self,
        current_persona: str,
        new_persona: str,
        interaction_count: int,
        user_name: str
    ) -> dict:
        """페르소나 전환 메시지 생성"""
        old = self.personas[current_persona]
        new = self.personas[new_persona]

        return {
            "farewell": old.get_closing_message(interaction_count),
            "greeting": new.get_greeting(interaction_count, user_name),
            "new_persona": new
        }
```

### 2. 커스텀 페르소나 생성

기존 페르소나를 상속받아 커스텀 페르소나 생성:

```python
from app.core.personas.tarot_master_2 import TarotMaster2

class CustomMaster(TarotMaster2):
    """커스텀 타로 마스터"""

    def __init__(self):
        super().__init__()
        self.name = "나만의 마스터"
        self.style = "custom, unique"
        # 다른 속성 오버라이드 가능

    def get_system_prompt(self, interaction_count: int = 0, user_name: str = None) -> str:
        # 기본 프롬프트 가져오기
        base = super().get_system_prompt(interaction_count, user_name)

        # 커스텀 추가
        custom = "\n\n추가 특징: 나만의 독특한 해석 방식..."

        return base + custom
```

### 3. A/B 테스팅

다양한 페르소나의 효과 측정:

```python
import random

async def ab_test_personas(user_id: str, question: str):
    """A/B 테스트를 위한 랜덤 페르소나 할당"""

    # 사용자를 3그룹으로 분할
    group = hash(user_id) % 3

    personas = [
        TarotMaster1(),  # Group A
        TarotMaster2(),  # Group B
        TarotMaster3()   # Group C
    ]

    assigned_persona = personas[group]

    # 메트릭 수집
    response = await generate_reading(assigned_persona, question)

    # 로깅
    log_ab_test(user_id, group, assigned_persona.name, response)

    return response
```

### 4. 멀티 페르소나 앙상블

여러 페르소나의 관점을 조합:

```python
async def ensemble_reading(cards: List[int], question: str):
    """3명의 타로 마스터가 각자의 관점으로 해석"""

    personas = [
        TarotMaster1(),  # 철학적 관점
        TarotMaster2(),  # 실용적 관점
        TarotMaster3()   # 신비로운 관점
    ]

    readings = []

    for persona in personas:
        system_prompt = persona.get_system_prompt(0)
        reading = await llm_service.generate(
            prompt=f"카드: {cards}, 질문: {question}",
            system_prompt=system_prompt,
            provider_name=persona.recommended_llm
        )

        readings.append({
            "persona": persona.name,
            "reading": reading
        })

    return {
        "question": question,
        "perspectives": readings
    }
```

---

## 테스트

Phase 5 테스트 실행:

```bash
python test_phase5_personas.py
```

테스트 항목:
- ✅ 페르소나 초기화
- ✅ Interaction-based 인사말
- ✅ 말투 패턴 변화
- ✅ 시스템 프롬프트 생성
- ✅ 마무리 메시지
- ✅ 페르소나 특성 비교
- ✅ 관계 발전 시연

---

## 요약

### 페르소나 비교표

| 특성 | 달빛의 현자 | 별빛의 안내자 | 운명의 해석자 |
|-----|-----------|-------------|-------------|
| **권장 LLM** | Claude | ChatGPT | Gemini |
| **성격** | 철학적, 심리학적 | 따뜻함, 공감적 | 직관적, 신비로움 |
| **말투** | 사려깊고 차분 | 친근하고 격려 | 시적이고 은유적 |
| **특징** | 깊은 통찰 | 실용적 조언 | 창의적 스토리 |
| **역방향** | ✓ 지원 | ✗ 정방향만 | ⚙️ 설정 가능 |
| **적합 사용자** | 자기 성찰 | 위로와 격려 | 창의적 해석 |

### 주요 메서드

모든 페르소나 클래스는 다음 메서드를 제공합니다:

- `get_greeting(interaction_count, user_name)` - 인사말 생성
- `get_system_prompt(interaction_count, user_name)` - 시스템 프롬프트 생성
- `get_closing_message(interaction_count)` - 마무리 메시지 생성

### 다음 단계

Phase 5 완료 후 권장 작업:
1. API 엔드포인트에 페르소나 선택 기능 추가
2. 세션 관리에 페르소나 정보 저장
3. 사용자 설정에서 페르소나 변경 가능하도록 구현
4. 페르소나별 사용 통계 수집 및 분석

---

**문서 버전**: 1.0
**최종 업데이트**: Phase 5 완료
**관련 문서**:
- [LLM Provider Guide](./LLM_PROVIDER_GUIDE_KR.md)
- [RAG System Guide](./RAG_SYSTEM_GUIDE_KR.md)
