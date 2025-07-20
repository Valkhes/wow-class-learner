# WoW Class Learner

A comprehensive World of Warcraft class learning application with RAG (Retrieval-Augmented Generation) capabilities, powered by LiteLLM gateway for cost monitoring, caching, and guardrails.

## 🚀 Features

- **RAG-powered Q&A**: Ask questions about WoW classes and get accurate answers based on official guides
- **LiteLLM Gateway**: Cost monitoring, rate limiting, caching, and Prometheus metrics
- **Guide Scraping**: Automated scraping of WoWhead class guides
- **Embedding Database**: Vector search for relevant guide content
- **Async Support**: High-performance async API endpoints
- **Monitoring**: Comprehensive metrics and health checks

## 🏗️ Architecture

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   FastAPI App   │    │  LiteLLM Gateway│    │  Google Gemini  │
│                 │    │                 │    │                 │
│ • Guide Router  │───▶│ • Cost Monitoring│───▶│ • LLM Provider  │
│ • LiteLLM Router│    │ • Rate Limiting │    │ • Model Access   │
│ • Health Checks │    │ • Caching       │    │ • API Keys      │
└─────────────────┘    │ • Metrics       │    └─────────────────┘
                       └─────────────────┘
                                │
                       ┌─────────────────┐
                       │ Embedding DB    │
                       │                 │
                       │ • Vector Search │
                       │ • Guide Storage │
                       └─────────────────┘
```

## 📋 Prerequisites

- Python 3.11+
- Google API Key for Gemini
- Redis (optional, for production caching)

## 🛠️ Installation

1. **Clone the repository**:
   ```bash
   git clone <repository-url>
   cd wow-class-learner
   ```

2. **Install dependencies**:
   ```bash
   uv sync
   ```

3. **Set environment variables**:
   ```bash
   export GOOGLE_API_KEY="your-google-api-key"
   export LLM_DAILY_COST_LIMIT="10.0"
   export LLM_MONTHLY_COST_LIMIT="100.0"
   ```

4. **Start the server**:
   ```bash
   python main.py
   ```

## 🔧 Configuration

### Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `GOOGLE_API_KEY` | Required | Google API key for Gemini |
| `LLM_DAILY_COST_LIMIT` | `10.0` | Daily cost limit in USD |
| `LLM_MONTHLY_COST_LIMIT` | `100.0` | Monthly cost limit in USD |
| `LLM_RATE_LIMIT_RPM` | `60` | Requests per minute |
| `LLM_RATE_LIMIT_RPH` | `1000` | Requests per hour |
| `LLM_CACHE_TYPE` | `memory` | Cache type (memory/redis) |
| `REDIS_URL` | Optional | Redis URL for caching |
| `ENABLE_PROMETHEUS` | `true` | Enable Prometheus metrics |

### Configuration File

```python
from conf.litellm_config import LiteLLMConfig

# Print current configuration
LiteLLMConfig.print_config()

# Validate configuration
if not LiteLLMConfig.validate_config():
    print("Configuration validation failed")
```

## 📚 API Endpoints

### LiteLLM Gateway

#### Ask Questions
```http
POST /api/v1/litellm/ask
Content-Type: application/json

{
  "question": "What is the best rotation for Fury Warrior?"
}
```

#### Sync Question Asking
```http
POST /api/v1/litellm/ask-sync
Content-Type: application/json

{
  "question": "What is the best rotation for Fury Warrior?"
}
```

#### Service Status
```http
GET /api/v1/litellm/status
```

#### Test Connection
```http
GET /api/v1/litellm/test
```

#### Cost Summary
```http
GET /api/v1/litellm/cost-summary
```

#### Performance Metrics
```http
GET /api/v1/litellm/performance
```

#### Prometheus Metrics
```http
GET /api/v1/litellm/metrics
```

#### Health Check
```http
GET /api/v1/litellm/health
```

### Guide Management

#### Get All Classes
```http
GET /api/v1/guides/classes
```

#### Get Class Guides
```http
GET /api/v1/guides/class/{class_name}
```

#### Scrape Guides
```http
POST /api/v1/guides/scrape
```

## 📊 Response Format

### Question Response
```json
{
  "success": true,
  "answer": "The basic rotation for Fury Warrior...",
  "error": null,
  "sources": [
    {
      "class_name": "Warrior",
      "spec_name": "Fury",
      "similarity_score": 0.95,
      "url": "https://wowhead.com/...",
      "content_preview": "Fury Warrior rotation..."
    }
  ],
  "metadata": {
    "duration": 1.23,
    "tokens_used": 1500,
    "cost_usd": 0.00045,
    "model": "gemini/gemini-2.0-flash-exp",
    "cache_hit": false
  }
}
```

## 🧪 Testing

### Run Integration Tests
```bash
python test/test_litellm_integration.py
```

### Run Examples
```bash
python examples/litellm_example.py
```

## 📈 Monitoring

### Prometheus Metrics
The application exposes Prometheus metrics at `/api/v1/litellm/metrics`:

- `llm_requests_total`: Total LLM requests by model and status
- `llm_request_duration_seconds`: Request duration histogram
- `llm_tokens_used`: Total tokens used by model and type
- `llm_cost_usd`: Total cost in USD by model
- `llm_cache_hits`: Cache hits by model
- `llm_cache_misses`: Cache misses by model

### Grafana Dashboard
You can create a Grafana dashboard using these metrics to monitor:
- Request volume and success rates
- Response times and performance
- Token usage and costs
- Cache hit rates
- Error rates

## 💰 Cost Monitoring

### Cost Estimation
The system estimates costs based on token usage:
- Input tokens: $0.000075 per 1K tokens
- Output tokens: $0.0003 per 1K tokens

### Cost Limits
- Daily limit: $10.0 (configurable)
- Monthly limit: $100.0 (configurable)

When limits are exceeded, requests are rejected with an error.

## 🔒 Guardrails

### Rate Limiting
- Requests per minute: 60 (configurable)
- Requests per hour: 1000 (configurable)

### Input Validation
- Question cannot be empty
- Maximum question length (configurable)
- Content filtering (can be extended)

### Error Handling
- Graceful degradation on API failures
- Detailed error messages
- Retry logic for transient failures

## 🚀 Performance

### Caching
- **In-Memory Cache**: Fastest option, cache lost on restart
- **Redis Cache**: Persistent across restarts, shared across instances

### Async Support
- High-performance async endpoints
- Concurrent request handling
- Non-blocking operations

## 🔧 Development

### Project Structure
```
wow-class-learner/
├── business/           # Business logic layer
│   ├── litellm_service.py
│   ├── monitoring_service.py
│   ├── guide_service.py
│   └── scraper_service.py
├── router/            # API routing layer
│   ├── litellm_router.py
│   ├── litellm_handler.py
│   └── guide_router.py
├── connector/         # Data access layer
│   └── embedding_connector.py
├── conf/             # Configuration
│   └── litellm_config.py
├── test/             # Tests
├── examples/         # Examples
└── main.py           # Application entry point
```

### Adding New Features
1. Add business logic in `business/`
2. Create handlers in `router/`
3. Add endpoints in router files
4. Update tests and examples

## 🚨 Troubleshooting

### Common Issues

1. **API Key Not Set**
   ```
   Error: GOOGLE_API_KEY environment variable not set
   ```
   Solution: Set the `GOOGLE_API_KEY` environment variable

2. **Rate Limit Exceeded**
   ```
   Error: Rate limit exceeded
   ```
   Solution: Wait or increase rate limits in configuration

3. **Cost Limit Exceeded**
   ```
   Error: Cost limit exceeded
   ```
   Solution: Increase cost limits or wait for reset

### Debug Mode
Enable verbose logging:
```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

## 📄 License

This project is licensed under the MIT License.

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Submit a pull request

## 📞 Support

For support and questions:
1. Check the configuration with `LiteLLMConfig.print_config()`
2. Run the integration tests: `python test/test_litellm_integration.py`
3. Check the logs for detailed error messages
4. Verify environment variables are set correctly
