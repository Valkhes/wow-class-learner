# WoW Class Learner

A FastAPI server that scrapes World of Warcraft class guides from WoWhead and stores them in a vector database for intelligent search and retrieval. Built with Clean Architecture and designed for RAG (Retrieval-Augmented Generation) applications.

## Goal

Create an intelligent system that can:
- Scrape WoW class guides from WoWhead
- Store guides in a vector database with semantic search
- Answer questions about WoW classes using RAG
- Provide up-to-date information from official guides

## Quick Start

### Prerequisites
```bash
# Install uv (if not already installed)
curl -LsSf https://astral.sh/uv/install.sh | sh

# Set up Google API key for LLM features (optional)
export GOOGLE_API_KEY="your-api-key-here"
```

### Setup and Run
```bash
# Clone and navigate to project
cd wow-class-learner

# Install dependencies
uv sync

# Start the server
uv run python main.py
```

The server will start on `http://localhost:8000` with automatic database setup.

### Test the System
```bash
# Scrape and store a guide
curl -X POST "http://localhost:8000/api/v1/embedding/store_guide" \
  -H "Content-Type: application/json" \
  -d '{"class_name": "warrior", "spec_name": "fury", "guide_type": "overview-pve-dps"}'

# Search guides
curl "http://localhost:8000/api/v1/embedding/search?query=fury warrior rotation&limit=3"

# Ask LLM questions (requires GOOGLE_API_KEY)
curl -X POST "http://localhost:8000/api/v1/llm/ask" \
  -H "Content-Type: application/json" \
  -d '{"question": "What is the basic rotation for Fury Warrior?"}'

# View API docs
open http://localhost:8000/docs
```

### Run Tests
```bash
# Run embedding database tests
uv run python test/test_embedding_database.py

# Run scraper tests
uv run python test/test_scraper.py

# Run LLM integration tests (requires GOOGLE_API_KEY)
uv run python test/test_llm_integration.py
```

## Project Structure

```
wow-class-learner/
├── entities/          # Domain entities (scraper)
├── business/          # Business logic services
│   ├── scraper_service.py
│   ├── guide_service.py
│   └── llm_service.py
├── connector/         # Database connectors
├── router/           # API endpoints
│   ├── guide_router.py
│   ├── guide_handler.py
│   ├── llm_router.py
│   └── llm_handler.py
├── pkg/              # Server components
├── conf/             # Configuration files
├── test/             # Test files
├── data/             # Scraped data (gitignored)
├── chroma_db/        # Vector database (gitignored)
└── main.py           # Entry point
```

## API Endpoints

### Guide Management
- `POST /api/v1/embedding/store_guide` - Store a guide in the database
- `GET /api/v1/embedding/search` - Search guides with semantic search
- `GET /api/v1/embedding/stats` - Get database statistics

### LLM Features (requires GOOGLE_API_KEY)
- `POST /api/v1/llm/ask` - Ask questions using RAG
- `GET /api/v1/llm/status` - Get LLM service status
- `POST /api/v1/llm/test` - Test LLM connection
- `GET /api/v1/llm/health` - LLM health check

Built with Clean Architecture principles for maintainability and extensibility.
