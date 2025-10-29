"""
Phase 3 테스트: LLM 프로바이더 추상화 레이어
여러 LLM 제공자를 쉽게 전환할 수 있는지 테스트합니다.
"""

import asyncio
from app.services.llm_service import llm_service
from app.config import settings


async def test_llm_providers():
    """LLM 프로바이더 전환 테스트"""
    print("=" * 80)
    print("Phase 3 테스트: LLM 프로바이더 추상화 레이어")
    print("=" * 80)

    # 사용 가능한 프로바이더 확인
    print("\n📋 사용 가능한 LLM 프로바이더:")
    providers = llm_service.list_providers()
    for provider in providers:
        print(f"   - {provider}")

    # 각 프로바이더 정보 확인
    print("\n" + "=" * 80)
    print("프로바이더 상세 정보")
    print("=" * 80)

    for provider_name in providers:
        info = llm_service.get_provider_info(provider_name)
        status = "✅ 사용 가능" if info['available'] else "❌ API 키 필요"
        print(f"\n🔹 {provider_name.upper()}")
        print(f"   모델: {info['model']}")
        print(f"   상태: {status}")

    # 기본 프로바이더 확인
    print("\n" + "=" * 80)
    print("기본 프로바이더 설정")
    print("=" * 80)
    print(f"\n⚙️  현재 기본 프로바이더: {settings.DEFAULT_LLM_PROVIDER}")
    print(f"   Claude 모델: {settings.CLAUDE_MODEL}")
    print(f"   OpenAI 모델: {settings.OPENAI_MODEL}")
    print(f"   Gemini 모델: {settings.GEMINI_MODEL}")

    # 프로바이더 전환 테스트
    print("\n" + "=" * 80)
    print("프로바이더 전환 테스트")
    print("=" * 80)

    test_prompt = "타로 카드 '광대'의 의미를 한 문장으로 설명해주세요."
    test_system = "당신은 전문 타로 마스터입니다."

    for provider_name in providers:
        print(f"\n🔄 {provider_name.upper()}로 전환 중...")

        try:
            provider = llm_service.get_provider(provider_name)
            print(f"   ✓ 프로바이더 획득 성공: {provider}")

            if provider.is_available():
                print(f"   ✓ API 키 확인됨")
                print(f"   ℹ️  실제 API 호출은 스킵 (API 키가 설정되지 않았을 수 있음)")
            else:
                print(f"   ⚠️  API 키가 설정되지 않음")
                print(f"   💡 .env 파일에 {provider_name.upper()}_API_KEY를 설정하세요")

        except Exception as e:
            print(f"   ❌ 오류: {e}")

    # 추상화 레이어의 장점 설명
    print("\n" + "=" * 80)
    print("✨ LLM 추상화 레이어의 장점")
    print("=" * 80)
    print("""
1. 🔄 쉬운 전환
   - config.py에서 DEFAULT_LLM_PROVIDER만 변경하면 됩니다
   - 코드 수정 없이 프로바이더 전환 가능

2. 🎯 일관된 인터페이스
   - 모든 프로바이더가 동일한 메서드 제공
   - generate(), generate_streaming(), is_available()

3. 🛡️ 안정성
   - 한 프로바이더에 문제가 생겨도 다른 프로바이더로 즉시 전환
   - Fallback 메커니즘 구현 가능

4. 💰 비용 최적화
   - 상황에 따라 적절한 모델 선택
   - Claude: 고품질 응답 필요시
   - GPT-4: 범용적 사용
   - Gemini: 비용 절감
    """)

    # 사용 예제
    print("\n" + "=" * 80)
    print("📝 사용 예제 코드")
    print("=" * 80)
    print("""
# 예제 1: 기본 프로바이더 사용
from app.services.llm_service import llm_service

response = await llm_service.generate_response(
    prompt="타로 카드를 해석해주세요",
    system_prompt="당신은 타로 마스터입니다"
)

# 예제 2: 특정 프로바이더 지정
response = await llm_service.generate_response(
    prompt="타로 카드를 해석해주세요",
    system_prompt="당신은 타로 마스터입니다",
    provider_name="claude"  # 또는 "openai", "gemini"
)

# 예제 3: 스트리밍 응답
async for chunk in llm_service.generate_streaming(
    prompt="타로 카드를 해석해주세요",
    provider_name="claude"
):
    print(chunk, end="", flush=True)

# 예제 4: 컨텍스트와 함께 생성 (RAG)
response = await llm_service.generate_with_context(
    prompt="이 카드의 의미는?",
    context="광대 카드: 새로운 시작, 순수함...",
    provider_name="claude"
)
    """)

    print("\n" + "=" * 80)
    print("Phase 3 테스트 완료!")
    print("=" * 80)


def test_provider_initialization():
    """프로바이더 초기화 테스트"""
    print("\n" + "=" * 80)
    print("프로바이더 초기화 테스트")
    print("=" * 80)

    from app.core.llm_providers.claude_provider import ClaudeProvider
    from app.core.llm_providers.openai_provider import OpenAIProvider
    from app.core.llm_providers.gemini_provider import GeminiProvider

    providers_to_test = [
        ("Claude", ClaudeProvider),
        ("OpenAI", OpenAIProvider),
        ("Gemini", GeminiProvider)
    ]

    for name, ProviderClass in providers_to_test:
        print(f"\n🔧 {name} 프로바이더 초기화...")
        try:
            provider = ProviderClass()
            print(f"   ✓ 초기화 성공")
            print(f"   모델: {provider.model_name}")
            print(f"   사용 가능: {provider.is_available()}")
        except Exception as e:
            print(f"   ❌ 초기화 실패: {e}")


if __name__ == "__main__":
    # 동기 테스트
    test_provider_initialization()

    # 비동기 테스트
    print("\n")
    asyncio.run(test_llm_providers())
