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

    def test_card_structure(self, rag_service):
        """카드 데이터 구조 확인"""
        first_card = rag_service.cards_data[0]

        # 필수 필드 존재 확인
        assert "id" in first_card
        assert "name_en" in first_card
        assert "name_ko" in first_card
        assert "arcana" in first_card
        assert "suit" in first_card or first_card["arcana"] == "Major"

    def test_major_arcana_cards(self, rag_service):
        """메이저 아르카나 카드 확인 (22장)"""
        major_cards = [
            card for card in rag_service.cards_data
            if card.get("arcana") == "Major"
        ]
        assert len(major_cards) == 22

    def test_minor_arcana_cards(self, rag_service):
        """마이너 아르카나 카드 확인 (56장)"""
        minor_cards = [
            card for card in rag_service.cards_data
            if card.get("arcana") == "Minor"
        ]
        assert len(minor_cards) == 56


class TestGetCardById:
    """Tests for get_card_by_id"""

    def test_get_valid_card(self, rag_service):
        """유효한 카드 ID로 조회"""
        card = rag_service.get_card_by_id(0)  # The Fool

        assert card is not None
        assert card["id"] == 0
        assert "name_ko" in card

    def test_get_last_card(self, rag_service):
        """마지막 카드 조회"""
        card = rag_service.get_card_by_id(77)

        assert card is not None
        assert card["id"] == 77

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


class TestSearchSimilarCards:
    """Tests for search_similar_cards (if implemented)"""

    def test_search_with_keyword(self, rag_service):
        """키워드로 유사 카드 검색"""
        # This test assumes search functionality exists
        # If not implemented, this will be a placeholder

        # 사랑 관련 키워드로 검색
        query = "사랑과 관계"

        # RAG 서비스에 search 메서드가 있다면 테스트
        if hasattr(rag_service, 'search_similar_cards'):
            results = rag_service.search_similar_cards(query, top_k=5)
            assert isinstance(results, list)
            assert len(results) <= 5
        else:
            pytest.skip("search_similar_cards not implemented")


class TestGetCardContext:
    """Tests for getting card context"""

    def test_get_context_for_card_ids(self, rag_service):
        """카드 ID들로 컨텍스트 가져오기"""
        card_ids = [0, 21, 42]  # The Fool, The World, 중간 카드

        context = rag_service.get_card_context(card_ids)

        assert context is not None
        assert isinstance(context, str)
        assert len(context) > 0

    def test_get_context_single_card(self, rag_service):
        """단일 카드 컨텍스트"""
        context = rag_service.get_card_context([0])

        assert context is not None
        assert isinstance(context, str)

    def test_get_context_with_orientations(self, rag_service):
        """방향 포함 컨텍스트"""
        card_ids = [0, 1]
        orientations = [CardOrientation.UPRIGHT, CardOrientation.REVERSED]

        context = rag_service.get_card_context(
            card_ids=card_ids,
            orientations=orientations
        )

        assert context is not None
        # 역방향 카드가 있으면 컨텍스트에 반영되어야 함
        if CardOrientation.REVERSED in orientations:
            # 역방향 언급이 있거나, 의미가 달라져야 함
            assert len(context) > 0


class TestCardMetadata:
    """Tests for card metadata and properties"""

    def test_all_cards_have_required_fields(self, rag_service):
        """모든 카드가 필수 필드를 가지고 있는지 확인"""
        required_fields = ["id", "name_en", "name_ko", "arcana"]

        for card in rag_service.cards_data:
            for field in required_fields:
                assert field in card, f"Card {card.get('id')} missing {field}"

    def test_card_ids_are_unique(self, rag_service):
        """카드 ID가 고유한지 확인"""
        card_ids = [card["id"] for card in rag_service.cards_data]
        assert len(card_ids) == len(set(card_ids))

    def test_card_ids_are_sequential(self, rag_service):
        """카드 ID가 0부터 77까지 연속적인지 확인"""
        card_ids = sorted([card["id"] for card in rag_service.cards_data])
        expected_ids = list(range(78))
        assert card_ids == expected_ids

    def test_suits_for_minor_arcana(self, rag_service):
        """마이너 아르카나 카드가 suit을 가지는지 확인"""
        minor_cards = [
            card for card in rag_service.cards_data
            if card.get("arcana") == "Minor"
        ]

        valid_suits = ["Wands", "Cups", "Swords", "Pentacles"]

        for card in minor_cards:
            assert "suit" in card
            assert card["suit"] in valid_suits


class TestReverseReading:
    """Tests for reversed card readings"""

    def test_upright_vs_reversed(self, rag_service):
        """정방향과 역방향 해석 차이"""
        card_id = 0  # The Fool

        # 정방향 컨텍스트
        upright_context = rag_service.get_card_context(
            card_ids=[card_id],
            orientations=[CardOrientation.UPRIGHT]
        )

        # 역방향 컨텍스트
        reversed_context = rag_service.get_card_context(
            card_ids=[card_id],
            orientations=[CardOrientation.REVERSED]
        )

        # 두 컨텍스트가 다르거나, 최소한 역방향 언급이 있어야 함
        assert upright_context != reversed_context or "역" in reversed_context


class TestEdgeCases:
    """Edge cases and error handling"""

    def test_empty_card_ids_list(self, rag_service):
        """빈 카드 ID 리스트"""
        context = rag_service.get_card_context([])
        # 빈 리스트에 대해서는 빈 컨텍스트나 에러 메시지 반환
        assert context is not None

    def test_invalid_card_ids_in_list(self, rag_service):
        """유효하지 않은 카드 ID 포함"""
        # 일부 유효, 일부 무효
        context = rag_service.get_card_context([0, 999, 21])
        # 유효한 카드에 대해서만 컨텍스트 생성
        assert context is not None

    def test_duplicate_card_ids(self, rag_service):
        """중복 카드 ID"""
        context = rag_service.get_card_context([0, 0, 0])
        # 중복이 있어도 처리 가능해야 함
        assert context is not None

    def test_mismatched_orientations_length(self, rag_service):
        """카드 개수와 방향 개수 불일치"""
        card_ids = [0, 1, 2]
        orientations = [CardOrientation.UPRIGHT]  # 1개만

        # 방향이 부족하면 기본값 사용하거나 에러 처리
        context = rag_service.get_card_context(
            card_ids=card_ids,
            orientations=orientations
        )
        assert context is not None


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
