"""
Embedding Service
텍스트를 벡터로 변환하는 서비스
OpenAI embedding 또는 로컬 모델 지원
"""

from typing import List, Optional
from abc import ABC, abstractmethod
import logging
from app.config import settings

logger = logging.getLogger(__name__)


class BaseEmbeddingProvider(ABC):
    """임베딩 프로바이더 기본 클래스"""

    @abstractmethod
    def embed_text(self, text: str) -> List[float]:
        """단일 텍스트를 임베딩"""
        pass

    @abstractmethod
    def embed_texts(self, texts: List[str]) -> List[List[float]]:
        """여러 텍스트를 배치로 임베딩"""
        pass

    @abstractmethod
    def get_dimension(self) -> int:
        """임베딩 차원 반환"""
        pass


class OpenAIEmbedding(BaseEmbeddingProvider):
    """OpenAI 임베딩 프로바이더"""

    def __init__(self, model: str = "text-embedding-3-small"):
        self.model = model
        self.client = None
        self._initialize_client()

    def _initialize_client(self):
        """OpenAI 클라이언트 초기화"""
        if settings.OPENAI_API_KEY:
            try:
                from openai import OpenAI
                self.client = OpenAI(api_key=settings.OPENAI_API_KEY)
                logger.info(f"OpenAI embedding client initialized with model: {self.model}")
            except ImportError:
                logger.warning("openai package not installed")
            except Exception as e:
                logger.error(f"OpenAI client initialization failed: {e}", exc_info=True)

    def embed_text(self, text: str) -> List[float]:
        """단일 텍스트를 임베딩"""
        if not self.client:
            raise RuntimeError("OpenAI 클라이언트를 사용할 수 없습니다")

        response = self.client.embeddings.create(
            model=self.model,
            input=text
        )
        return response.data[0].embedding

    def embed_texts(self, texts: List[str]) -> List[List[float]]:
        """여러 텍스트를 배치로 임베딩"""
        if not self.client:
            raise RuntimeError("OpenAI 클라이언트를 사용할 수 없습니다")

        response = self.client.embeddings.create(
            model=self.model,
            input=texts
        )
        return [item.embedding for item in response.data]

    def get_dimension(self) -> int:
        """임베딩 차원 반환"""
        # text-embedding-3-small: 1536 dimensions
        # text-embedding-3-large: 3072 dimensions
        if "large" in self.model:
            return 3072
        return 1536

    def is_available(self) -> bool:
        """사용 가능 여부 확인"""
        return self.client is not None


class LocalEmbedding(BaseEmbeddingProvider):
    """로컬 임베딩 프로바이더 (sentence-transformers 사용)"""

    def __init__(self, model_name: str = "sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2"):
        self.model_name = model_name
        self.model = None
        self._initialize_model()

    def _initialize_model(self):
        """로컬 모델 초기화"""
        try:
            from sentence_transformers import SentenceTransformer
            self.model = SentenceTransformer(self.model_name)
            logger.info(f"Local embedding model loaded: {self.model_name}")
        except ImportError:
            logger.warning("sentence-transformers package not installed. Run: pip install sentence-transformers")
        except Exception as e:
            logger.error(f"Local model initialization failed: {e}", exc_info=True)

    def embed_text(self, text: str) -> List[float]:
        """단일 텍스트를 임베딩"""
        if not self.model:
            raise RuntimeError("로컬 모델을 사용할 수 없습니다")

        embedding = self.model.encode(text, convert_to_numpy=True)
        return embedding.tolist()

    def embed_texts(self, texts: List[str]) -> List[List[float]]:
        """여러 텍스트를 배치로 임베딩"""
        if not self.model:
            raise RuntimeError("로컬 모델을 사용할 수 없습니다")

        embeddings = self.model.encode(texts, convert_to_numpy=True)
        return embeddings.tolist()

    def get_dimension(self) -> int:
        """임베딩 차원 반환"""
        if not self.model:
            return 384  # 기본 MiniLM 차원

        # 모델에서 실제 차원 가져오기
        return self.model.get_sentence_embedding_dimension()

    def is_available(self) -> bool:
        """사용 가능 여부 확인"""
        return self.model is not None


class EmbeddingService:
    """임베딩 서비스 통합 클래스"""

    def __init__(self, provider: str = "openai"):
        """
        임베딩 서비스 초기화

        Args:
            provider: "openai" 또는 "local"
        """
        self.provider_name = provider
        self.provider: Optional[BaseEmbeddingProvider] = None
        self._initialize_provider()

    def _initialize_provider(self):
        """프로바이더 초기화"""
        if self.provider_name == "openai":
            self.provider = OpenAIEmbedding(model=settings.EMBEDDING_MODEL)
        elif self.provider_name == "local":
            self.provider = LocalEmbedding()
        else:
            raise ValueError(f"알 수 없는 프로바이더: {self.provider_name}")

        if not self.provider.is_available():
            logger.warning(f"{self.provider_name} provider not available")
            # Fallback to local
            if self.provider_name == "openai":
                logger.info("Attempting fallback to local embedding model...")
                self.provider_name = "local"
                self.provider = LocalEmbedding()

    def embed(self, text: str) -> List[float]:
        """텍스트를 임베딩 벡터로 변환"""
        if not self.provider or not self.provider.is_available():
            raise RuntimeError("임베딩 프로바이더를 사용할 수 없습니다")

        return self.provider.embed_text(text)

    def embed_batch(self, texts: List[str]) -> List[List[float]]:
        """여러 텍스트를 배치로 임베딩"""
        if not self.provider or not self.provider.is_available():
            raise RuntimeError("임베딩 프로바이더를 사용할 수 없습니다")

        return self.provider.embed_texts(texts)

    def get_dimension(self) -> int:
        """임베딩 차원 반환"""
        if not self.provider:
            return 0
        return self.provider.get_dimension()

    def is_available(self) -> bool:
        """서비스 사용 가능 여부"""
        return self.provider is not None and self.provider.is_available()


# 싱글톤 인스턴스
embedding_service = EmbeddingService(provider="local")  # 기본: 로컬 모델
