import sys
import os
import logging

# Add the project root to the Python path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from pkg.server import create_server
from business.llm_service import LLMService
from connector.embedding_connector import create_embedding_connector
from router.llm_handler import LLMHandler

# Configure logging
logging.basicConfig(level=logging.INFO)

def test_llm_service_setup():
    """Test LLM service setup"""
    print("\n=== Testing LLM Service Setup ===")
    
    try:
        # Create embedding connector
        embedding_connector = create_embedding_connector()
        
        # Create LLM service
        llm_service = LLMService(embedding_connector)
        
        # Check if API key is available
        api_key = os.getenv("GOOGLE_API_KEY")
        if not api_key:
            print("GOOGLE_API_KEY not set - skipping LLM initialization test")
            return False
        
        # Initialize the service
        if llm_service.initialize():
            print("LLMService initialized successfully!")
            return True
        else:
            print("LLMService initialization failed!")
            return False
            
    except Exception as e:
        print(f"Error during LLM service setup: {e}")
        return False

def test_llm_handler():
    """Test LLM handler functionality"""
    print("\n=== Testing LLM Handler ===")
    
    try:
        # Create embedding connector
        embedding_connector = create_embedding_connector()
        
        # Create LLM service
        llm_service = LLMService(embedding_connector)
        
        # Check if API key is available
        api_key = os.getenv("GOOGLE_API_KEY")
        if not api_key:
            print("GOOGLE_API_KEY not set - skipping LLM handler test")
            return False
        
        # Initialize the service
        if not llm_service.initialize():
            print("Failed to initialize LLMService for handler test")
            return False
        
        # Create handler
        handler = LLMHandler(llm_service)
        print("LLMHandler created successfully")
        
        # Test getting LLM status
        status_result = handler.get_llm_status()
        if status_result["success"]:
            print("LLMHandler can get LLM status")
        else:
            print("LLMHandler failed to get LLM status")
        
        # Test asking a question (if we have guides in the database)
        test_question = "What is the basic rotation for Fury Warrior?"
        result = handler.ask_question(test_question)
        
        if result["success"]:
            print("LLMHandler can process questions")
            print(f"Answer received: {len(result.get('answer', ''))} characters")
            print(f"Sources found: {len(result.get('sources', []))}")
        else:
            print("LLMHandler failed to process question")
            print(f"Error: {result.get('error')}")
        
        return True
        
    except Exception as e:
        print(f"Error testing LLM handler: {e}")
        return False

def test_server_with_llm():
    """Test server setup with LLM components"""
    print("\n=== Testing Server with LLM Components ===")
    
    try:
        # Create server
        server = create_server()
        
        # Check if API key is available
        api_key = os.getenv("GOOGLE_API_KEY")
        if not api_key:
            print("GOOGLE_API_KEY not set - skipping server LLM test")
            return False
        
        # Setup server
        if server.setup():
            print("Server setup successful with LLM components")
            
            # Test LLM service
            llm_service = server.get_llm_service()
            if llm_service and llm_service.is_ready():
                print("LLMService is ready")
            else:
                print("LLMService not ready")
            
            # Test LLM handler
            llm_handler = server.get_llm_handler()
            if llm_handler:
                print("LLMHandler is available")
            else:
                print("LLMHandler not available")
            
            # Test server status
            status = server.get_status()
            llm_ready = status.get("layers", {}).get("business", {}).get("llm_service", {}).get("ready", False)
            print(f"LLM service ready in server status: {llm_ready}")
            
            return True
        else:
            print("Server setup failed")
            return False
            
    except Exception as e:
        print(f"Error during server LLM test: {e}")
        return False

def test_llm_with_guides():
    """Test LLM with actual guides in the database"""
    print("\n=== Testing LLM with Guides ===")
    
    try:
        # Create embedding connector
        embedding_connector = create_embedding_connector()
        
        # Check if we have guides in the database
        stats = embedding_connector.get_stats()
        total_guides = stats.get("total_guides", 0)
        
        if total_guides == 0:
            print("No guides in database - skipping LLM with guides test")
            print("Please scrape some guides first using the scraping endpoints")
            return False
        
        print(f"Found {total_guides} guides in database")
        
        # Create LLM service
        llm_service = LLMService(embedding_connector)
        
        # Check if API key is available
        api_key = os.getenv("GOOGLE_API_KEY")
        if not api_key:
            print("GOOGLE_API_KEY not set - skipping LLM with guides test")
            return False
        
        # Initialize the service
        if not llm_service.initialize():
            print("Failed to initialize LLMService")
            return False
        
        # Test questions
        test_questions = [
            "What is the basic rotation for Fury Warrior?",
            "What talents should I use for Arms Warrior?",
            "How do I optimize my DPS as a Warrior?"
        ]
        
        for question in test_questions:
            print(f"\nTesting question: {question}")
            result = llm_service.ask_question(question)
            
            if result["success"]:
                print(f"Answer: {result['answer'][:200]}...")
                print(f"Sources: {len(result['sources'])}")
            else:
                print(f"Error: {result.get('error')}")
        
        return True
        
    except Exception as e:
        print(f"Error testing LLM with guides: {e}")
        return False

def main():
    """Run all LLM integration tests"""
    print("Starting LLM Integration Tests...")
    
    # Test 1: LLM service setup
    test1_passed = test_llm_service_setup()
    
    # Test 2: LLM handler
    test2_passed = test_llm_handler()
    
    # Test 3: Server with LLM components
    test3_passed = test_server_with_llm()
    
    # Test 4: LLM with guides
    test4_passed = test_llm_with_guides()
    
    # Summary
    print("\n=== Test Summary ===")
    print(f"LLM Service Setup: {'PASSED' if test1_passed else 'FAILED'}")
    print(f"LLM Handler: {'PASSED' if test2_passed else 'FAILED'}")
    print(f"Server with LLM: {'PASSED' if test3_passed else 'FAILED'}")
    print(f"LLM with Guides: {'PASSED' if test4_passed else 'FAILED'}")
    
    all_passed = test1_passed and test2_passed and test3_passed and test4_passed
    print(f"\nOverall Result: {'ALL TESTS PASSED' if all_passed else 'SOME TESTS FAILED'}")
    
    # Note about API key
    if not os.getenv("GOOGLE_API_KEY"):
        print("\nNote: Set GOOGLE_API_KEY environment variable to test LLM functionality")
    
    return all_passed

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1) 