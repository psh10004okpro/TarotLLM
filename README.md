# Unwoldam Tarot LLM API

AI-powered Tarot Card Reading API with multiple LLM providers and diverse tarot master personas.

## Features

- **Multiple LLM Providers**: Support for Claude, ChatGPT, and Gemini
- **Tarot Master Personas**: 3 unique personas with interaction-based relationships
  - 달빛의 현자 (Sage of Moonlight): Philosophical & psychological insights (Claude)
  - 별빛의 안내자 (Starlight Guide): Warm, empathetic & practical advice (ChatGPT)
  - 운명의 해석자 (Destiny Interpreter): Intuitive, mystical & creative storytelling (Gemini)
- **Comprehensive Tarot Database**: Complete 78-card deck with Korean interpretations
- **RAG System**: Context-aware retrieval with love, finance, career, and health meanings
- **Session Management**: Track user interactions and build relationships
- **Multiple Spread Types**: Single card, three-card, Celtic Cross, and more
- **RESTful API**: FastAPI-based with automatic API documentation

## Project Structure

```
unwoldam-api/
├── app/
│   ├── main.py                 # FastAPI application entry point
│   ├── config.py               # Configuration and settings
│   ├── models/                 # Pydantic data models
│   │   ├── tarot_card.py
│   │   ├── reading.py
│   │   └── user_session.py
│   ├── services/               # Business logic
│   │   ├── llm_service.py
│   │   ├── rag_service.py
│   │   ├── tarot_master_service.py
│   │   └── session_service.py
│   ├── api/v1/                 # API endpoints
│   │   ├── tarot_reading.py
│   │   └── tarot_master.py
│   ├── core/
│   │   ├── llm_providers/      # LLM provider implementations
│   │   │   ├── base.py
│   │   │   ├── claude_provider.py
│   │   │   ├── openai_provider.py
│   │   │   └── gemini_provider.py
│   │   └── personas/           # Tarot master personas
│   │       ├── tarot_master_1.py
│   │       ├── tarot_master_2.py
│   │       └── tarot_master_3.py
│   └── data/                   # Tarot card data
│       ├── tarot_cards.json
│       └── card_meanings.json
├── requirements.txt
├── .env.example
└── README.md
```

## Installation

1. Clone the repository:
```bash
git clone <repository-url>
cd TarotLLM
```

2. Create a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Set up environment variables:
```bash
cp .env.example .env
# Edit .env and add your API keys
```

## Configuration

Edit the `.env` file with your API keys and preferences:

```env
# LLM Provider API Keys
ANTHROPIC_API_KEY=your_anthropic_api_key_here
OPENAI_API_KEY=your_openai_api_key_here
GOOGLE_API_KEY=your_google_api_key_here

# Default LLM Provider
DEFAULT_LLM_PROVIDER=claude
```

## Usage

1. Start the server:
```bash
python -m app.main
# Or using uvicorn directly:
uvicorn app.main:app --reload
```

2. Access the API documentation:
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## API Endpoints

### Tarot Reading

- `POST /api/v1/reading` - Create a new tarot reading
- `GET /api/v1/reading/{reading_id}` - Get reading by ID
- `GET /api/v1/reading/user/{user_id}/history` - Get user's reading history
- `GET /api/v1/spreads` - List available spread types

### Tarot Master & Sessions

- `GET /api/v1/masters` - List available tarot master personas
- `GET /api/v1/masters/{master_id}` - Get tarot master details
- `POST /api/v1/session` - Create user session
- `GET /api/v1/session/{session_id}` - Get session details
- `GET /api/v1/session/user/{user_id}/history` - Get user's session history
- `DELETE /api/v1/session/{session_id}` - Close session

## Example Usage

### Create a Tarot Reading

```bash
curl -X POST "http://localhost:8000/api/v1/reading" \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": "user_12345",
    "question": "What should I focus on in my career?",
    "spread_type": "three_card",
    "llm_provider": "claude",
    "tarot_master_id": 1
  }'
```

### List Tarot Masters

```bash
curl "http://localhost:8000/api/v1/masters"
```

## LLM Provider Configuration

The API supports multiple LLM providers that can be easily switched via configuration.

### Supported Providers

- **Claude** (Anthropic): `claude-sonnet-4-5-20250929`
- **GPT-4** (OpenAI): `gpt-4-turbo`
- **Gemini** (Google): `gemini-pro`

### Quick Start

1. **Set up API keys** in `.env`:
```bash
ANTHROPIC_API_KEY=your_key_here
OPENAI_API_KEY=your_key_here
GOOGLE_API_KEY=your_key_here

# Choose default provider
DEFAULT_LLM_PROVIDER=claude
```

2. **Use in code**:
```python
from app.services.llm_service import llm_service

# Use default provider
response = await llm_service.generate_response(
    prompt="Interpret this tarot card",
    system_prompt="You are a tarot master"
)

# Or specify provider
response = await llm_service.generate_response(
    prompt="Interpret this tarot card",
    provider_name="claude"  # or "openai", "gemini"
)
```

### Advanced Usage

See [LLM Provider Guide (Korean)](docs/LLM_PROVIDER_GUIDE_KR.md) for:
- Streaming responses
- RAG integration
- Provider fallback
- Error handling
- Performance optimization

## RAG System

The API includes a powerful RAG (Retrieval-Augmented Generation) system using ChromaDB for semantic search of tarot card meanings.

### Features

- **Vector Search**: ChromaDB-based semantic search
- **Embedding Support**: OpenAI or local sentence-transformers
- **Context-Aware**: Search by love, finance, career, health contexts
- **312 Documents**: 78 cards × 4 document types
- **Intelligent Matching**: Finds relevant card interpretations

### Quick Example

```python
from app.services.vector_store_service import vector_store
from app.services.rag_service import rag_service

# Index all cards (first time only)
vector_store.index_all_cards()

# Semantic search
results = vector_store.search(
    query="Will I find new love?",
    context_type="love",
    n_results=5
)

# Get RAG-enhanced context
context = rag_service.get_context_for_reading(
    cards=[0, 6, 19],  # The Fool, The Lovers, The Sun
    question="Will I find new love?",
    context_type="love",
    use_vector_search=True  # Enable RAG!
)
```

### Setup

```bash
# Install dependencies
pip install chromadb sentence-transformers

# Configure in .env
VECTOR_STORE_PATH=./data/vector_store
EMBEDDING_MODEL=text-embedding-3-small
```

See [RAG System Guide (Korean)](docs/RAG_SYSTEM_GUIDE_KR.md) for detailed documentation.

## Tarot Master Persona System

The API features 3 distinct tarot master personas with interaction-based relationship building.

### Three Unique Personas

#### 1. 달빛의 현자 (Sage of Moonlight)
- **Style**: Philosophical, psychological, profound
- **Recommended LLM**: Claude
- **Approach**: Deep analytical insights, Jungian psychology, explores conscious & unconscious
- **Reversed Cards**: ✓ Supported (interprets both upright and reversed)

#### 2. 별빛의 안내자 (Starlight Guide)
- **Style**: Warm, empathetic, encouraging, practical
- **Recommended LLM**: ChatGPT
- **Approach**: Supportive guidance, practical advice, positive energy, emotional comfort
- **Reversed Cards**: ✗ Upright only (focuses on positive perspectives)

#### 3. 운명의 해석자 (Destiny Interpreter)
- **Style**: Intuitive, mystical, poetic, storytelling
- **Recommended LLM**: Gemini
- **Approach**: Creative narratives, card connections, metaphorical language, cosmic perspective
- **Reversed Cards**: ⚙️ Configurable (can be enabled or disabled)

### Interaction-Based Relationships

Each persona evolves their speech patterns and relationship style based on meeting count:

| Meeting # | Relationship | Speech Style | Intimacy |
|-----------|--------------|--------------|----------|
| **1st (0)** | First meeting | Formal, respectful | Professional |
| **2-5th** | Trust building | Friendly honorifics | Warm |
| **6-10th** | Deep bond | Casual honorifics, uses name | Close friend |
| **11+** | Soul companion | May use informal speech | Deep intimacy |

### Quick Example

```python
from app.core.personas.tarot_master_1 import TarotMaster1

# Initialize persona
master = TarotMaster1()

# First meeting (formal)
greeting = master.get_greeting(interaction_count=0, user_name="민수")
# "안녕하세요, 민수님. 저는 '달빛의 현자'입니다..."

# 7th meeting (friendly)
greeting = master.get_greeting(interaction_count=6, user_name="민수")
# "민수님, 또 뵙게 되어 기쁩니다. 7번째 만남이네요..."

# Generate context-aware system prompt
system_prompt = master.get_system_prompt(
    interaction_count=6,
    user_name="민수"
)

# Use with LLM
response = await llm_service.generate(
    prompt=user_question,
    system_prompt=system_prompt,
    provider_name=master.recommended_llm  # "claude"
)
```

See [Persona System Guide (Korean)](docs/PERSONA_SYSTEM_GUIDE_KR.md) for detailed documentation.

## Development Roadmap

### Phase 1: Core Setup ✅
- [x] Project structure
- [x] Basic models and services
- [x] LLM provider integration
- [x] Tarot master personas
- [x] API endpoints

### Phase 2: Data & RAG ✅
- [x] Complete 78-card tarot deck data (22 Major + 56 Minor Arcana)
- [x] Comprehensive Korean tarot database with detailed interpretations
- [x] Context-specific meanings (love, finance, career, health, etc.)
- [x] Enhanced RAG service with search and filtering
- [x] Symbolism, numerology, and guidance for each card
- [ ] Vector database integration (future)
- [ ] Advanced semantic search (future)
- [ ] Card relationship analysis (future)

### Phase 3: LLM Provider Abstraction ✅
- [x] Abstract base class for LLM providers
- [x] Claude provider (claude-sonnet-4-5-20250929)
- [x] OpenAI provider (gpt-4-turbo)
- [x] Gemini provider (gemini-pro)
- [x] Easy provider switching via configuration
- [x] Streaming response support
- [x] Comprehensive Korean documentation
- [x] Provider fallback mechanism support

### Phase 4: RAG System ✅
- [x] ChromaDB vector database integration
- [x] Embedding service (OpenAI + local models)
- [x] 312-document indexing (78 cards × 4 contexts)
- [x] Semantic search functionality
- [x] Context-aware retrieval (love, finance, career, health)
- [x] RAG-enhanced context generation
- [x] Card filtering and similarity search
- [x] Comprehensive Korean documentation

### Phase 5: Tarot Master Persona System ✅
- [x] 3 distinct tarot master personas with unique characteristics
- [x] 달빛의 현자 (Sage of Moonlight): Philosophical & psychological insights
- [x] 별빛의 안내자 (Starlight Guide): Warm, empathetic & practical advice
- [x] 운명의 해석자 (Destiny Interpreter): Intuitive, mystical & creative storytelling
- [x] Interaction-based relationship system (4 tiers: 0, 1-4, 5-9, 10+ meetings)
- [x] Progressive speech pattern evolution with interaction count
- [x] LLM provider recommendations per persona
- [x] Configurable reversed card interpretation
- [x] Comprehensive Korean documentation

### Phase 6: Session & Memory
- [ ] Database integration
- [ ] Persistent session storage
- [ ] Conversation history
- [ ] User preferences

### Phase 7: TTS/STT
- [ ] Text-to-Speech integration
- [ ] Speech-to-Text integration
- [ ] Voice-based readings

### Phase 8: Advanced Features
- [ ] Custom spread builder
- [ ] Reading insights and analytics
- [ ] Multi-language support
- [ ] Mobile app integration

## Technologies

- **Framework**: FastAPI
- **LLM Providers**: Anthropic Claude, OpenAI GPT, Google Gemini
- **Data Validation**: Pydantic
- **Async**: asyncio, aiofiles
- **Testing**: pytest

## License

[Add your license here]

## Contributing

[Add contribution guidelines here]

## Contact

[Add contact information here]
