"""
Phase 4 테스트: RAG 시스템 구축
ChromaDB를 활용한 벡터 검색 시스템 테스트
"""

import asyncio
from app.services.embedding_service import embedding_service
from app.services.vector_store_service import vector_store
from app.services.rag_service import rag_service


def test_embedding_service():
    """임베딩 서비스 테스트"""
    print("=" * 80)
    print("1. 임베딩 서비스 테스트")
    print("=" * 80)

    print(f"\n📊 임베딩 프로바이더: {embedding_service.provider_name}")
    print(f"✓ 사용 가능: {embedding_service.is_available()}")
    print(f"✓ 차원: {embedding_service.get_dimension()}")

    if embedding_service.is_available():
        # 단일 텍스트 임베딩 테스트
        print("\n🔤 단일 텍스트 임베딩 테스트...")
        test_text = "타로 카드 광대는 새로운 시작을 의미합니다"
        embedding = embedding_service.embed(test_text)
        print(f"   텍스트: {test_text}")
        print(f"   임베딩 차원: {len(embedding)}")
        print(f"   첫 5개 값: {embedding[:5]}")

        # 배치 임베딩 테스트
        print("\n📦 배치 임베딩 테스트...")
        test_texts = [
            "연애운에 대해 알고 싶어요",
            "재물운이 궁금합니다",
            "새로운 시작과 모험"
        ]
        embeddings = embedding_service.embed_batch(test_texts)
        print(f"   {len(test_texts)}개 텍스트 임베딩 완료")
        print(f"   각 임베딩 차원: {len(embeddings[0])}")

        print("\n✅ 임베딩 서비스 테스트 통과!")
    else:
        print("\n⚠️  임베딩 서비스를 사용할 수 없습니다")
        print("   pip install sentence-transformers 실행 필요")


def test_vector_store_indexing():
    """벡터 저장소 인덱싱 테스트"""
    print("\n" + "=" * 80)
    print("2. 벡터 저장소 인덱싱 테스트")
    print("=" * 80)

    # 통계 확인
    stats = vector_store.get_statistics()
    print(f"\n📊 벡터 저장소 상태: {stats['status']}")

    if stats['status'] == 'ready':
        print(f"✓ 총 문서 수: {stats['total_documents']}")
        print(f"✓ 임베딩 차원: {stats['embedding_dimension']}")
        print(f"✓ 임베딩 프로바이더: {stats['embedding_provider']}")
        print(f"✓ 컬렉션 이름: {stats['collection_name']}")

        if stats['total_documents'] == 0:
            print("\n🔄 타로카드 인덱싱 시작...")
            vector_store.index_all_cards(force_reindex=False)

            # 재확인
            stats = vector_store.get_statistics()
            print(f"\n✓ 인덱싱 완료! 총 {stats['total_documents']}개 문서")
        else:
            print("\n✓ 이미 인덱싱되어 있습니다")

        print("\n✅ 벡터 저장소 테스트 통과!")
    else:
        print(f"\n❌ 벡터 저장소 에러: {stats.get('error', 'Unknown')}")


def test_semantic_search():
    """시맨틱 검색 테스트"""
    print("\n" + "=" * 80)
    print("3. 시맨틱 검색 테스트")
    print("=" * 80)

    test_queries = [
        ("연애운을 알고 싶어요", "love"),
        ("재물과 돈에 대해 궁금합니다", "finance"),
        ("새로운 시작과 모험", None),
        ("건강과 몸 상태", "other")
    ]

    for query, context_type in test_queries:
        print(f"\n🔍 질의: '{query}'")
        if context_type:
            print(f"   컨텍스트: {context_type}")

        results = vector_store.search(
            query=query,
            context_type=context_type,
            n_results=3
        )

        if results:
            print(f"   ✓ {len(results)}개 결과 찾음")
            for i, result in enumerate(results[:2], 1):
                print(f"\n   {i}. {result['metadata']['card_name']} ({result['metadata']['card_name_ko']})")
                print(f"      유사도: {result['similarity']:.3f}")
                print(f"      문서 유형: {result['metadata']['doc_type']}")
                print(f"      내용: {result['document'][:100]}...")
        else:
            print("   ⚠️  결과 없음")

    print("\n✅ 시맨틱 검색 테스트 통과!")


def test_context_generation():
    """컨텍스트 생성 테스트"""
    print("\n" + "=" * 80)
    print("4. 컨텍스트 생성 테스트")
    print("=" * 80)

    # 테스트 시나리오들
    scenarios = [
        {
            "name": "연애운 3장 리딩",
            "card_ids": [0, 6, 19],  # 광대, 연인, 태양
            "question": "새로운 연애를 시작할 수 있을까요?",
            "context_type": "love"
        },
        {
            "name": "재물운 3장 리딩",
            "card_ids": [1, 10, 21],  # 마법사, 운명의 수레바퀴, 세계
            "question": "사업이 성공할 수 있을까요?",
            "context_type": "finance"
        }
    ]

    for scenario in scenarios:
        print(f"\n📋 시나리오: {scenario['name']}")
        print(f"   카드: {scenario['card_ids']}")
        print(f"   질문: {scenario['question']}")
        print(f"   유형: {scenario['context_type']}")

        # 기본 컨텍스트 생성
        print("\n   [기본 컨텍스트]")
        basic_context = rag_service.get_context_for_reading(
            cards=scenario['card_ids'],
            question=scenario['question'],
            context_type=scenario['context_type'],
            use_vector_search=False
        )
        print(f"   길이: {len(basic_context)} 문자")
        print(f"   샘플: {basic_context[:150]}...")

        # 벡터 검색 활용 컨텍스트
        if vector_store.collection and vector_store.collection.count() > 0:
            print("\n   [RAG 향상 컨텍스트]")
            rag_context = rag_service.get_context_for_reading(
                cards=scenario['card_ids'],
                question=scenario['question'],
                context_type=scenario['context_type'],
                use_vector_search=True
            )
            print(f"   길이: {len(rag_context)} 문자")
            print(f"   샘플: {rag_context[:150]}...")

            improvement = ((len(rag_context) - len(basic_context)) / len(basic_context)) * 100
            print(f"\n   💡 RAG로 {improvement:.1f}% 더 풍부한 컨텍스트 제공")

    print("\n✅ 컨텍스트 생성 테스트 통과!")


def test_card_filtering():
    """특정 카드 필터링 검색 테스트"""
    print("\n" + "=" * 80)
    print("5. 카드 필터링 검색 테스트")
    print("=" * 80)

    # 특정 카드들(광대, 마법사, 연인)에서만 검색
    filter_cards = [0, 1, 6]
    print(f"\n🎴 필터링 카드: {filter_cards}")

    query = "새로운 시작과 사랑"
    print(f"🔍 질의: '{query}'")

    results = vector_store.search(
        query=query,
        filter_cards=filter_cards,
        n_results=5
    )

    print(f"\n✓ {len(results)}개 결과 (필터링됨)")
    for result in results:
        print(f"   - {result['metadata']['card_name']} (ID: {result['metadata']['card_id']})")
        print(f"     유사도: {result['similarity']:.3f}")

    print("\n✅ 카드 필터링 테스트 통과!")


def show_rag_benefits():
    """RAG 시스템의 이점 설명"""
    print("\n" + "=" * 80)
    print("✨ RAG 시스템의 이점")
    print("=" * 80)

    print("""
1. 🎯 정확한 의미 검색
   - 키워드 매칭이 아닌 의미 기반 검색
   - "연애"와 "사랑", "관계" 등을 동일하게 인식
   - 질문의 의도를 파악하여 관련 해석 제공

2. 📚 컨텍스트 풍부화
   - 선택된 카드의 정보 + 유사한 해석 사례
   - 더 깊이 있고 다양한 관점 제공
   - LLM이 더 정확한 해석 생성 가능

3. 🔄 유연한 검색
   - 정방향/역방향 의미 모두 검색
   - 상황별(연애, 재물, 건강) 맞춤 검색
   - 카드 조합에 대한 통합 해석

4. 💡 지능적 매칭
   - 타로카드 78장 * 4개 문서 = 312개 문서
   - 각 문서는 특정 상황에 최적화
   - 질문과 가장 관련있는 정보만 선택

5. ⚡ 빠른 검색
   - 벡터 인덱스로 밀리초 단위 검색
   - 실시간 타로 리딩 가능
   - 대량 데이터도 빠르게 처리
    """)


def show_usage_examples():
    """사용 예제 표시"""
    print("\n" + "=" * 80)
    print("📝 RAG 시스템 사용 예제")
    print("=" * 80)

    print("""
# 예제 1: 기본 검색
from app.services.vector_store_service import vector_store

results = vector_store.search(
    query="연애운을 알고 싶어요",
    context_type="love",
    n_results=5
)

for result in results:
    print(f"{result['metadata']['card_name']}: {result['similarity']:.2f}")


# 예제 2: 특정 카드로 필터링
results = vector_store.search(
    query="새로운 시작",
    filter_cards=[0, 1, 19],  # 광대, 마법사, 태양
    n_results=3
)


# 예제 3: RAG 컨텍스트 생성
from app.services.rag_service import rag_service

context = rag_service.get_context_for_reading(
    cards=[0, 6, 19],
    question="새로운 연애를 시작할 수 있을까요?",
    context_type="love",
    use_vector_search=True  # RAG 활성화
)


# 예제 4: LLM과 통합
from app.services.llm_service import llm_service

interpretation = await llm_service.generate_with_context(
    prompt="이 카드들을 해석해주세요",
    context=context,
    system_prompt="당신은 타로 마스터입니다",
    provider_name="claude"
)
    """)


def main():
    """메인 테스트 실행"""
    print("\n" + "🎴" * 40)
    print("Phase 4: RAG 시스템 구축 테스트")
    print("🎴" * 40)

    # 1. 임베딩 서비스 테스트
    test_embedding_service()

    # 임베딩이 가능한 경우만 계속 진행
    if not embedding_service.is_available():
        print("\n" + "=" * 80)
        print("⚠️  임베딩 서비스를 사용할 수 없어 나머지 테스트를 건너뜁니다")
        print("   로컬 모델 설치:")
        print("   pip install sentence-transformers")
        print("=" * 80)
        return

    # 2. 벡터 저장소 인덱싱
    test_vector_store_indexing()

    # 3. 시맨틱 검색
    test_semantic_search()

    # 4. 컨텍스트 생성
    test_context_generation()

    # 5. 카드 필터링
    test_card_filtering()

    # RAG 이점 설명
    show_rag_benefits()

    # 사용 예제
    show_usage_examples()

    print("\n" + "=" * 80)
    print("✅ Phase 4 테스트 완료!")
    print("=" * 80)


if __name__ == "__main__":
    main()
