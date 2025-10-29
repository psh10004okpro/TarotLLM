"""
Vector Search Testing Script
ChromaDB 벡터 검색 기능 종합 테스트

Phase 11: RAG System Completion Test
"""

import sys
from pathlib import Path
import time

# Add app directory to path
sys.path.insert(0, str(Path(__file__).parent))

from app.services.vector_store_service import vector_store
from app.services.embedding_service import embedding_service
from app.services.rag_service import rag_service


def print_section(title: str):
    """섹션 타이틀 출력"""
    print("\n" + "=" * 80)
    print(f"  {title}")
    print("=" * 80 + "\n")


def test_1_basic_initialization():
    """테스트 1: 기본 초기화 확인"""
    print_section("TEST 1: Basic Initialization")

    print("1. Checking RAG Service...")
    cards = rag_service.get_all_cards()
    assert len(cards) > 0, "❌ No cards loaded"
    print(f"   ✓ Loaded {len(cards)} tarot cards")

    print("\n2. Checking Embedding Service...")
    assert embedding_service.is_available(), "❌ Embedding service not available"
    print(f"   ✓ Embedding provider: {embedding_service.provider_name}")
    print(f"   ✓ Embedding dimension: {embedding_service.get_dimension()}")

    print("\n3. Checking Vector Store...")
    assert vector_store.collection is not None, "❌ Vector store not initialized"
    stats = vector_store.get_statistics()
    print(f"   ✓ Collection: {stats['collection_name']}")
    print(f"   ✓ Documents: {stats['total_documents']}")

    print("\n✅ TEST 1 PASSED: All services initialized successfully\n")


def test_2_vector_indexing():
    """테스트 2: 벡터 인덱싱"""
    print_section("TEST 2: Vector Indexing")

    stats_before = vector_store.get_statistics()
    doc_count_before = stats_before.get('total_documents', 0)

    print(f"Documents before indexing: {doc_count_before}")

    if doc_count_before == 0:
        print("\nIndexing all cards (this may take a few minutes)...")
        start_time = time.time()

        vector_store.index_all_cards(force_reindex=False)

        elapsed = time.time() - start_time
        print(f"\n⏱️  Indexing completed in {elapsed:.2f} seconds")
    else:
        print("\n✓ Vector database already indexed")

    # 인덱싱 후 통계 확인
    stats_after = vector_store.get_statistics()
    doc_count_after = stats_after['total_documents']

    print(f"\nDocuments after indexing: {doc_count_after}")

    # 각 카드당 평균 4개의 문서가 생성되어야 함 (base, love, finance, other)
    cards_count = len(rag_service.get_all_cards())
    expected_min = cards_count * 2  # 최소 2개 문서
    expected_max = cards_count * 5  # 최대 5개 문서

    assert expected_min <= doc_count_after <= expected_max, \
        f"❌ Unexpected document count: {doc_count_after} (expected {expected_min}-{expected_max})"

    print(f"\n✅ TEST 2 PASSED: {doc_count_after} documents indexed successfully\n")


def test_3_basic_search():
    """테스트 3: 기본 검색 기능"""
    print_section("TEST 3: Basic Search")

    test_cases = [
        {
            "query": "사랑과 연애",
            "expected_context": "love",
            "min_results": 1
        },
        {
            "query": "돈과 재물운",
            "expected_context": "finance",
            "min_results": 1
        },
        {
            "query": "새로운 시작",
            "expected_context": None,
            "min_results": 1
        }
    ]

    for i, test_case in enumerate(test_cases, 1):
        query = test_case["query"]
        expected_context = test_case["expected_context"]

        print(f"{i}. Testing query: \"{query}\"")

        results = vector_store.search(
            query=query,
            context_type=expected_context,
            n_results=5
        )

        assert len(results) >= test_case["min_results"], \
            f"❌ Expected at least {test_case['min_results']} results, got {len(results)}"

        print(f"   ✓ Found {len(results)} results")

        # 첫 번째 결과 확인
        if results:
            top_result = results[0]
            print(f"   ✓ Top match: {top_result['metadata']['card_name_ko']}")
            print(f"   ✓ Similarity: {top_result['similarity']:.3f}")

            # 문서 타입 확인
            if expected_context:
                doc_type = top_result['metadata'].get('doc_type')
                print(f"   ✓ Document type: {doc_type}")

        print()

    print("✅ TEST 3 PASSED: All searches returned valid results\n")


def test_4_context_filtering():
    """테스트 4: 컨텍스트 필터링"""
    print_section("TEST 4: Context Filtering")

    query = "좋은 결과와 행운"

    contexts = ["love", "finance", "base", "other"]

    for context in contexts:
        print(f"Testing with context: {context}")

        results = vector_store.search(
            query=query,
            context_type=context,
            n_results=3
        )

        assert len(results) > 0, f"❌ No results for context: {context}"

        # 모든 결과가 올바른 context를 가지는지 확인
        for result in results:
            doc_type = result['metadata'].get('doc_type')
            assert doc_type == context, \
                f"❌ Expected doc_type '{context}', got '{doc_type}'"

        print(f"   ✓ {len(results)} results, all have doc_type='{context}'")

    print("\n✅ TEST 4 PASSED: Context filtering works correctly\n")


def test_5_card_specific_search():
    """테스트 5: 특정 카드 검색"""
    print_section("TEST 5: Card-Specific Search")

    # 3장의 카드를 무작위로 선택
    import random
    all_cards = rag_service.get_all_cards()
    selected_cards = random.sample(all_cards, 3)
    card_ids = [card.id for card in selected_cards]

    print(f"Selected cards: {[card.name_ko for card in selected_cards]}")

    query = "이 카드들의 의미는 무엇인가요?"

    # 특정 카드로 필터링해서 검색
    results = vector_store.search(
        query=query,
        n_results=10,
        filter_cards=card_ids
    )

    assert len(results) > 0, "❌ No results for selected cards"

    print(f"\nFound {len(results)} documents from selected cards:")

    # 모든 결과가 선택한 카드에서 나왔는지 확인
    for result in results:
        card_id = result['metadata']['card_id']
        assert card_id in card_ids, \
            f"❌ Unexpected card_id {card_id} in results"

        card_name = result['metadata']['card_name_ko']
        print(f"   ✓ {card_name} (card_id={card_id}, similarity={result['similarity']:.3f})")

    print("\n✅ TEST 5 PASSED: Card-specific filtering works correctly\n")


def test_6_context_generation():
    """테스트 6: 리딩 컨텍스트 생성"""
    print_section("TEST 6: Reading Context Generation")

    # 3-card reading 시뮬레이션
    import random
    all_cards = rag_service.get_all_cards()
    reading_cards = random.sample(all_cards, 3)
    card_ids = [card.id for card in reading_cards]

    questions = [
        ("내 연애운은 어떻게 될까요?", "love"),
        ("새로운 직장으로 이직해도 될까요?", "career"),
        ("이번 투자는 성공할까요?", "finance"),
    ]

    for question, context_type in questions:
        print(f"\nQuestion: {question}")
        print(f"Context: {context_type}")
        print(f"Cards: {[card.name_ko for card in reading_cards]}")

        # 컨텍스트 생성
        context = vector_store.get_context_for_cards(
            card_ids=card_ids,
            question=question,
            context_type=context_type,
            n_similar=3
        )

        assert len(context) > 0, "❌ Empty context generated"

        # 컨텍스트에 필수 요소가 포함되어 있는지 확인
        assert question in context, "❌ Question not in context"
        for card in reading_cards:
            assert card.name_ko in context, f"❌ Card '{card.name_ko}' not in context"

        print(f"   ✓ Context generated ({len(context)} characters)")
        print(f"   ✓ Contains question and all card names")

    print("\n✅ TEST 6 PASSED: Context generation works correctly\n")


def test_7_similarity_scores():
    """테스트 7: 유사도 점수 검증"""
    print_section("TEST 7: Similarity Scores")

    test_queries = [
        "바보 카드의 의미",  # 매우 구체적 - 높은 유사도 예상
        "새로운 여정의 시작",  # 관련 있지만 일반적 - 중간 유사도 예상
        "abcdefg random text",  # 무작위 - 낮은 유사도 예상
    ]

    for query in test_queries:
        print(f"\nQuery: \"{query}\"")

        results = vector_store.search(
            query=query,
            n_results=5
        )

        if not results:
            print("   ⚠️  No results found")
            continue

        print(f"   Found {len(results)} results:")

        for i, result in enumerate(results[:3], 1):
            similarity = result['similarity']
            card_name = result['metadata']['card_name_ko']

            # 유사도 점수가 0-1 범위인지 확인
            assert 0 <= similarity <= 1, \
                f"❌ Invalid similarity score: {similarity}"

            print(f"   [{i}] {card_name}: {similarity:.3f}")

        # 결과가 유사도 순으로 정렬되어 있는지 확인
        similarities = [r['similarity'] for r in results]
        assert similarities == sorted(similarities, reverse=True), \
            "❌ Results not sorted by similarity"

        print("   ✓ Results properly sorted by similarity")

    print("\n✅ TEST 7 PASSED: Similarity scores are valid\n")


def test_8_performance():
    """테스트 8: 성능 테스트"""
    print_section("TEST 8: Performance Test")

    query = "미래의 운세를 알려주세요"
    n_iterations = 10

    print(f"Running {n_iterations} search iterations...")

    start_time = time.time()

    for i in range(n_iterations):
        results = vector_store.search(
            query=query,
            n_results=5
        )
        assert len(results) > 0, f"❌ No results in iteration {i+1}"

    elapsed = time.time() - start_time
    avg_time = elapsed / n_iterations

    print(f"\n⏱️  Total time: {elapsed:.3f} seconds")
    print(f"⏱️  Average time per search: {avg_time:.3f} seconds")

    # 검색 속도가 합리적인지 확인 (3초 이하)
    assert avg_time < 3.0, f"❌ Search too slow: {avg_time:.3f}s per search"

    print(f"\n✅ TEST 8 PASSED: Performance is acceptable (< 3s per search)\n")


def run_all_tests():
    """모든 테스트 실행"""
    print("\n" + "█" * 80)
    print("█" + " " * 78 + "█")
    print("█" + " " * 20 + "VECTOR SEARCH COMPREHENSIVE TEST" + " " * 26 + "█")
    print("█" + " " * 78 + "█")
    print("█" * 80 + "\n")

    tests = [
        ("Basic Initialization", test_1_basic_initialization),
        ("Vector Indexing", test_2_vector_indexing),
        ("Basic Search", test_3_basic_search),
        ("Context Filtering", test_4_context_filtering),
        ("Card-Specific Search", test_5_card_specific_search),
        ("Context Generation", test_6_context_generation),
        ("Similarity Scores", test_7_similarity_scores),
        ("Performance", test_8_performance),
    ]

    passed = 0
    failed = 0
    start_time = time.time()

    for test_name, test_func in tests:
        try:
            test_func()
            passed += 1
        except AssertionError as e:
            print(f"\n❌ TEST FAILED: {test_name}")
            print(f"   Error: {str(e)}\n")
            failed += 1
        except Exception as e:
            print(f"\n💥 TEST ERROR: {test_name}")
            print(f"   Exception: {str(e)}\n")
            import traceback
            traceback.print_exc()
            failed += 1

    total_time = time.time() - start_time

    # 최종 결과
    print("\n" + "█" * 80)
    print("█" + " " * 78 + "█")
    print("█" + " " * 30 + "FINAL RESULTS" + " " * 35 + "█")
    print("█" + " " * 78 + "█")
    print("█" * 80 + "\n")

    print(f"Total Tests:   {passed + failed}")
    print(f"✅ Passed:     {passed}")
    print(f"❌ Failed:     {failed}")
    print(f"⏱️  Total Time: {total_time:.2f} seconds")

    if failed == 0:
        print("\n" + "🎉" * 40)
        print("\n✅ ALL TESTS PASSED! Vector Search System is fully functional!\n")
        print("🎉" * 40 + "\n")
        return 0
    else:
        print(f"\n❌ {failed} test(s) failed. Please check the errors above.\n")
        return 1


if __name__ == "__main__":
    try:
        exit_code = run_all_tests()
        sys.exit(exit_code)
    except KeyboardInterrupt:
        print("\n\n⚠️  Tests interrupted by user\n")
        sys.exit(1)
    except Exception as e:
        print(f"\n\n💥 Fatal error: {e}\n")
        import traceback
        traceback.print_exc()
        sys.exit(1)
