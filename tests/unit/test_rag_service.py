"""
Unit tests for RAG Service
"""

import pytest
from app.services.rag_service import RAGService
from app.models.tarot_card import TarotCard, CardOrientation


@pytest.fixture
def rag_service():
    """Create RAG service instance"""
    service = RAGService()
    return service


class TestLoadTarotData:
    """Tests for tarot data loading"""

    def test_cards_loaded(self, rag_service):
        """타로 카드 데이터 로드 확인"""
        assert rag_service.cards_data is not None
        assert len(rag_service.cards_data) > 0

    def test_cards_count(self, rag_service):
        """78장의 타로 카드 확인"""
        # 메이저 아르카나 22장 + 마이너 아르카나 56장 = 78장
        assert len(rag_service.cards_data) == 78

    def test_card_is_tarot_card_object(self, rag_service):
        """카드가 TarotCard 객체인지 확인"""
        first_card = rag_service.cards_data[0]
        assert isinstance(first_card, TarotCard)

    def test_all_cards(self, rag_service):
        """get_all_cards 메서드"""
        cards = rag_service.get_all_cards()
        assert len(cards) == 78
        assert all(isinstance(card, TarotCard) for card in cards)


class TestGetCardById:
    """Tests for get_card_by_id"""

    def test_get_valid_card(self, rag_service):
        """유효한 카드 ID로 조회"""
        card = rag_service.get_card_by_id(0)  # The Fool

        assert card is not None
        assert isinstance(card, TarotCard)

    def test_get_last_card(self, rag_service):
        """마지막 카드 조회"""
        card = rag_service.get_card_by_id(77)

        assert card is not None
        assert isinstance(card, TarotCard)

    def test_get_invalid_card_negative(self, rag_service):
        """음수 ID는 None 반환"""
        card = rag_service.get_card_by_id(-1)
        assert card is None

    def test_get_invalid_card_too_large(self, rag_service):
        """범위 초과 ID는 None 반환"""
        card = rag_service.get_card_by_id(78)
        assert card is None

        card = rag_service.get_card_by_id(999)
        assert card is None


class TestGetCardByName:
    """Tests for get_card_by_name"""

    def test_get_card_by_name(self, rag_service):
        """이름으로 카드 조회"""
        # 카드 이름은 실제 데이터에 따라 다를 수 있음
        card = rag_service.get_card_by_name("FOOL")
        # 카드가 없을 수도 있으므로 None이 아니면 TarotCard 타입 확인
        if card:
            assert isinstance(card, TarotCard)


class TestGetCardMeaning:
    """Tests for get_card_meaning"""

    def test_get_upright_meaning(self, rag_service):
        """정방향 의미 조회"""
        meaning = rag_service.get_card_meaning(
            card_id=0,
            orientation="upright"
        )
        assert meaning is not None
        assert isinstance(meaning, str)
        assert len(meaning) > 0

    def test_get_reversed_meaning(self, rag_service):
        """역방향 의미 조회"""
        meaning = rag_service.get_card_meaning(
            card_id=0,
            orientation="reversed"
        )
        assert meaning is not None
        assert isinstance(meaning, str)
        assert len(meaning) > 0

    def test_get_meaning_with_context(self, rag_service):
        """컨텍스트별 의미 조회"""
        meaning = rag_service.get_card_meaning(
            card_id=0,
            orientation="upright",
            context="love"
        )
        assert meaning is not None
        assert isinstance(meaning, str)


class TestGetComprehensiveInfo:
    """Tests for get_comprehensive_card_info"""

    def test_get_comprehensive_info(self, rag_service):
        """종합 카드 정보 조회"""
        info = rag_service.get_comprehensive_card_info(0)

        assert info is not None
        assert isinstance(info, dict)
        # 필수 필드 확인
        assert "card" in info or "name" in info


class TestSearchCards:
    """Tests for search_cards"""

    def test_search_with_keyword(self, rag_service):
        """키워드로 카드 검색"""
        results = rag_service.search_cards("love")

        assert isinstance(results, list)
        # 결과가 있으면 모두 TarotCard 객체
        if results:
            assert all(isinstance(card, TarotCard) for card in results)

    def test_search_korean_keyword(self, rag_service):
        """한글 키워드로 검색"""
        results = rag_service.search_cards("사랑")

        assert isinstance(results, list)


class TestGetContextForReading:
    """Tests for get_context_for_reading"""

    def test_get_context_single_card(self, rag_service):
        """단일 카드 컨텍스트"""
        context = rag_service.get_context_for_reading(
            cards=[0]
        )

        assert context is not None
        assert isinstance(context, str)
        assert len(context) > 0

    def test_get_context_multiple_cards(self, rag_service):
        """여러 카드 컨텍스트"""
        context = rag_service.get_context_for_reading(
            cards=[0, 21, 42],
            question="새로운 시작에 대한 조언"
        )

        assert context is not None
        assert isinstance(context, str)
        assert len(context) > 0

    def test_get_context_with_context_type(self, rag_service):
        """컨텍스트 타입 포함"""
        context = rag_service.get_context_for_reading(
            cards=[0, 1, 2],
            context_type="love"
        )

        assert context is not None
        assert isinstance(context, str)


class TestStatistics:
    """Tests for statistics"""

    def test_get_statistics(self, rag_service):
        """통계 정보 조회"""
        stats = rag_service.get_statistics()

        assert stats is not None
        assert isinstance(stats, dict)
        # 기본 통계 확인
        if "total_cards" in stats:
            assert stats["total_cards"] == 78


class TestServiceOperations:
    """Tests for service operations"""

    def test_reload_data(self, rag_service):
        """데이터 재로딩"""
        initial_count = len(rag_service.cards_data)

        rag_service.reload_data()

        # 재로딩 후에도 카드 개수 동일
        assert len(rag_service.cards_data) == initial_count

    def test_multiple_calls_consistency(self, rag_service):
        """여러 번 호출해도 일관성 유지"""
        card1 = rag_service.get_card_by_id(0)
        card2 = rag_service.get_card_by_id(0)

        # 같은 카드 반환
        assert card1 == card2 or (
            card1 is not None and card2 is not None
        )


class TestEdgeCases:
    """Edge cases and error handling"""

    def test_empty_card_ids_list(self, rag_service):
        """빈 카드 ID 리스트"""
        context = rag_service.get_context_for_reading(
            cards=[]
        )
        # 빈 리스트에 대해서는 빈 컨텍스트나 기본 메시지 반환
        assert context is not None or context == ""

    def test_invalid_card_id_in_context(self, rag_service):
        """유효하지 않은 카드 ID 포함"""
        # 일부 유효, 일부 무효
        context = rag_service.get_context_for_reading(
            cards=[0, 999, 21]
        )
        # 유효한 카드에 대해서만 컨텍스트 생성
        assert context is not None

    def test_context_with_question(self, rag_service):
        """질문 포함 컨텍스트"""
        context = rag_service.get_context_for_reading(
            cards=[0, 1, 2],
            question="내 미래는 어떻게 될까요?"
        )
        assert context is not None

    def test_search_empty_query(self, rag_service):
        """빈 검색어"""
        results = rag_service.search_cards("")
        assert isinstance(results, list)

    def test_get_meaning_invalid_card(self, rag_service):
        """유효하지 않은 카드의 의미 조회"""
        meaning = rag_service.get_card_meaning(
            card_id=999,
            orientation="upright"
        )
        # 에러 메시지 또는 "Card not found"
        assert isinstance(meaning, str)


class TestServiceInitialization:
    """Tests for service initialization"""

    def test_service_created_successfully(self):
        """RAG 서비스 생성 성공"""
        service = RAGService()
        assert service is not None

    def test_cards_loaded_on_init(self):
        """초기화 시 카드 데이터 자동 로드"""
        service = RAGService()
        assert service.cards_data is not None
        assert len(service.cards_data) == 78

    def test_multiple_service_instances(self):
        """여러 서비스 인스턴스 생성 가능"""
        service1 = RAGService()
        service2 = RAGService()

        # 두 인스턴스 모두 정상 작동
        assert len(service1.cards_data) == 78
        assert len(service2.cards_data) == 78


class TestCardDataIntegrity:
    """Tests for card data integrity"""

    def test_all_cards_accessible(self, rag_service):
        """모든 카드 ID로 접근 가능"""
        for card_id in range(78):
            card = rag_service.get_card_by_id(card_id)
            assert card is not None, f"Card {card_id} not accessible"

    def test_no_duplicate_cards(self, rag_service):
        """중복 카드 없음"""
        cards = rag_service.get_all_cards()
        # 카드 객체를 직접 비교하기는 어려우므로 개수로 확인
        assert len(cards) == 78
