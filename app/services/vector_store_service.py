"""
Vector Store Service
ChromaDB를 사용한 벡터 데이터베이스 서비스
타로카드 데이터의 임베딩 저장 및 검색
"""

from typing import List, Dict, Any, Optional, Tuple
import logging
import chromadb
from chromadb.config import Settings
from chromadb.errors import InvalidCollectionException
from pathlib import Path
from app.services.embedding_service import embedding_service
from app.services.rag_service import rag_service
from app.models.tarot_card import TarotCard
from app.config import settings as app_settings

logger = logging.getLogger(__name__)


class VectorStoreService:
    """ChromaDB를 사용한 벡터 저장소 서비스"""

    def __init__(self):
        """벡터 저장소 초기화"""
        self.client = None
        self.collection = None
        self.collection_name = "tarot_cards"
        self._initialize_chroma()

    def _initialize_chroma(self):
        """ChromaDB 클라이언트 초기화"""
        try:
            # 저장 경로 생성
            persist_path = Path(app_settings.VECTOR_STORE_PATH)
            persist_path.mkdir(parents=True, exist_ok=True)

            # ChromaDB 클라이언트 생성
            self.client = chromadb.PersistentClient(
                path=str(persist_path),
                settings=Settings(
                    anonymized_telemetry=False,
                    allow_reset=True
                )
            )

            # 컬렉션 가져오기 또는 생성
            try:
                self.collection = self.client.get_collection(
                    name=self.collection_name
                )
                logger.info(f"Loaded existing collection: {self.collection_name}")
            except (InvalidCollectionException, ValueError):
                # Collection doesn't exist, create new one
                self.collection = self.client.create_collection(
                    name=self.collection_name,
                    metadata={"description": "Tarot card meanings and interpretations"}
                )
                logger.info(f"Created new collection: {self.collection_name}")

        except Exception as e:
            logger.error(f"ChromaDB initialization failed: {e}", exc_info=True)
            self.collection = None

    def _prepare_card_documents(self, card: TarotCard) -> List[Dict[str, Any]]:
        """
        타로카드를 여러 문서로 분할하여 준비

        각 카드를:
        - 기본 정보 문서
        - 연애/관계 문서
        - 재물/사업 문서
        - 건강/기타 문서
        로 분할하여 더 정확한 검색 가능
        """
        documents = []

        # 1. 기본 정보 문서
        base_doc = {
            "id": f"{card.id}_base",
            "text": f"""
{card.name} ({card.name_ko})

이미지 설명:
{card.image_description}

키워드: {', '.join(card.keywords[:15])}

상징:
{card.symbolism[:500] if card.symbolism else ''}

수비학:
{card.numerology[:300] if card.numerology else ''}

분위기: {card.mood}
            """.strip(),
            "metadata": {
                "card_id": card.id,
                "card_name": card.name,
                "card_name_ko": card.name_ko,
                "suit": card.suit.value,
                "doc_type": "base",
                "keywords": ','.join(card.keywords[:10])
            }
        }
        documents.append(base_doc)

        # 2. 연애/관계 문서
        if card.love or card.relationship:
            love_doc = {
                "id": f"{card.id}_love",
                "text": f"""
{card.name} ({card.name_ko}) - 연애와 관계

연애:
{card.love}

인간관계:
{card.relationship}

재회:
{card.reunion}

조언: {card.advice[:200] if card.advice else ''}
                """.strip(),
                "metadata": {
                    "card_id": card.id,
                    "card_name": card.name,
                    "card_name_ko": card.name_ko,
                    "suit": card.suit.value,
                    "doc_type": "love",
                    "context": "연애,관계,사랑,재회"
                }
            }
            documents.append(love_doc)

        # 3. 재물/사업 문서
        if card.finance or card.education_career_business:
            finance_doc = {
                "id": f"{card.id}_finance",
                "text": f"""
{card.name} ({card.name_ko}) - 재물과 사업

재물:
{card.finance}

직업/학업/사업:
{card.education_career_business}

계약:
{card.contract}

이직:
{card.job_change}

조언: {card.advice[:200] if card.advice else ''}
                """.strip(),
                "metadata": {
                    "card_id": card.id,
                    "card_name": card.name,
                    "card_name_ko": card.name_ko,
                    "suit": card.suit.value,
                    "doc_type": "finance",
                    "context": "재물,돈,사업,직업,이직,계약"
                }
            }
            documents.append(finance_doc)

        # 4. 건강/기타 문서
        if card.health or card.travel_moving:
            other_doc = {
                "id": f"{card.id}_other",
                "text": f"""
{card.name} ({card.name_ko}) - 건강과 기타

건강:
{card.health}

여행/이사:
{card.travel_moving}

장소: {card.places}

주의사항: {card.caution[:200] if card.caution else ''}
                """.strip(),
                "metadata": {
                    "card_id": card.id,
                    "card_name": card.name,
                    "card_name_ko": card.name_ko,
                    "suit": card.suit.value,
                    "doc_type": "other",
                    "context": "건강,여행,이사,장소"
                }
            }
            documents.append(other_doc)

        return documents

    def index_all_cards(self, force_reindex: bool = False):
        """
        모든 타로카드를 벡터 DB에 인덱싱

        Args:
            force_reindex: True일 경우 기존 데이터 삭제 후 재인덱싱
        """
        if not self.collection:
            logger.error("Collection not initialized")
            return

        if not embedding_service.is_available():
            logger.error("Embedding service not available")
            return

        # 기존 데이터 확인
        existing_count = self.collection.count()
        if existing_count > 0 and not force_reindex:
            logger.info(f"Already indexed {existing_count} documents")
            return

        # 기존 데이터 삭제 (재인덱싱 시)
        if force_reindex and existing_count > 0:
            logger.info(f"Deleting existing {existing_count} documents for reindexing...")
            self.client.delete_collection(self.collection_name)
            self.collection = self.client.create_collection(
                name=self.collection_name,
                metadata={"description": "Tarot card meanings and interpretations"}
            )

        # 모든 카드 가져오기
        all_cards = rag_service.get_all_cards()
        logger.info(f"Starting indexing of {len(all_cards)} tarot cards...")

        all_documents = []
        all_ids = []
        all_texts = []
        all_metadatas = []

        # 각 카드를 여러 문서로 분할
        for card in all_cards:
            docs = self._prepare_card_documents(card)
            for doc in docs:
                all_documents.append(doc)
                all_ids.append(doc["id"])
                all_texts.append(doc["text"])
                all_metadatas.append(doc["metadata"])

        logger.info(f"Generated {len(all_documents)} documents")
        logger.info(f"Creating embeddings (dimension: {embedding_service.get_dimension()})...")

        try:
            # 배치로 임베딩 생성
            batch_size = 10
            for i in range(0, len(all_texts), batch_size):
                batch_end = min(i + batch_size, len(all_texts))
                batch_ids = all_ids[i:batch_end]
                batch_texts = all_texts[i:batch_end]
                batch_metadatas = all_metadatas[i:batch_end]

                # 임베딩 생성
                embeddings = embedding_service.embed_batch(batch_texts)

                # ChromaDB에 추가
                self.collection.add(
                    ids=batch_ids,
                    documents=batch_texts,
                    embeddings=embeddings,
                    metadatas=batch_metadatas
                )

                logger.debug(f"Indexed {batch_end}/{len(all_texts)} documents")

            logger.info(f"Indexing completed! Total: {len(all_documents)} documents")

        except Exception as e:
            logger.error(f"Indexing failed: {e}", exc_info=True)

    def search(
        self,
        query: str,
        context_type: Optional[str] = None,
        n_results: int = 5,
        filter_cards: Optional[List[int]] = None
    ) -> List[Dict[str, Any]]:
        """
        시맨틱 검색 수행

        Args:
            query: 검색 쿼리
            context_type: 컨텍스트 유형 (love, finance, other 등)
            n_results: 반환할 결과 개수
            filter_cards: 특정 카드 ID로 필터링

        Returns:
            검색 결과 리스트
        """
        if not self.collection:
            logger.error("Collection not initialized")
            return []

        if not embedding_service.is_available():
            logger.error("Embedding service not available")
            return []

        try:
            # 쿼리 임베딩 생성
            query_embedding = embedding_service.embed(query)

            # 필터 구성
            where_filter = None
            if context_type:
                where_filter = {"doc_type": context_type}

            if filter_cards:
                # 특정 카드로 필터링
                if where_filter:
                    where_filter = {
                        "$and": [
                            where_filter,
                            {"card_id": {"$in": filter_cards}}
                        ]
                    }
                else:
                    where_filter = {"card_id": {"$in": filter_cards}}

            # 검색 수행
            results = self.collection.query(
                query_embeddings=[query_embedding],
                n_results=n_results,
                where=where_filter,
                include=["documents", "metadatas", "distances"]
            )

            # 결과 포맷팅
            formatted_results = []
            if results['ids'] and len(results['ids']) > 0:
                for i in range(len(results['ids'][0])):
                    formatted_results.append({
                        "id": results['ids'][0][i],
                        "document": results['documents'][0][i],
                        "metadata": results['metadatas'][0][i],
                        "distance": results['distances'][0][i],
                        "similarity": 1 - results['distances'][0][i]  # 유사도 점수
                    })

            return formatted_results

        except Exception as e:
            logger.error(f"Search failed: {e}", exc_info=True)
            return []

    def get_context_for_cards(
        self,
        card_ids: List[int],
        question: str,
        context_type: Optional[str] = None,
        n_similar: int = 3
    ) -> str:
        """
        선택된 카드들과 질문을 기반으로 컨텍스트 생성

        Args:
            card_ids: 선택된 카드 ID 리스트
            question: 사용자 질문
            context_type: 상담 유형 (love, finance 등)
            n_similar: 추가로 검색할 유사 해석 개수

        Returns:
            LLM에 제공할 컨텍스트 문자열
        """
        context = "=" * 60 + "\n"
        context += "타로 리딩 컨텍스트\n"
        context += "=" * 60 + "\n\n"

        # 1. 사용자 질문
        context += f"📋 질문: {question}\n"
        if context_type:
            context += f"📂 상담 유형: {context_type}\n"
        context += "\n"

        # 2. 선택된 카드들의 정보
        context += "🎴 선택된 카드들:\n"
        context += "-" * 60 + "\n"

        for i, card_id in enumerate(card_ids, 1):
            card = rag_service.get_card_by_id(card_id)
            if card:
                context += f"\n{i}. {card.name} ({card.name_ko})\n"
                context += f"   키워드: {', '.join(card.keywords[:5])}\n"

                # 컨텍스트 유형별 의미 추가
                if context_type == "love":
                    context += f"   연애: {card.love[:150]}...\n"
                elif context_type == "finance":
                    context += f"   재물: {card.finance[:150]}...\n"
                elif context_type == "career":
                    context += f"   직업: {card.education_career_business[:150]}...\n"
                else:
                    context += f"   설명: {card.image_description[:150]}...\n"

        context += "\n"

        # 3. 유사한 해석 사례 검색 (RAG)
        if n_similar > 0:
            context += "💡 관련 해석 가이드:\n"
            context += "-" * 60 + "\n"

            # 질문 + 카드 정보로 검색
            search_query = f"{question} "
            for card_id in card_ids:
                card = rag_service.get_card_by_id(card_id)
                if card:
                    search_query += f"{card.name} "

            # 선택된 카드 외의 유사 해석 검색
            similar_docs = self.search(
                query=search_query,
                context_type=context_type,
                n_results=n_similar
            )

            for i, doc in enumerate(similar_docs, 1):
                if doc['similarity'] > 0.7:  # 유사도 임계값
                    context += f"\n{i}. [{doc['metadata']['card_name_ko']}] "
                    context += f"(유사도: {doc['similarity']:.2f})\n"
                    context += f"   {doc['document'][:200]}...\n"

        context += "\n" + "=" * 60 + "\n"

        return context

    def get_statistics(self) -> Dict[str, Any]:
        """벡터 저장소 통계 정보"""
        if not self.collection:
            return {"status": "not_initialized"}

        try:
            count = self.collection.count()
            return {
                "status": "ready",
                "total_documents": count,
                "embedding_dimension": embedding_service.get_dimension(),
                "embedding_provider": embedding_service.provider_name,
                "collection_name": self.collection_name
            }
        except Exception as e:
            return {
                "status": "error",
                "error": str(e)
            }


# 싱글톤 인스턴스
vector_store = VectorStoreService()
