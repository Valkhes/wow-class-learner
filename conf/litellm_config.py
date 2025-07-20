import os
from typing import Dict, Any, Optional

class LiteLLMConfig:
    """Configuration for LiteLLM gateway settings"""
    
    # API Keys
    GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
    
    # Model Configuration
    MODEL_NAME = os.getenv("LLM_MODEL", "gemini/gemini-2.0-flash-exp")
    TEMPERATURE = float(os.getenv("LLM_TEMPERATURE", "0.1"))
    MAX_TOKENS = int(os.getenv("LLM_MAX_TOKENS", "2048"))
    
    # Caching Configuration
    REDIS_URL = os.getenv("REDIS_URL")
    REDIS_PASSWORD = os.getenv("REDIS_PASSWORD")
    CACHE_TYPE = os.getenv("LLM_CACHE_TYPE", "memory")  # memory or redis
    
    # Cost Limits (USD)
    DAILY_COST_LIMIT = float(os.getenv("LLM_DAILY_COST_LIMIT", "10.0"))
    MONTHLY_COST_LIMIT = float(os.getenv("LLM_MONTHLY_COST_LIMIT", "100.0"))
    
    # Rate Limits
    REQUESTS_PER_MINUTE = int(os.getenv("LLM_RATE_LIMIT_RPM", "60"))
    REQUESTS_PER_HOUR = int(os.getenv("LLM_RATE_LIMIT_RPH", "1000"))
    
    # Monitoring Configuration
    ENABLE_PROMETHEUS = os.getenv("ENABLE_PROMETHEUS", "true").lower() == "true"
    METRICS_PORT = int(os.getenv("METRICS_PORT", "9090"))
    
    # Cost Estimation (USD per 1K tokens)
    INPUT_COST_PER_1K = float(os.getenv("LLM_INPUT_COST_PER_1K", "0.000075"))
    OUTPUT_COST_PER_1K = float(os.getenv("LLM_OUTPUT_COST_PER_1K", "0.0003"))
    
    @classmethod
    def get_model_config(cls) -> Dict[str, Any]:
        """Get model configuration"""
        return {
            "model": cls.MODEL_NAME,
            "temperature": cls.TEMPERATURE,
            "max_tokens": cls.MAX_TOKENS,
            "api_key": cls.GOOGLE_API_KEY
        }
    
    @classmethod
    def get_cache_config(cls) -> Dict[str, Any]:
        """Get cache configuration"""
        if cls.CACHE_TYPE == "redis" and cls.REDIS_URL:
            return {
                "type": "redis",
                "host": cls.REDIS_URL,
                "port": 6379,
                "password": cls.REDIS_PASSWORD,
                "db": 0
            }
        else:
            return {
                "type": "memory"
            }
    
    @classmethod
    def get_cost_limits(cls) -> Dict[str, float]:
        """Get cost limits"""
        return {
            "daily_limit": cls.DAILY_COST_LIMIT,
            "monthly_limit": cls.MONTHLY_COST_LIMIT
        }
    
    @classmethod
    def get_rate_limits(cls) -> Dict[str, int]:
        """Get rate limits"""
        return {
            "requests_per_minute": cls.REQUESTS_PER_MINUTE,
            "requests_per_hour": cls.REQUESTS_PER_HOUR
        }
    
    @classmethod
    def get_cost_estimation(cls) -> Dict[str, float]:
        """Get cost estimation parameters"""
        return {
            "input_cost_per_1k": cls.INPUT_COST_PER_1K,
            "output_cost_per_1k": cls.OUTPUT_COST_PER_1K
        }
    
    @classmethod
    def validate_config(cls) -> bool:
        """Validate configuration"""
        errors = []
        
        if not cls.GOOGLE_API_KEY:
            errors.append("GOOGLE_API_KEY environment variable is required")
        
        if cls.DAILY_COST_LIMIT <= 0:
            errors.append("LLM_DAILY_COST_LIMIT must be greater than 0")
        
        if cls.MONTHLY_COST_LIMIT <= 0:
            errors.append("LLM_MONTHLY_COST_LIMIT must be greater than 0")
        
        if cls.REQUESTS_PER_MINUTE <= 0:
            errors.append("LLM_RATE_LIMIT_RPM must be greater than 0")
        
        if cls.REQUESTS_PER_HOUR <= 0:
            errors.append("LLM_RATE_LIMIT_RPH must be greater than 0")
        
        if errors:
            print("Configuration validation errors:")
            for error in errors:
                print(f"  - {error}")
            return False
        
        return True
    
    @classmethod
    def print_config(cls):
        """Print current configuration"""
        print("LiteLLM Configuration:")
        print(f"  Model: {cls.MODEL_NAME}")
        print(f"  Temperature: {cls.TEMPERATURE}")
        print(f"  Max Tokens: {cls.MAX_TOKENS}")
        print(f"  Cache Type: {cls.CACHE_TYPE}")
        print(f"  Daily Cost Limit: ${cls.DAILY_COST_LIMIT}")
        print(f"  Monthly Cost Limit: ${cls.MONTHLY_COST_LIMIT}")
        print(f"  Rate Limit (RPM): {cls.REQUESTS_PER_MINUTE}")
        print(f"  Rate Limit (RPH): {cls.REQUESTS_PER_HOUR}")
        print(f"  Prometheus Enabled: {cls.ENABLE_PROMETHEUS}")
        print(f"  API Key Set: {'Yes' if cls.GOOGLE_API_KEY else 'No'}") 