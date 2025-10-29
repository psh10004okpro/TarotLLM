"""
Vector Database Initialization Script
타로카드 데이터를 ChromaDB 벡터 데이터베이스에 인덱싱

Usage:
    python init_vector_db.py                    # 기존 인덱스가 없으면 생성
    python init_vector_db.py --force-reindex    # 기존 인덱스 삭제 후 재생성
    python init_vector_db.py --stats            # 통계 정보만 출력
    python init_vector_db.py --test-search      # 검색 테스트
"""

import sys
import argparse
from pathlib import Path

# Add app directory to path
sys.path.insert(0, str(Path(__file__).parent))

from app.services.vector_store_service import vector_store
from app.services.embedding_service import embedding_service
from app.services.rag_service import rag_service


def print_banner():
    """배너 출력"""
    print("\n" + "=" * 70)
    print("🎴 Unwoldam Tarot - Vector Database Initialization")
    print("=" * 70 + "\n")


def check_dependencies():
    """필수 종속성 확인"""
    print("📋 Checking dependencies...\n")

    # RAG Service 확인
    cards_count = len(rag_service.get_all_cards())
    if cards_count == 0:
        print("❌ 타로카드 데이터를 로드할 수 없습니다")
        print("   app/data/tarot_cards.json 파일을 확인하세요")
        return False
    print(f"✓ 타로카드 데이터: {cards_count}장")

    # Embedding Service 확인
    if not embedding_service.is_available():
        print("❌ 임베딩 서비스를 사용할 수 없습니다")
        print("   sentence-transformers를 설치하거나 OpenAI API 키를 설정하세요")
        print("   pip install sentence-transformers")
        return False
    print(f"✓ 임베딩 서비스: {embedding_service.provider_name}")
    print(f"  - 모델 차원: {embedding_service.get_dimension()}")

    # ChromaDB 확인
    if not vector_store.collection:
        print("❌ ChromaDB 컬렉션을 초기화할 수 없습니다")
        return False
    print(f"✓ ChromaDB 컬렉션: {vector_store.collection_name}")

    print()
    return True


def show_statistics():
    """벡터 DB 통계 출력"""
    print("📊 Vector Database Statistics\n")
    print("-" * 70)

    stats = vector_store.get_statistics()

    if stats["status"] == "not_initialized":
        print("❌ 벡터 저장소가 초기화되지 않았습니다")
        return

    if stats["status"] == "error":
        print(f"❌ 오류 발생: {stats['error']}")
        return

    print(f"Status:              {stats['status']}")
    print(f"Collection Name:     {stats['collection_name']}")
    print(f"Total Documents:     {stats['total_documents']}")
    print(f"Embedding Provider:  {stats['embedding_provider']}")
    print(f"Embedding Dimension: {stats['embedding_dimension']}")

    # RAG 통계
    rag_stats = rag_service.get_statistics()
    print(f"\nTarot Card Statistics:")
    print(f"  Total Cards:     {rag_stats['total_cards']}")
    print(f"  Major Arcana:    {rag_stats['major_arcana']}")
    print(f"  Wands:           {rag_stats['wands']}")
    print(f"  Cups:            {rag_stats['cups']}")
    print(f"  Swords:          {rag_stats['swords']}")
    print(f"  Pentacles:       {rag_stats['pentacles']}")

    print("-" * 70)


def index_cards(force_reindex: bool = False):
    """타로카드 인덱싱"""
    print("\n🚀 Starting vector database indexing...\n")
    print("-" * 70)

    if force_reindex:
        print("⚠️  강제 재인덱싱 모드: 기존 데이터를 삭제합니다")

    vector_store.index_all_cards(force_reindex=force_reindex)

    print("-" * 70)
    print("\n✅ Indexing completed!\n")


def test_search():
    """벡터 검색 테스트"""
    print("\n🔍 Testing Vector Search\n")
    print("-" * 70)

    # 테스트 쿼리들
    test_queries = [
        ("사랑과 관계에 대한 조언", "love"),
        ("새로운 시작과 기회", None),
        ("재물운과 금전적 성공", "finance"),
        ("직업 선택과 진로", "career"),
        ("건강과 치유", "other"),
    ]

    for i, (query, context_type) in enumerate(test_queries, 1):
        print(f"\n{i}. Query: \"{query}\"")
        if context_type:
            print(f"   Context: {context_type}")

        results = vector_store.search(
            query=query,
            context_type=context_type,
            n_results=3
        )

        if not results:
            print("   ❌ No results found")
            continue

        print(f"   Found {len(results)} results:")
        for j, result in enumerate(results, 1):
            similarity = result['similarity']
            card_name = result['metadata'].get('card_name_ko', 'Unknown')
            doc_type = result['metadata'].get('doc_type', 'base')

            # 색상 코드로 유사도 표시
            if similarity > 0.8:
                sim_indicator = "🟢"
            elif similarity > 0.6:
                sim_indicator = "🟡"
            else:
                sim_indicator = "🔴"

            print(f"   {sim_indicator} [{j}] {card_name} (유사도: {similarity:.3f}, 타입: {doc_type})")

            # 문서 내용 미리보기 (첫 100자)
            doc_preview = result['document'][:100].replace('\n', ' ').strip()
            print(f"       \"{doc_preview}...\"")

    print("\n" + "-" * 70)
    print("✅ Search test completed!\n")


def main():
    """메인 함수"""
    parser = argparse.ArgumentParser(
        description="Vector Database Initialization for Unwoldam Tarot",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python init_vector_db.py                     # Initialize if not exists
  python init_vector_db.py --force-reindex     # Force reindex all cards
  python init_vector_db.py --stats             # Show statistics only
  python init_vector_db.py --test-search       # Test vector search
  python init_vector_db.py --all               # Index + Stats + Test
        """
    )

    parser.add_argument(
        '--force-reindex',
        action='store_true',
        help='Force reindexing (delete existing data)'
    )
    parser.add_argument(
        '--stats',
        action='store_true',
        help='Show statistics only'
    )
    parser.add_argument(
        '--test-search',
        action='store_true',
        help='Test vector search'
    )
    parser.add_argument(
        '--all',
        action='store_true',
        help='Run full pipeline: index + stats + test'
    )

    args = parser.parse_args()

    # 배너 출력
    print_banner()

    # 종속성 확인
    if not check_dependencies():
        print("\n❌ Dependency check failed. Please fix the issues above.\n")
        sys.exit(1)

    try:
        # --all 플래그: 전체 파이프라인 실행
        if args.all:
            index_cards(force_reindex=True)
            show_statistics()
            test_search()

        # --stats 플래그: 통계만 출력
        elif args.stats:
            show_statistics()

        # --test-search 플래그: 검색 테스트만
        elif args.test_search:
            # 인덱스가 없으면 먼저 생성
            stats = vector_store.get_statistics()
            if stats.get("total_documents", 0) == 0:
                print("⚠️  벡터 DB가 비어있습니다. 먼저 인덱싱을 실행합니다.\n")
                index_cards(force_reindex=False)
            test_search()

        # 기본 동작: 인덱싱 (force_reindex 옵션 적용)
        else:
            index_cards(force_reindex=args.force_reindex)
            show_statistics()

        print("\n" + "=" * 70)
        print("✅ All operations completed successfully!")
        print("=" * 70 + "\n")

    except KeyboardInterrupt:
        print("\n\n⚠️  Operation cancelled by user\n")
        sys.exit(1)
    except Exception as e:
        print(f"\n\n❌ Error occurred: {e}\n")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
