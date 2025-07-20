#!/usr/bin/env python3
"""
Test script for LiteLLM integration
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

def test_configuration():
    """Test LiteLLM configuration"""
    print("Testing LiteLLM Configuration...")
    
    # Print current configuration
    LiteLLMConfig.print_config()
    
    # Validate configuration
    if not LiteLLMConfig.validate_config():
        print("❌ Configuration validation failed")
        return False
    
    print("✅ Configuration validation passed")
    return True

def test_monitoring_service():
    """Test monitoring service"""
    print("\nTesting Monitoring Service...")
    
    try:
        monitoring_service = MonitoringService()
        
        # Test metrics generation
        metrics = monitoring_service.get_metrics()
        if metrics:
            print("✅ Prometheus metrics generation working")
        else:
            print("❌ Prometheus metrics generation failed")
            return False
        
        # Test health status
        health = monitoring_service.get_health_status()
        if health.get("status") == "healthy":
            print("✅ Monitoring service health check passed")
        else:
            print("❌ Monitoring service health check failed")
            return False
        
        return True
        
    except Exception as e:
        print(f"❌ Monitoring service test failed: {e}")
        return False

def test_litellm_service():
    """Test LiteLLM service"""
    print("\nTesting LiteLLM Service...")
    
    try:
        # Initialize embedding connector
        embedding_connector = EmbeddingConnector()
        if not embedding_connector.setup():
            print("❌ Failed to setup embedding connector")
            return False
        
        # Initialize LiteLLM service
        litellm_service = LiteLLMService(embedding_connector)
        if not litellm_service.initialize():
            print("❌ Failed to initialize LiteLLM service")
            return False
        
        # Test service info
        service_info = litellm_service.get_service_info()
        print(f"✅ LiteLLM service initialized: {service_info['model']}")
        
        # Test ready status
        if litellm_service.is_ready():
            print("✅ LiteLLM service is ready")
        else:
            print("❌ LiteLLM service is not ready")
            return False
        
        return True
        
    except Exception as e:
        print(f"❌ LiteLLM service test failed: {e}")
        return False

async def test_litellm_question():
    """Test asking a question with LiteLLM"""
    print("\nTesting LiteLLM Question...")
    
    try:
        # Initialize services
        embedding_connector = EmbeddingConnector()
        if not embedding_connector.setup():
            print("❌ Failed to setup embedding connector")
            return False
        
        litellm_service = LiteLLMService(embedding_connector)
        if not litellm_service.initialize():
            print("❌ Failed to initialize LiteLLM service")
            return False
        
        # Test question
        test_question = "What is the basic rotation for Fury Warrior?"
        print(f"Testing question: {test_question}")
        
        # Test sync version
        response: LLMResponse = litellm_service.ask_question(test_question)
        
        if response.success:
            print("✅ Sync question test passed")
            print(f"   Answer length: {len(response.answer)} characters")
            print(f"   Sources found: {len(response.sources)}")
            print(f"   Duration: {response.metadata.get('duration', 0):.2f}s")
            print(f"   Tokens used: {response.metadata.get('tokens_used', 0)}")
            print(f"   Cost: ${response.metadata.get('cost_usd', 0):.6f}")
            print(f"   Cache hit: {response.metadata.get('cache_hit', False)}")
        else:
            print(f"❌ Sync question test failed: {response.error}")
            return False
        
        # Test async version
        async_response: LLMResponse = await litellm_service.ask_question_async(test_question)
        
        if async_response.success:
            print("✅ Async question test passed")
            print(f"   Answer length: {len(async_response.answer)} characters")
            print(f"   Sources found: {len(async_response.sources)}")
            print(f"   Duration: {async_response.metadata.get('duration', 0):.2f}s")
            print(f"   Tokens used: {async_response.metadata.get('tokens_used', 0)}")
            print(f"   Cost: ${async_response.metadata.get('cost_usd', 0):.6f}")
            print(f"   Cache hit: {async_response.metadata.get('cache_hit', False)}")
        else:
            print(f"❌ Async question test failed: {async_response.error}")
            return False
        
        return True
        
    except Exception as e:
        print(f"❌ LiteLLM question test failed: {e}")
        return False

def test_cost_estimation():
    """Test cost estimation"""
    print("\nTesting Cost Estimation...")
    
    try:
        embedding_connector = EmbeddingConnector()
        embedding_connector.setup()
        
        litellm_service = LiteLLMService(embedding_connector)
        litellm_service.initialize()
        
        # Test cost estimation
        test_tokens = [100, 500, 1000, 2000]
        
        for tokens in test_tokens:
            cost = litellm_service._estimate_cost(tokens)
            print(f"   {tokens} tokens = ${cost:.6f}")
        
        print("✅ Cost estimation working")
        return True
        
    except Exception as e:
        print(f"❌ Cost estimation test failed: {e}")
        return False

def main():
    """Run all tests"""
    print("🧪 LiteLLM Integration Tests")
    print("=" * 50)
    
    tests = [
        ("Configuration", test_configuration),
        ("Monitoring Service", test_monitoring_service),
        ("LiteLLM Service", test_litellm_service),
        ("Cost Estimation", test_cost_estimation),
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        try:
            if test_func():
                passed += 1
            else:
                print(f"❌ {test_name} test failed")
        except Exception as e:
            print(f"❌ {test_name} test failed with exception: {e}")
    
    # Test async question (requires asyncio)
    try:
        if asyncio.run(test_litellm_question()):
            passed += 1
            total += 1
        else:
            print("❌ Async question test failed")
            total += 1
    except Exception as e:
        print(f"❌ Async question test failed with exception: {e}")
        total += 1
    
    print("\n" + "=" * 50)
    print(f"📊 Test Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! LiteLLM integration is working correctly.")
        return 0
    else:
        print("❌ Some tests failed. Please check the configuration and setup.")
        return 1

if __name__ == "__main__":
    exit(main()) 