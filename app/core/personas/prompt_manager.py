"""
타로마스터 프롬프트 관리 시스템
압축/상세 프롬프트를 상황에 맞게 선택하는 2단계 시스템
"""

from typing import Dict, Optional
from enum import Enum

from .prompt_definitions import (
    MASTER_1_SHORT, MASTER_1_DETAILED,
    MASTER_2_SHORT, MASTER_2_DETAILED,
    MASTER_3_SHORT, MASTER_3_DETAILED
)


class PromptLevel(Enum):
    """프롬프트 레벨"""
    SHORT = "short"          # 압축 버전만
    DETAILED = "detailed"    # 압축 + 상세 버전
    FULL = "full"           # 모든 정보 포함 (향후 확장용)


class TarotMasterPrompts:
    """타로마스터 프롬프트 관리 클래스"""

    # 압축 버전 (항상 사용)
    SHORT_PROMPTS = {
        "master_1": MASTER_1_SHORT,
        "master_2": MASTER_2_SHORT,
        "master_3": MASTER_3_SHORT
    }

    # 상세 버전 (필요시 추가)
    DETAILED_PROMPTS = {
        "master_1": MASTER_1_DETAILED,
        "master_2": MASTER_2_DETAILED,
        "master_3": MASTER_3_DETAILED
    }

    @staticmethod
    def get_prompt(
        master_id: str,
        level: PromptLevel = PromptLevel.SHORT,
        context: Optional[Dict] = None
    ) -> str:
        """
        타로마스터 프롬프트 가져오기

        Args:
            master_id: 타로마스터 ID (master_1, master_2, master_3)
            level: 프롬프트 레벨 (SHORT, DETAILED, FULL)
            context: 변수 치환용 컨텍스트

        Returns:
            포맷된 시스템 프롬프트

        Example:
            >>> context = {
            ...     "meeting_count": 1,
            ...     "user_name": "민수",
            ...     "interpret_reversed": True
            ... }
            >>> prompt = TarotMasterPrompts.get_prompt(
            ...     "master_1",
            ...     PromptLevel.SHORT,
            ...     context
            ... )
        """
        if context is None:
            context = {}

        # 기본값 설정
        context.setdefault("meeting_count", 1)
        context.setdefault("user_name", "내담자")
        context.setdefault("interpret_reversed", True)

        # 기본 압축 버전
        prompt = TarotMasterPrompts.SHORT_PROMPTS.get(master_id, "")

        # 레벨에 따라 상세 버전 추가
        if level in [PromptLevel.DETAILED, PromptLevel.FULL]:
            detailed = TarotMasterPrompts.DETAILED_PROMPTS.get(master_id, "")
            prompt = f"{prompt}\n\n{detailed}"

        # 변수 치환
        try:
            prompt = prompt.format(**context)
        except KeyError as e:
            # 누락된 변수가 있어도 계속 진행
            pass

        return prompt

    @staticmethod
    def should_use_detailed(
        is_first_message: bool = False,
        message_count: int = 0,
        complexity: str = "normal",
        card_count: int = 1,
        has_specific_context: bool = False
    ) -> PromptLevel:
        """
        상황에 따라 프롬프트 레벨 결정

        Args:
            is_first_message: 세션의 첫 메시지인지
            message_count: 현재까지 메시지 수
            complexity: 질문 복잡도 (simple, normal, complex)
            card_count: 뽑은 카드 개수 (많을수록 복잡)
            has_specific_context: 특정 컨텍스트 요청 (연애, 재물 등)

        Returns:
            사용할 프롬프트 레벨

        Logic:
            - 첫 메시지: 상세 버전 (페르소나 확립)
            - 복잡한 질문: 상세 버전
            - 5장 이상 카드: 상세 버전 (켈틱 크로스 등)
            - 특정 컨텍스트: 상세 버전
            - 그 외: 압축 버전 (토큰 절약)
        """
        # 첫 메시지는 상세 버전 사용 (페르소나 확립)
        if is_first_message:
            return PromptLevel.DETAILED

        # 복잡한 질문은 상세 버전
        if complexity == "complex":
            return PromptLevel.DETAILED

        # 5장 이상 카드는 상세 버전 (복잡한 스프레드)
        if card_count >= 5:
            return PromptLevel.DETAILED

        # 특정 컨텍스트 요청시 상세 버전
        if has_specific_context:
            return PromptLevel.DETAILED

        # 그 외에는 압축 버전 (토큰 절약)
        return PromptLevel.SHORT

    @staticmethod
    def assess_complexity(concern: str) -> str:
        """
        질문 복잡도 평가

        Args:
            concern: 사용자의 고민/질문

        Returns:
            복잡도 레벨 (simple, normal, complex)
        """
        # 단어 수 기반 평가
        word_count = len(concern.split())

        # 복잡도를 높이는 키워드
        complex_keywords = [
            "관계", "직장", "이직", "결혼", "이혼", "사업",
            "투자", "건강", "가족", "갈등", "선택", "결정"
        ]

        # 키워드 매칭
        keyword_matches = sum(1 for keyword in complex_keywords if keyword in concern)

        # 복잡도 판단
        if word_count < 10 and keyword_matches == 0:
            return "simple"
        elif word_count < 30 and keyword_matches <= 1:
            return "normal"
        else:
            return "complex"

    @staticmethod
    def estimate_tokens(prompt: str) -> int:
        """
        프롬프트의 대략적인 토큰 수 추정

        Args:
            prompt: 프롬프트 텍스트

        Returns:
            추정 토큰 수

        Note:
            한글은 대략 1.5 토큰/단어, 영어는 1.3 토큰/단어
        """
        # 간단한 추정: 공백 기준 단어 수 * 1.5
        word_count = len(prompt.split())
        estimated_tokens = int(word_count * 1.5)

        return estimated_tokens

    @staticmethod
    def get_all_masters_info() -> Dict[str, Dict]:
        """
        모든 타로마스터의 기본 정보 반환

        Returns:
            타로마스터 정보 딕셔너리
        """
        return {
            "master_1": {
                "name": "달빛의 현자",
                "name_en": "Sage of Moonlight",
                "style": "philosophical, psychological, profound",
                "llm_provider": "claude",
                "supports_reversed": True
            },
            "master_2": {
                "name": "별빛의 안내자",
                "name_en": "Starlight Guide",
                "style": "warm, empathetic, encouraging, practical",
                "llm_provider": "openai",
                "supports_reversed": False
            },
            "master_3": {
                "name": "운명의 해석자",
                "name_en": "Destiny Interpreter",
                "style": "intuitive, mystical, poetic, storytelling",
                "llm_provider": "gemini",
                "supports_reversed": True  # configurable
            }
        }


# 편의 함수들
def get_master_prompt(
    master_id: str,
    meeting_count: int = 1,
    user_name: str = "내담자",
    is_first_message: bool = False,
    complexity: str = "normal",
    **kwargs
) -> tuple[str, PromptLevel]:
    """
    타로마스터 프롬프트를 가져오는 편의 함수

    Args:
        master_id: 타로마스터 ID
        meeting_count: 만남 횟수
        user_name: 사용자 이름
        is_first_message: 첫 메시지 여부
        complexity: 질문 복잡도
        **kwargs: 추가 컨텍스트

    Returns:
        (프롬프트, 사용된 레벨) 튜플
    """
    # 프롬프트 레벨 결정
    level = TarotMasterPrompts.should_use_detailed(
        is_first_message=is_first_message,
        message_count=meeting_count,
        complexity=complexity,
        card_count=kwargs.get("card_count", 1),
        has_specific_context=kwargs.get("has_specific_context", False)
    )

    # 컨텍스트 준비
    context = {
        "meeting_count": meeting_count,
        "user_name": user_name,
        "interpret_reversed": kwargs.get("interpret_reversed", True)
    }
    context.update(kwargs)

    # 프롬프트 생성
    prompt = TarotMasterPrompts.get_prompt(
        master_id=master_id,
        level=level,
        context=context
    )

    return prompt, level


def assess_question(concern: str, cards: list) -> Dict[str, any]:
    """
    질문과 카드를 분석하여 프롬프트 전략 결정

    Args:
        concern: 사용자의 고민/질문
        cards: 선택된 카드 리스트

    Returns:
        분석 결과 딕셔너리
    """
    complexity = TarotMasterPrompts.assess_complexity(concern)
    card_count = len(cards)

    # 특정 컨텍스트 감지
    context_keywords = {
        "love": ["연애", "사랑", "연인", "결혼", "이별", "재회"],
        "finance": ["돈", "재물", "투자", "사업", "수입", "재정"],
        "career": ["직장", "일", "이직", "승진", "업무", "커리어"],
        "health": ["건강", "병", "치료", "몸", "마음"]
    }

    detected_context = None
    for context_type, keywords in context_keywords.items():
        if any(keyword in concern for keyword in keywords):
            detected_context = context_type
            break

    return {
        "complexity": complexity,
        "card_count": card_count,
        "has_specific_context": detected_context is not None,
        "context_type": detected_context,
        "recommended_level": TarotMasterPrompts.should_use_detailed(
            complexity=complexity,
            card_count=card_count,
            has_specific_context=detected_context is not None
        )
    }
