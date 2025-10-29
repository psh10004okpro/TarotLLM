"""
Security utilities for input validation and sanitization
"""

import re
from typing import Optional


def sanitize_llm_prompt(text: Optional[str], max_length: int = 2000) -> str:
    """
    Sanitize user input before sending to LLM to prevent prompt injection

    Args:
        text: User input text
        max_length: Maximum allowed length

    Returns:
        Sanitized text safe for LLM processing
    """
    if not text:
        return ""

    # Trim to max length
    text = text[:max_length]

    # Remove potential code block markers that could break out of context
    text = text.replace("```", "")
    text = text.replace("~~~", "")

    # Remove system-like prompts
    dangerous_patterns = [
        r"(?i)ignore\s+(previous|above|all)\s+(instructions?|prompts?)",
        r"(?i)you\s+are\s+(now|a)\s+",
        r"(?i)system\s*:",
        r"(?i)assistant\s*:",
        r"(?i)forget\s+(everything|all)",
    ]

    for pattern in dangerous_patterns:
        text = re.sub(pattern, "[filtered]", text)

    # Trim whitespace
    text = text.strip()

    return text


def validate_card_id(card_id: int) -> bool:
    """
    Validate that card ID is within valid range

    Args:
        card_id: Card ID to validate

    Returns:
        True if valid, False otherwise
    """
    return 0 <= card_id <= 77  # 78 tarot cards (0-77)


def sanitize_user_name(name: Optional[str]) -> str:
    """
    Sanitize user name for display

    Args:
        name: User name

    Returns:
        Sanitized name
    """
    if not name:
        return "내담자"

    # Remove special characters, keep only alphanumeric and Korean
    name = re.sub(r'[^\w\s가-힣]', '', name, flags=re.UNICODE)
    name = name.strip()

    # Limit length
    name = name[:50]

    return name if name else "내담자"
