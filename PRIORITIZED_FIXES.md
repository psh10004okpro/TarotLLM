# TarotLLM - Prioritized Fix List

## IMMEDIATE FIXES REQUIRED (Before Any Deploy)

These 3 CRITICAL bugs will cause runtime failures:

### 1. Fix API method call (tarot_reading.py:128)
**File:** `app/api/v1/tarot_reading.py`
**Change:** 
```python
# Before:
interpretation = await llm_service.generate(...)

# After:
interpretation = await llm_service.generate_response(...)
```

### 2. Fix session service method name (tarot_master_service.py:193)
**File:** `app/services/tarot_master_service.py`
**Change:**
```python
# Before:
await session_service.update_interaction(session.session_id)

# After:
await session_service.increment_interaction(session.session_id)
```

### 3. Fix type error in persona_id (tarot_master_service.py:265)
**File:** `app/services/tarot_master_service.py`
**Change:**
```python
# Before:
"interpret_reversed": getattr(persona_id, 'supports_reversed', True)

# After:
"interpret_reversed": TAROT_MASTERS.get(f"master_{persona_id}", {}).get("interpret_reversed", True)
```

---

## HIGH PRIORITY FIXES (Week 1)

### 4. Add timeout handling to all LLM provider calls
**Files:**
- `app/core/llm_providers/claude_provider.py` (lines 69, 111)
- `app/core/llm_providers/openai_provider.py` (lines 69, 110)
- `app/core/llm_providers/gemini_provider.py` (lines 78, 125)

**Example for Claude:**
```python
import asyncio

response = await asyncio.wait_for(
    self.client.messages.create(...),
    timeout=30.0
)
```

### 5. Fix all bare except clauses
**Files and lines:**
- `app/main.py:132`
- `app/models/tarot_card.py:87, 102, 113`
- `app/services/rag_service.py:236`
- `app/services/vector_store_service.py:49`

**Pattern:**
```python
# Before:
except:
    pass

# After:
except Exception as e:
    logger.error(f"Error message: {e}", exc_info=True)
```

### 6. Replace all print() with proper logging
**Files affected:**
- `app/core/llm_providers/claude_provider.py`
- `app/core/llm_providers/openai_provider.py`
- `app/core/llm_providers/gemini_provider.py`
- `app/services/embedding_service.py`
- `app/services/vector_store_service.py`
- `app/services/rag_service.py`

**Pattern:**
```python
import logging
logger = logging.getLogger(__name__)

# Before:
print("Message")

# After:
logger.info("Message")
logger.warning("Warning message")
logger.error("Error message")
```

### 7. Fix hardcoded Redis connection
**File:** `app/services/session_service.py:39-42`

```python
import os

self.redis_client = redis.Redis(
    host=os.getenv('REDIS_HOST', 'localhost'),
    port=int(os.getenv('REDIS_PORT', 6379)),
    db=int(os.getenv('REDIS_DB', 0)),
    decode_responses=True,
    socket_connect_timeout=int(os.getenv('REDIS_TIMEOUT', 1))
)
```

### 8. Add JSON error handling
**File:** `app/services/session_service.py` (lines 82, 111, 252, 341, 529)

```python
import json
import logging
logger = logging.getLogger(__name__)

try:
    session_data = json.loads(data)
except json.JSONDecodeError as e:
    logger.error(f"Failed to parse session data: {e}")
    session_data = {}
```

### 9. Add retry logic to LLM calls
**Install:** Add `tenacity==8.2.3` to `requirements.txt`

**Pattern:**
```python
from tenacity import retry, stop_after_attempt, wait_exponential

@retry(
    stop=stop_after_attempt(3),
    wait=wait_exponential(multiplier=1, min=4, max=10)
)
async def generate(self, prompt, system_prompt, **kwargs):
    # Implementation
```

---

## MEDIUM PRIORITY (Week 2)

### 10. Add resource cleanup to lifespan
**File:** `app/main.py:24-65`

```python
@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Starting up...")
    # ... existing startup code ...
    
    yield
    
    # Shutdown code
    logger.info("Shutting down...")
    if session_service.redis_client:
        session_service.redis_client.close()
    logger.info("Shutdown complete")
```

### 11. Add input validation
**File:** `app/models/reading.py`

```python
from pydantic import Field, validator

class ReadingRequest(BaseModel):
    user_id: str = Field(..., min_length=1, max_length=100)
    concern: Optional[str] = Field(None, min_length=1, max_length=500)
    
    @validator('user_id', 'concern')
    def not_empty_whitespace(cls, v):
        if v and len(v.strip()) == 0:
            raise ValueError('Cannot be empty whitespace')
        return v
```

### 12. Fix type annotations
**File:** `app/core/personas/prompt_manager.py:275`

```python
from typing import Dict, Any, List
from app.models.tarot_card import DrawnCard

def assess_question(concern: str, cards: List[DrawnCard]) -> Dict[str, Any]:
    # Implementation
```

### 13. Hide internal errors from clients
**File:** `app/api/v1/tarot_reading.py:174-178`

```python
except Exception as e:
    logger.error(f"Reading generation failed: {str(e)}", exc_info=True)
    raise HTTPException(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        detail="Failed to generate reading. Please try again later."
    )
```

### 14. Add spread type validation
**File:** `app/services/tarot_master_service.py:61-69`

```python
spread_config = {
    SpreadType.SINGLE_CARD: 1,
    SpreadType.THREE_CARD: 3,
    SpreadType.CELTIC_CROSS: 10,
    SpreadType.RELATIONSHIP: 5,
    SpreadType.CAREER: 5,
    SpreadType.CUSTOM: 3
}

if spread_type not in spread_config:
    raise ValueError(f"Invalid spread type: {spread_type}")

num_cards = spread_config[spread_type]
```

---

## LOW PRIORITY (Week 3+)

### 15. Add exception documentation
Add to docstrings in `app/services/llm_service.py`

### 16. Extract magic numbers as constants
**File:** `app/services/session_service.py`

```python
MAX_READING_HISTORY = 100
REDIS_EXPIRY_DAYS = 90
```

### 17. Convert manual tests to pytest
Create proper pytest test suite with fixtures

### 18. Add API key validation at startup
**File:** `app/config.py`

### 19. Add logging integration tests
Verify all logging works properly in CI/CD

---

## Implementation Checklist

- [ ] Apply all 3 CRITICAL fixes
- [ ] Add timeout handling (30+ seconds)
- [ ] Replace all bare except clauses
- [ ] Replace all print() with logging
- [ ] Fix Redis hardcoding
- [ ] Add JSON error handling
- [ ] Add retry logic with tenacity
- [ ] Test all APIs endpoint-to-end
- [ ] Verify no more AttributeError
- [ ] Add resource cleanup
- [ ] Add input validation
- [ ] Fix type annotations
- [ ] Hide error messages from clients
- [ ] Add spread type validation
- [ ] Run full test suite
- [ ] Update documentation

---

## Testing Strategy

After fixes, test these flows:

1. **Basic Reading Flow**
   - User creates session
   - Requests tarot reading with 3-card spread
   - Verifies reading is generated
   - Checks meeting count increments

2. **Error Scenarios**
   - No API keys configured
   - Redis unavailable
   - Invalid card IDs
   - Timeout on API calls
   - Corrupted Redis data

3. **Edge Cases**
   - Very long concern text (>500 chars)
   - Empty concern
   - Multiple rapid requests
   - All 3 tarot masters
   - All spread types

---

## Deployment Checklist

Before deploying to production:

- [ ] All CRITICAL fixes applied and tested
- [ ] All HIGH priority fixes applied
- [ ] Environment variables configured
- [ ] Redis configured and accessible
- [ ] All 3 LLM API keys configured
- [ ] Logging properly configured
- [ ] Error messages non-leaking
- [ ] Timeout values appropriate
- [ ] Retry logic tested
- [ ] Resource cleanup verified
- [ ] Load tested under expected traffic
- [ ] Monitoring/alerting configured

