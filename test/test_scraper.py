#!/usr/bin/env python3
"""
Test script for the WoWhead scraper with Clean Architecture and class-based layers
"""

import sys
import os
import logging

# Add the project root to the Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from pkg.server import create_server
from business.scraper_service import ScraperService
from business.guide_service import GuideService
from connector.embedding_connector import create_embedding_connector
from router.guide_handler import GuideHandler

# Configure logging
logging.basicConfig(level=logging.INFO)

def test_server_setup():
    """Test server setup with all layers"""
    print("\n=== Testing Server Setup ===")
    
    try:
        # Create server
        server = create_server()
        
        # Setup server
        if server.setup():
            print("Server setup successful!")
            
            # Test connector layer
            if server.get_embedding_connector():
                print("Connector layer (embedding database) initialized")
            else:
                print("Connector layer not initialized")
            
            # Test business layer - scraper service
            if server.get_scraper_service():
                print("Business layer (scraper service) initialized")
            else:
                print("Business layer (scraper service) not initialized")
            
            # Test business layer - guide service
            if server.get_guide_service():
                print("Business layer (guide service) initialized")
            else:
                print("Business layer (guide service) not initialized")
            
            # Test handler layer
            if server.get_guide_handler():
                print("Handler layer (guide handler) initialized")
            else:
                print("Handler layer (guide handler) not initialized")
            
            return server
        else:
            print("Server setup failed!")
            return None
            
    except Exception as e:
        print(f"Error during server setup: {e}")
        return None

def test_scraper_service():
    """Test ScraperService functionality"""
    print("\n=== Testing ScraperService ===")
    
    try:
        # Create ScraperService
        scraper_service = ScraperService()
        
        # Initialize
        if scraper_service.initialize():
            print("ScraperService initialized successfully")
            
            # Test scraping a guide
            result = scraper_service.scrape_guide("warrior", "arms", "overview-pve-dps")
            if result["success"]:
                print("ScraperService can scrape guides")
                return True
            else:
                print("ScraperService failed to scrape guide")
                return False
        else:
            print("ScraperService initialization failed")
            return False
            
    except Exception as e:
        print(f"Error testing ScraperService: {e}")
        return False

def test_guide_service():
    """Test GuideService functionality"""
    print("\n=== Testing GuideService ===")
    
    try:
        # Create embedding connector
        embedding_connector = create_embedding_connector()
        
        # Create GuideService
        guide_service = GuideService(embedding_connector)
        
        # Initialize
        if guide_service.initialize():
            print("GuideService with EmbeddingConnector initialized successfully!")
            
            # Test getting database stats
            stats = guide_service.get_database_stats()
            print(f"GuideService can get database stats: {stats}")
            
            return True
        else:
            print("GuideService with EmbeddingConnector initialization failed")
            return False
            
    except Exception as e:
        print(f"Error testing GuideService: {e}")
        return False

def test_guide_handler():
    """Test GuideHandler functionality"""
    print("\n=== Testing GuideHandler ===")
    
    try:
        # Create services
        scraper_service = ScraperService()
        if not scraper_service.initialize():
            print("Failed to initialize ScraperService for handler test")
            return False
        
        embedding_connector = create_embedding_connector()
        guide_service = GuideService(embedding_connector)
        if not guide_service.initialize():
            print("Failed to initialize GuideService for handler test")
            return False
        
        # Create handler
        handler = GuideHandler(scraper_service, guide_service)
        print("GuideHandler created successfully")
        
        # Test getting classes
        classes_data = handler.get_classes()
        if classes_data:
            print("GuideHandler can get classes")
        
        # Test scraping guides
        result = handler.scrape_guide("warrior", "arms", "overview-pve-dps")
        if result["success"]:
            print("GuideHandler can scrape guides")
        else:
            print("GuideHandler failed to scrape guide")
        
        # Test getting database stats
        stats_result = handler.get_embedding_db_stats()
        if stats_result["success"]:
            print("GuideHandler can get database stats")
        else:
            print("GuideHandler failed to get database stats")
        
        return True
        
    except Exception as e:
        print(f"Error testing handler: {e}")
        return False

def test_integration():
    """Test complete integration"""
    print("\n=== Testing Complete Integration ===")
    
    try:
        # Create server
        server = create_server()
        if not server.setup():
            print("Server setup failed")
            return False
        
        print("Server setup successful")
        
        # Test scraping and storing a guide
        scraper_service = server.get_scraper_service()
        guide_service = server.get_guide_service()
        
        if scraper_service and guide_service:
            # Scrape guide
            result = scraper_service.scrape_guide("warrior", "arms", "overview-pve-dps")
            if result["success"]:
                print("Guide scraped successfully")
                
                # Store guide
                if guide_service.store_guide(result):
                    print("Guide stored in embedding database successfully")
                    
                    # Retrieve guide
                    retrieved_guide = guide_service.get_guide("warrior", "arms", "overview-pve-dps")
                    if retrieved_guide:
                        print("Guide retrieved from embedding database successfully")
                        return True
                    else:
                        print("Failed to retrieve guide from embedding database")
                        return False
                else:
                    print("Failed to store guide in embedding database")
                    return False
            else:
                print("Failed to scrape guide")
                return False
        else:
            print("Services not available")
            return False
            
    except Exception as e:
        print(f"Error during integration test: {e}")
        return False

def main():
    """Run all tests"""
    print("Starting WoW Class Learner Integration Tests...")
    
    # Test 1: Server setup
    server = test_server_setup()
    test1_passed = server is not None
    
    # Test 2: ScraperService
    test2_passed = test_scraper_service()
    
    # Test 3: GuideService
    test3_passed = test_guide_service()
    
    # Test 4: GuideHandler
    test4_passed = test_guide_handler()
    
    # Test 5: Complete integration
    test5_passed = test_integration()
    
    # Summary
    print("\n=== Test Summary ===")
    print(f"Server Setup: {'PASSED' if test1_passed else 'FAILED'}")
    print(f"ScraperService: {'PASSED' if test2_passed else 'FAILED'}")
    print(f"GuideService: {'PASSED' if test3_passed else 'FAILED'}")
    print(f"GuideHandler: {'PASSED' if test4_passed else 'FAILED'}")
    print(f"Integration: {'PASSED' if test5_passed else 'FAILED'}")
    
    all_passed = test1_passed and test2_passed and test3_passed and test4_passed and test5_passed
    print(f"\nOverall Result: {'ALL TESTS PASSED' if all_passed else 'SOME TESTS FAILED'}")
    
    return all_passed

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1) 