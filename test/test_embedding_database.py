#!/usr/bin/env python3
"""
Test script for embedding database integration
"""

import sys
import os
import logging

# Add the project root to the Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from connector.embedding_connector import create_embedding_connector
from business.guide_service import GuideService

# Configure logging
logging.basicConfig(level=logging.INFO)

def test_embedding_database_setup():
    """Test embedding database setup"""
    print("\n=== Testing Embedding Database Setup ===")
    
    try:
        # Create embedding connector
        embedding_connector = create_embedding_connector()
        
        # Setup the database
        if embedding_connector.setup():
            print("Embedding database setup successful!")
            return True
        else:
            print("Embedding database setup failed!")
            return False
            
    except Exception as e:
        print(f"Error during embedding database setup: {e}")
        return False

def test_guide_service_with_embedding_connector():
    """Test GuideService with EmbeddingConnector"""
    print("\n=== Testing GuideService with EmbeddingConnector ===")
    
    try:
        # Create embedding connector
        embedding_connector = create_embedding_connector()
        
        # Create GuideService
        guide_service = GuideService(embedding_connector)
        
        # Initialize the service
        if guide_service.initialize():
            print("GuideService with EmbeddingConnector initialized successfully!")
            return guide_service
        else:
            print("GuideService with EmbeddingConnector initialization failed!")
            return None
            
    except Exception as e:
        print(f"Error during GuideService setup: {e}")
        return None

def test_embedding_generation():
    """Test embedding generation"""
    print("\n=== Testing Embedding Generation ===")
    
    try:
        # Create embedding connector
        embedding_connector = create_embedding_connector()
        
        # Setup the database
        if not embedding_connector.setup():
            print("Failed to setup embedding database for embedding test")
            return False
        
        # Test embedding generation
        test_text = "This is a test text for embedding generation."
        embedding = embedding_connector._generate_embedding(test_text)
        
        print(f"Generated embedding with {len(embedding)} dimensions")
        return True
        
    except Exception as e:
        print(f"Error during embedding generation: {e}")
        return False

def test_guide_storage_and_retrieval():
    """Test guide storage and retrieval"""
    print("\n=== Testing Guide Storage and Retrieval ===")
    
    try:
        # Create embedding connector
        embedding_connector = create_embedding_connector()
        
        # Setup the database
        if not embedding_connector.setup():
            print("Failed to setup embedding database")
            return False
        
        # Test data
        test_guide_data = {
            "success": True,
            "class_name": "warrior",
            "spec_name": "arms",
            "guide_type": "overview-pve-dps",
            "url": "https://www.wowhead.com/guide/classes/warrior/arms/overview-pve-dps",
            "data": {
                "content": "This is a test guide content for Arms Warrior.",
                "metadata": {
                    "title": "Arms Warrior Test Guide",
                    "description": "Test guide for Arms Warrior",
                    "author": "Test Author"
                }
            }
        }
        
        # Store guide
        if embedding_connector.store_guide(test_guide_data):
            print("Guide stored successfully")
        else:
            print("Failed to store guide")
            return False
        
        # Retrieve guide
        retrieved_guide = embedding_connector.get_guide("warrior", "arms", "overview-pve-dps")
        if retrieved_guide:
            print("Guide retrieved successfully")
            return True
        else:
            print("Failed to retrieve guide")
            return False
            
    except Exception as e:
        print(f"Error during guide storage/retrieval: {e}")
        return False

def test_search_functionality():
    """Test search functionality"""
    print("\n=== Testing Search Functionality ===")
    
    try:
        # Create embedding connector
        embedding_connector = create_embedding_connector()
        
        # Setup the database
        if not embedding_connector.setup():
            print("Failed to setup embedding database")
            return False
        
        # Test search
        search_results = embedding_connector.search_guides("damage rotation", limit=5)
        
        if search_results:
            print(f"Found {len(search_results)} guides matching 'damage rotation'")
            return True
        else:
            print("No search results found")
            return False
            
    except Exception as e:
        print(f"Error during search test: {e}")
        return False

def main():
    """Run all embedding database tests"""
    print("Starting Embedding Database Tests...")
    
    # Test 1: Database setup
    test1_passed = test_embedding_database_setup()
    
    # Test 2: GuideService with EmbeddingConnector
    guide_service = test_guide_service_with_embedding_connector()
    test2_passed = guide_service is not None
    
    # Test 3: Embedding generation
    test3_passed = test_embedding_generation()
    
    # Test 4: Guide storage and retrieval
    test4_passed = test_guide_storage_and_retrieval()
    
    # Test 5: Search functionality
    test5_passed = test_search_functionality()
    
    # Summary
    print("\n=== Test Summary ===")
    print(f"Database Setup: {'PASSED' if test1_passed else 'FAILED'}")
    print(f"GuideService Setup: {'PASSED' if test2_passed else 'FAILED'}")
    print(f"Embedding Generation: {'PASSED' if test3_passed else 'FAILED'}")
    print(f"Guide Storage/Retrieval: {'PASSED' if test4_passed else 'FAILED'}")
    print(f"Search Functionality: {'PASSED' if test5_passed else 'FAILED'}")
    
    all_passed = test1_passed and test2_passed and test3_passed and test4_passed and test5_passed
    print(f"\nOverall Result: {'ALL TESTS PASSED' if all_passed else 'SOME TESTS FAILED'}")
    
    return all_passed

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1) 