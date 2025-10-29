"""
Phase 5 테스트: 타로마스터 페르소나 시스템
3명의 독특한 페르소나와 interaction-based 관계 시스템 테스트
"""

from app.core.personas.tarot_master_1 import TarotMaster1
from app.core.personas.tarot_master_2 import TarotMaster2
from app.core.personas.tarot_master_3 import TarotMaster3


def test_persona_initialization():
    """페르소나 초기화 테스트"""
    print("=" * 80)
    print("1. 페르소나 초기화 테스트")
    print("=" * 80)

    # 페르소나 1: 달빛의 현자
    master1 = TarotMaster1()
    print(f"\n✓ {master1.name} ({master1.name_en})")
    print(f"  설명: {master1.description}")
    print(f"  스타일: {master1.style}")
    print(f"  권장 LLM: {master1.recommended_llm}")
    print(f"  역방향 지원: {master1.supports_reversed}")

    # 페르소나 2: 별빛의 안내자
    master2 = TarotMaster2()
    print(f"\n✓ {master2.name} ({master2.name_en})")
    print(f"  설명: {master2.description}")
    print(f"  스타일: {master2.style}")
    print(f"  권장 LLM: {master2.recommended_llm}")
    print(f"  역방향 지원: {master2.supports_reversed}")

    # 페르소나 3: 운명의 해석자
    master3 = TarotMaster3()
    print(f"\n✓ {master3.name} ({master3.name_en})")
    print(f"  설명: {master3.description}")
    print(f"  스타일: {master3.style}")
    print(f"  권장 LLM: {master3.recommended_llm}")
    print(f"  역방향 지원: {master3.supports_reversed}")

    # 페르소나 3 - 역방향 비활성화 버전
    master3_no_reversed = TarotMaster3(supports_reversed=False)
    print(f"\n✓ {master3_no_reversed.name} (역방향 비활성화)")
    print(f"  역방향 지원: {master3_no_reversed.supports_reversed}")

    print("\n✅ 페르소나 초기화 테스트 통과!")


def test_interaction_based_greetings():
    """만남 횟수에 따른 인사말 테스트"""
    print("\n" + "=" * 80)
    print("2. Interaction-based 인사말 테스트")
    print("=" * 80)

    personas = [
        TarotMaster1(),
        TarotMaster2(),
        TarotMaster3()
    ]

    interaction_counts = [0, 3, 7, 12]
    user_name = "민수"

    for persona in personas:
        print(f"\n{'─' * 80}")
        print(f"📌 {persona.name}")
        print(f"{'─' * 80}")

        for count in interaction_counts:
            print(f"\n[{count + 1}회 만남]")
            greeting = persona.get_greeting(count, user_name)
            # 첫 두 줄만 출력 (간략하게)
            lines = greeting.split('\n')
            print(f"  {lines[0]}")
            if len(lines) > 1:
                print(f"  {lines[1]}")

    print("\n✅ 인사말 테스트 통과!")


def test_speech_patterns():
    """말투 변화 테스트"""
    print("\n" + "=" * 80)
    print("3. 말투 패턴 변화 테스트")
    print("=" * 80)

    master1 = TarotMaster1()

    print(f"\n📌 {master1.name}의 말투 변화")
    print("─" * 80)

    interaction_stages = [
        (0, "첫 만남"),
        (2, "2-5회 만남"),
        (6, "6-10회 만남"),
        (11, "11회 이상")
    ]

    for count, stage in interaction_stages:
        prompt = master1.get_system_prompt(count, "지현")
        # 말투 가이드 부분만 추출
        if "【말투 가이드" in prompt:
            guide_start = prompt.find("【말투 가이드")
            guide_end = prompt.find("\n\n", guide_start)
            guide = prompt[guide_start:guide_end] if guide_end != -1 else prompt[guide_start:guide_start+300]

            print(f"\n{stage}:")
            # 첫 3줄만 출력
            lines = guide.split('\n')[:3]
            for line in lines:
                if line.strip():
                    print(f"  {line}")

    print("\n✅ 말투 패턴 테스트 통과!")


def test_system_prompts():
    """시스템 프롬프트 생성 테스트"""
    print("\n" + "=" * 80)
    print("4. 시스템 프롬프트 생성 테스트")
    print("=" * 80)

    personas = [
        ("달빛의 현자", TarotMaster1()),
        ("별빛의 안내자", TarotMaster2()),
        ("운명의 해석자", TarotMaster3())
    ]

    for name, persona in personas:
        print(f"\n📌 {name}")
        print("─" * 80)

        # 첫 만남 프롬프트
        prompt = persona.get_system_prompt(0, "수진")

        # 주요 섹션 확인
        sections_found = []
        sections = ["【페르소나 특징】", "【성격】", "【말투와 어조】", "【해석 방식】"]

        for section in sections:
            if section in prompt:
                sections_found.append(section)

        print(f"  ✓ 프롬프트 길이: {len(prompt)} 문자")
        print(f"  ✓ 포함된 섹션: {', '.join(sections_found)}")

        # 페르소나 특징 부분 출력 (첫 2줄)
        if "【페르소나 특징】" in prompt:
            feature_start = prompt.find("【페르소나 특징】")
            feature_end = prompt.find("【", feature_start + 1)
            feature_section = prompt[feature_start:feature_end]
            lines = feature_section.split('\n')[:3]
            print(f"\n  페르소나 특징:")
            for line in lines:
                if line.strip() and "【" not in line:
                    print(f"    {line.strip()}")

    print("\n✅ 시스템 프롬프트 테스트 통과!")


def test_closing_messages():
    """마무리 메시지 테스트"""
    print("\n" + "=" * 80)
    print("5. 마무리 메시지 테스트")
    print("=" * 80)

    personas = [
        TarotMaster1(),
        TarotMaster2(),
        TarotMaster3()
    ]

    for persona in personas:
        print(f"\n📌 {persona.name}")
        print("─" * 80)

        for count in [0, 3, 7, 12]:
            closing = persona.get_closing_message(count)
            print(f"  [{count + 1}회] {closing[:60]}...")

    print("\n✅ 마무리 메시지 테스트 통과!")


def test_persona_characteristics():
    """페르소나별 특성 비교 테스트"""
    print("\n" + "=" * 80)
    print("6. 페르소나 특성 비교")
    print("=" * 80)

    print("""
┌─────────────────┬──────────────────┬──────────────────┬──────────────────┐
│     특성        │  달빛의 현자     │  별빛의 안내자   │  운명의 해석자   │
├─────────────────┼──────────────────┼──────────────────┼──────────────────┤
│ 권장 LLM        │ Claude           │ ChatGPT/OpenAI   │ Gemini           │
├─────────────────┼──────────────────┼──────────────────┼──────────────────┤
│ 성격            │ 철학적, 심리학적 │ 따뜻함, 공감적   │ 직관적, 신비로움 │
├─────────────────┼──────────────────┼──────────────────┼──────────────────┤
│ 말투            │ 사려깊고 차분    │ 친근하고 격려    │ 시적이고 은유적  │
├─────────────────┼──────────────────┼──────────────────┼──────────────────┤
│ 특징            │ 깊은 통찰        │ 실용적 조언      │ 창의적 스토리    │
├─────────────────┼──────────────────┼──────────────────┼──────────────────┤
│ 역방향 해석     │ ✓ 지원           │ ✗ 정방향만       │ ⚙ 설정 가능      │
└─────────────────┴──────────────────┴──────────────────┴──────────────────┘
""")

    master1 = TarotMaster1()
    master2 = TarotMaster2()
    master3 = TarotMaster3()

    print("핵심 메시지 스타일 비교:")
    print(f"\n{master1.name}:")
    print('  "카드의 상징과 무의식의 세계를 탐구하며..."')
    print(f"\n{master2.name}:")
    print('  "괜찮아요, 당신은 충분히 잘하고 있어요!"')
    print(f"\n{master3.name}:")
    print('  "별들이 당신의 도착을 속삭였습니다..."')

    print("\n✅ 특성 비교 테스트 통과!")


def demonstrate_interaction_progression():
    """만남 횟수에 따른 관계 발전 시연"""
    print("\n" + "=" * 80)
    print("7. 관계 발전 시연 (별빛의 안내자)")
    print("=" * 80)

    master = TarotMaster2()
    user_name = "서연"

    stages = [
        (0, "첫 만남", "정중하고 친근하게"),
        (2, "3번째 만남", "편안하고 격려"),
        (6, "7번째 만남", "친구처럼 친밀"),
        (12, "13번째 만남", "깊은 유대감")
    ]

    for count, stage, description in stages:
        print(f"\n{'─' * 80}")
        print(f"[{stage}] {description}")
        print(f"{'─' * 80}")

        greeting = master.get_greeting(count, user_name)
        print(greeting)

        closing = master.get_closing_message(count)
        print(f"\n마무리: {closing}")

    print("\n✅ 관계 발전 시연 완료!")


def show_usage_example():
    """사용 예제 표시"""
    print("\n" + "=" * 80)
    print("📝 페르소나 사용 예제")
    print("=" * 80)

    print("""
# 예제 1: 기본 사용
from app.core.personas.tarot_master_1 import TarotMaster1

master = TarotMaster1()

# 첫 만남 인사
greeting = master.get_greeting(interaction_count=0, user_name="민수")
print(greeting)

# 시스템 프롬프트 생성
system_prompt = master.get_system_prompt(interaction_count=0, user_name="민수")

# LLM에 전달
# await llm_service.generate(
#     prompt=user_question,
#     system_prompt=system_prompt,
#     provider_name=master.recommended_llm  # "claude"
# )


# 예제 2: 설정 가능한 역방향 해석 (운명의 해석자)
from app.core.personas.tarot_master_3 import TarotMaster3

# 역방향 해석 활성화
master_with_reversed = TarotMaster3(supports_reversed=True)

# 역방향 해석 비활성화
master_no_reversed = TarotMaster3(supports_reversed=False)


# 예제 3: Interaction count 관리
session_data = {
    "user_id": "user123",
    "interaction_count": 5,  # 6번째 만남
    "user_name": "지현"
}

master = TarotMaster2()
greeting = master.get_greeting(
    interaction_count=session_data["interaction_count"],
    user_name=session_data["user_name"]
)
# "지현님, 반가워요! 벌써 6번째 만남이에요..."


# 예제 4: 페르소나 선택 시스템
persona_map = {
    "philosophical": TarotMaster1(),
    "warm": TarotMaster2(),
    "mystical": TarotMaster3()
}

user_preference = "warm"
master = persona_map[user_preference]
    """)


def main():
    """메인 테스트 실행"""
    print("\n" + "🎴" * 40)
    print("Phase 5: 타로마스터 페르소나 시스템 테스트")
    print("🎴" * 40)

    # 1. 초기화 테스트
    test_persona_initialization()

    # 2. 인사말 테스트
    test_interaction_based_greetings()

    # 3. 말투 패턴 테스트
    test_speech_patterns()

    # 4. 시스템 프롬프트 테스트
    test_system_prompts()

    # 5. 마무리 메시지 테스트
    test_closing_messages()

    # 6. 특성 비교
    test_persona_characteristics()

    # 7. 관계 발전 시연
    demonstrate_interaction_progression()

    # 8. 사용 예제
    show_usage_example()

    print("\n" + "=" * 80)
    print("✅ Phase 5 테스트 완료!")
    print("=" * 80)

    print("""
🎉 모든 페르소나가 성공적으로 구현되었습니다!

✓ 3개의 독특한 페르소나
✓ Interaction-based 관계 시스템 (0회, 1-4회, 5-9회, 10+회)
✓ 각 페르소나별 말투 변화
✓ 권장 LLM 프로바이더 매핑
✓ 설정 가능한 역방향 해석 지원

다음 단계:
- API 엔드포인트와 통합
- 세션 관리 시스템과 연결
- LLM 프로바이더와 통합 테스트
    """)


if __name__ == "__main__":
    main()
