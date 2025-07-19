# Test Folder

This folder contains all test files for the WoW Class Learner project.

## Test Files

- `test_embedding_database.py` - Tests for embedding database functionality
- `test_scraper.py` - Tests for scraper and integration functionality

## Running Tests

```bash
# Run embedding database tests
uv run python test/test_embedding_database.py

# Run scraper tests
uv run python test/test_scraper.py
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