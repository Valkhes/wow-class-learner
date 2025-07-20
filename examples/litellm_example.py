#!/usr/bin/env python3
"""
Example script demonstrating LiteLLM gateway usage
"""

import os
import sys
import asyncio
import logging
from typing import Dict, Any

# Add project root to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from business.litellm_service import LiteLLMService, LLMResponse
from business.monitoring_service import MonitoringService
from connector.embedding_connector import EmbeddingConnector
from conf.litellm_config import LiteLLMConfig

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def example_basic_usage():
    """Example of basic LiteLLM usage"""
    print("🔍 Example: Basic LiteLLM Usage")
    print("-" * 40)
    
    # Initialize services
    embedding_connector = EmbeddingConnector()
    embedding_connector.setup()
    
    litellm_service = LiteLLMService(embedding_connector)
    litellm_service.initialize()
    
    # Ask a question
    question = "What is the best talent build for Fire Mage?"
    print(f"Question: {question}")
    
    response: LLMResponse = litellm_service.ask_question(question)
    
    if response.success:
        print(f"✅ Answer: {response.answer[:200]}...")
        print(f"📊 Metadata:")
        print(f"   - Duration: {response.metadata.get('duration', 0):.2f}s")
        print(f"   - Tokens used: {response.metadata.get('tokens_used', 0)}")
        print(f"   - Cost: ${response.metadata.get('cost_usd', 0):.6f}")
        print(f"   - Cache hit: {response.metadata.get('cache_hit', False)}")
        print(f"   - Sources: {len(response.sources)}")
    else:
        print(f"❌ Error: {response.error}")

async def example_async_usage():
    """Example of async LiteLLM usage"""
    print("\n⚡ Example: Async LiteLLM Usage")
    print("-" * 40)
    
    # Initialize services
    embedding_connector = EmbeddingConnector()
    embedding_connector.setup()
    
    litellm_service = LiteLLMService(embedding_connector)
    litellm_service.initialize()
    
    # Ask multiple questions concurrently
    questions = [
        "What is the basic rotation for Fury Warrior?",
        "How do I optimize DPS as a Fire Mage?",
        "What are the best talents for Holy Paladin?"
    ]
    
    print(f"Asking {len(questions)} questions concurrently...")
    
    # Create tasks for concurrent execution
    tasks = [
        litellm_service.ask_question_async(question)
        for question in questions
    ]
    
    # Execute all questions concurrently
    responses = await asyncio.gather(*tasks)
    
    for i, response in enumerate(responses):
        if response.success:
            print(f"✅ Question {i+1}: {response.answer[:100]}...")
            print(f"   Duration: {response.metadata.get('duration', 0):.2f}s")
            print(f"   Cost: ${response.metadata.get('cost_usd', 0):.6f}")
        else:
            print(f"❌ Question {i+1} failed: {response.error}")

def example_monitoring():
    """Example of monitoring usage"""
    print("\n📊 Example: Monitoring Usage")
    print("-" * 40)
    
    # Initialize monitoring service
    monitoring_service = MonitoringService()
    
    # Get various metrics
    print("📈 Prometheus Metrics:")
    metrics = monitoring_service.get_metrics()
    print(f"   Metrics length: {len(metrics)} characters")
    
    print("\n🏥 Health Status:")
    health = monitoring_service.get_health_status()
    print(f"   Status: {health.get('status')}")
    print(f"   Timestamp: {health.get('timestamp')}")
    
    print("\n📋 Usage Summary:")
    usage = monitoring_service.get_usage_summary()
    print(f"   Total requests: {usage.get('total_requests', 0)}")
    print(f"   Successful requests: {usage.get('successful_requests', 0)}")
    print(f"   Failed requests: {usage.get('failed_requests', 0)}")
    
    print("\n💰 Cost Analysis:")
    cost_analysis = monitoring_service.get_cost_analysis()
    print(f"   Daily cost: ${cost_analysis.get('daily_cost', 0):.2f}")
    print(f"   Monthly cost: ${cost_analysis.get('monthly_cost', 0):.2f}")

def example_configuration():
    """Example of configuration usage"""
    print("\n⚙️ Example: Configuration Usage")
    print("-" * 40)
    
    # Print current configuration
    LiteLLMConfig.print_config()
    
    # Get specific configurations
    model_config = LiteLLMConfig.get_model_config()
    cache_config = LiteLLMConfig.get_cache_config()
    cost_limits = LiteLLMConfig.get_cost_limits()
    rate_limits = LiteLLMConfig.get_rate_limits()
    
    print(f"\n🔧 Model Config: {model_config['model']}")
    print(f"🔧 Cache Type: {cache_config['type']}")
    print(f"🔧 Daily Cost Limit: ${cost_limits['daily_limit']}")
    print(f"🔧 Rate Limit (RPM): {rate_limits['requests_per_minute']}")

def example_cost_tracking():
    """Example of cost tracking"""
    print("\n💰 Example: Cost Tracking")
    print("-" * 40)
    
    # Initialize services
    embedding_connector = EmbeddingConnector()
    embedding_connector.setup()
    
    litellm_service = LiteLLMService(embedding_connector)
    litellm_service.initialize()
    
    # Test different token amounts
    test_tokens = [100, 500, 1000, 2000, 5000]
    
    print("Token usage vs cost estimation:")
    for tokens in test_tokens:
        cost = litellm_service._estimate_cost(tokens)
        print(f"   {tokens:>5} tokens = ${cost:>8.6f}")
    
    # Show cost limits
    cost_limits = litellm_service.cost_limits
    print(f"\nCost Limits:")
    print(f"   Daily: ${cost_limits['daily_limit']}")
    print(f"   Monthly: ${cost_limits['monthly_limit']}")

async def main():
    """Run all examples"""
    print("🚀 LiteLLM Gateway Examples")
    print("=" * 50)
    
    try:
        # Check configuration first
        if not LiteLLMConfig.validate_config():
            print("❌ Configuration validation failed. Please check your environment variables.")
            print("Required: GOOGLE_API_KEY")
            return 1
        
        # Run examples
        await example_basic_usage()
        await example_async_usage()
        example_monitoring()
        example_configuration()
        example_cost_tracking()
        
        print("\n" + "=" * 50)
        print("✅ All examples completed successfully!")
        print("\n💡 Tips:")
        print("   - Use caching to improve performance")
        print("   - Monitor costs with Prometheus metrics")
        print("   - Set appropriate rate and cost limits")
        print("   - Use async endpoints for better concurrency")
        
        return 0
        
    except Exception as e:
        print(f"❌ Example failed with error: {e}")
        return 1

if __name__ == "__main__":
    exit(asyncio.run(main())) 