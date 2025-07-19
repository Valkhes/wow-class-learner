# Test Folder

This folder contains all test files for the WoW Class Learner project.

## Test Files

- `test_embedding_database.py` - Tests for embedding database functionality
- `test_scraper.py` - Tests for scraper and integration functionality
- `test_llm_integration.py` - Tests for LLM integration with Gemini 2.0 Flash

## Running Tests

```bash
# Run embedding database tests
uv run python test/test_embedding_database.py

# Run scraper tests
uv run python test/test_scraper.py

# Run LLM integration tests
uv run python test/test_llm_integration.py
```

## Test Coverage

### Embedding Database Tests
- Database setup and initialization
- GuideService with EmbeddingConnector
- Embedding generation
- Guide storage and retrieval
- Search functionality

### Scraper Tests
- Server setup with all layers
- ScraperService functionality
- GuideService functionality
- GuideHandler functionality
- Complete integration testing

### LLM Integration Tests
- LLM service setup with Gemini 2.0 Flash
- LLM handler functionality
- Server integration with LLM components
- RAG (Retrieval-Augmented Generation) testing
- Question answering with source attribution

## Prerequisites for LLM Tests

To run LLM integration tests, you need:

1. **Google API Key**: Set the `GOOGLE_API_KEY` environment variable
   ```bash
   export GOOGLE_API_KEY="your-api-key-here"
   ```

2. **Scraped Guides**: Have some guides in the embedding database
   ```bash
   # Scrape guides first
   curl -X POST "http://localhost:8000/api/v1/scrape_all_guides" \
     -H "Content-Type: application/json" \
     -d '{"save_to_file": true, "store_in_embedding_db": true}'
   ```

## Notes

- Tests use the same Clean Architecture structure as the main application
- All tests are designed to run independently
- Tests create their own database instances for isolation
- Test output shows clear pass/fail status for each component
- LLM tests require external API access and may incur costs