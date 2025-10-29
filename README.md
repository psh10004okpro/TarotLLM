# Unwoldam Tarot LLM API

AI-powered Tarot Card Reading API with multiple LLM providers and diverse tarot master personas.

## Features

- **Multiple LLM Providers**: Support for Claude, ChatGPT, and Gemini
- **Tarot Master Personas**: 3 unique personas with different reading styles
  - 현자 (The Wise Oracle): Compassionate spiritual guide
  - 실용가 (The Practical Guide): Direct and solution-focused
  - 신비가 (The Mystic Seer): Mysterious and intuitive prophet
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

### Phase 3: Session & Memory
- [ ] Database integration
- [ ] Persistent session storage
- [ ] Conversation history
- [ ] User preferences

### Phase 4: TTS/STT
- [ ] Text-to-Speech integration
- [ ] Speech-to-Text integration
- [ ] Voice-based readings

### Phase 5: Advanced Features
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
