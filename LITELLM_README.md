# LiteLLM Gateway for WoW Class Learner

This document explains how to use the LiteLLM gateway for cost monitoring, guardrails, and caching in the WoW Class Learner application.

## Features

- **Cost Monitoring**: Track token usage and costs in real-time
- **Guardrails**: Rate limiting and cost limits to prevent overspending
- **Caching**: In-memory or Redis-based caching for improved performance
- **Prometheus Metrics**: Detailed metrics for monitoring and alerting
- **Async Support**: Both synchronous and asynchronous API endpoints

## Setup

### 1. Install Dependencies

The LiteLLM dependencies have been added to `pyproject.toml`. Install them with:

```bash
uv sync
```

### 2. Environment Variables

Set the following environment variables:

```bash
# Required
export GOOGLE_API_KEY="your-google-api-key"

# Optional - Cost Limits (USD)
export LLM_DAILY_COST_LIMIT="10.0"
export LLM_MONTHLY_COST_LIMIT="100.0"

# Optional - Rate Limits
export LLM_RATE_LIMIT_RPM="60"  # Requests per minute
export LLM_RATE_LIMIT_RPH="1000"  # Requests per hour

# Optional - Caching
export LLM_CACHE_TYPE="memory"  # or "redis"
export REDIS_URL="redis://localhost:6379"  # if using Redis
export REDIS_PASSWORD="your-redis-password"  # if using Redis

# Optional - Model Configuration
export LLM_MODEL="gemini/gemini-2.0-flash-exp"
export LLM_TEMPERATURE="0.1"
export LLM_MAX_TOKENS="2048"

# Optional - Monitoring
export ENABLE_PROMETHEUS="true"
export METRICS_PORT="9090"

# Optional - Cost Estimation (USD per 1K tokens)
export LLM_INPUT_COST_PER_1K="0.000075"
export LLM_OUTPUT_COST_PER_1K="0.0003"
```

### 3. Start the Server

```bash
python main.py
```

## API Endpoints

### LiteLLM Endpoints

#### Ask a Question (Async)
```http
POST /api/v1/litellm/ask
Content-Type: application/json

{
  "question": "What is the best rotation for Fury Warrior?"
}
```

#### Ask a Question (Sync)
```http
POST /api/v1/litellm/ask-sync
Content-Type: application/json

{
  "question": "What is the best rotation for Fury Warrior?"
}
```

#### Get Service Status
```http
GET /api/v1/litellm/status
```

#### Test Connection
```http
GET /api/v1/litellm/test
```

#### Get Cost Summary
```http
GET /api/v1/litellm/cost-summary
```

#### Get Performance Metrics
```http
GET /api/v1/litellm/performance
```

### Monitoring Endpoints

#### Prometheus Metrics
```http
GET /api/v1/litellm/metrics
```

#### Usage Summary
```http
GET /api/v1/litellm/usage-summary
```

#### Cost Analysis
```http
GET /api/v1/litellm/cost-analysis
```

#### Health Status
```http
GET /api/v1/litellm/health
```

## Response Format

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

### Status Response
```json
{
  "success": true,
  "litellm_service": {
    "model": "gemini/gemini-2.0-flash-exp",
    "provider": "Google (via LiteLLM)",
    "initialized": true,
    "embedding_connector_ready": true,
    "cache_enabled": true,
    "cost_limits": {
      "daily_limit": 10.0,
      "monthly_limit": 100.0
    },
    "rate_limits": {
      "requests_per_minute": 60,
      "requests_per_hour": 1000
    }
  },
  "ready": true,
  "features": {
    "caching": true,
    "cost_monitoring": true,
    "rate_limiting": true,
    "prometheus_metrics": true
  }
}
```

## Monitoring

### Prometheus Metrics

The following metrics are available:

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

## Caching

### In-Memory Cache (Default)
- Fastest option
- Cache is lost on server restart
- Good for development and testing

### Redis Cache
- Persistent across server restarts
- Can be shared across multiple instances
- Better for production environments

To enable Redis caching:

1. Install Redis:
```bash
# macOS
brew install redis

# Ubuntu
sudo apt-get install redis-server
```

2. Set environment variables:
```bash
export LLM_CACHE_TYPE="redis"
export REDIS_URL="redis://localhost:6379"
```

## Cost Monitoring

### Cost Estimation
The system estimates costs based on token usage:
- Input tokens: $0.000075 per 1K tokens
- Output tokens: $0.0003 per 1K tokens

### Cost Limits
- Daily limit: $10.0 (configurable)
- Monthly limit: $100.0 (configurable)

When limits are exceeded, requests are rejected with an error.

## Rate Limiting

### Limits
- Requests per minute: 60 (configurable)
- Requests per hour: 1000 (configurable)

### Implementation
Currently uses a simplified in-memory rate limiter. For production, consider:
- Redis-based rate limiting for distributed systems
- Database-backed rate limiting for persistence

## Guardrails

### Input Validation
- Question cannot be empty
- Maximum question length (configurable)
- Content filtering (can be extended)

### Output Validation
- Response length limits
- Content safety checks (can be extended)

### Error Handling
- Graceful degradation on API failures
- Detailed error messages
- Retry logic for transient failures

## Configuration

### Configuration File
Use `conf/litellm_config.py` to manage settings:

```python
from conf.litellm_config import LiteLLMConfig

# Print current configuration
LiteLLMConfig.print_config()

# Validate configuration
if not LiteLLMConfig.validate_config():
    print("Configuration validation failed")
```

### Environment Variables Reference

| Variable | Default | Description |
|----------|---------|-------------|
| `GOOGLE_API_KEY` | Required | Google API key for Gemini |
| `LLM_MODEL` | `gemini/gemini-2.0-flash-exp` | Model to use |
| `LLM_TEMPERATURE` | `0.1` | Model temperature |
| `LLM_MAX_TOKENS` | `2048` | Maximum tokens per response |
| `LLM_CACHE_TYPE` | `memory` | Cache type (memory/redis) |
| `LLM_DAILY_COST_LIMIT` | `10.0` | Daily cost limit in USD |
| `LLM_MONTHLY_COST_LIMIT` | `100.0` | Monthly cost limit in USD |
| `LLM_RATE_LIMIT_RPM` | `60` | Requests per minute |
| `LLM_RATE_LIMIT_RPH` | `1000` | Requests per hour |
| `ENABLE_PROMETHEUS` | `true` | Enable Prometheus metrics |
| `METRICS_PORT` | `9090` | Prometheus metrics port |

## Troubleshooting

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

4. **Redis Connection Failed**
   ```
   Error: Redis connection failed
   ```
   Solution: Check Redis server status and connection settings

### Debug Mode

Enable verbose logging:

```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

### Health Checks

Use the health endpoint to check service status:

```bash
curl http://localhost:8000/api/v1/litellm/health
```

## Performance Tips

1. **Use Caching**: Enable Redis caching for better performance
2. **Monitor Metrics**: Use Prometheus metrics to identify bottlenecks
3. **Optimize Prompts**: Shorter, more focused prompts use fewer tokens
4. **Batch Requests**: Consider batching similar questions
5. **Set Appropriate Limits**: Balance cost control with user experience

## Security Considerations

1. **API Key Security**: Store API keys securely, never commit to version control
2. **Rate Limiting**: Implement appropriate rate limits to prevent abuse
3. **Input Validation**: Validate all user inputs
4. **Error Handling**: Don't expose sensitive information in error messages
5. **Monitoring**: Monitor for unusual usage patterns

## Future Enhancements

- [ ] Database-backed cost tracking
- [ ] Advanced rate limiting with Redis
- [ ] Content filtering and safety checks
- [ ] Multi-model support
- [ ] A/B testing capabilities
- [ ] Advanced caching strategies
- [ ] Cost optimization recommendations 