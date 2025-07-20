#!/usr/bin/env python3
"""
Script to scrape all WoW classes and query about Destruction Warlock
"""

import os
import sys
import asyncio
import json
import time
import logging
from typing import Dict, List, Any

# Add project root to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from business.scraper_service import ScraperService
from business.guide_service import GuideService
from business.litellm_service import LiteLLMService
from connector.embedding_connector import EmbeddingConnector

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class WoWDataScraper:
    """Comprehensive scraper for all WoW classes with querying capabilities"""
    
    def __init__(self):
        self.scraper_service = ScraperService()
        self.embedding_connector = EmbeddingConnector()
        self.guide_service = GuideService(self.embedding_connector)
        self.litellm_service = LiteLLMService(self.embedding_connector)
        
    def initialize_services(self) -> bool:
        """Initialize all services"""
        try:
            logger.info("Initializing services...")
            
            # Initialize scraper
            if not self.scraper_service.initialize():
                logger.error("Failed to initialize scraper service")
                return False
            
            # Initialize embedding connector
            if not self.embedding_connector.setup():
                logger.error("Failed to setup embedding connector")
                return False
            
            # Initialize guide service
            if not self.guide_service.initialize():
                logger.error("Failed to initialize guide service")
                return False
            
            # Initialize LiteLLM service
            if not self.litellm_service.initialize():
                logger.error("Failed to initialize LiteLLM service")
                return False
            
            logger.info("✅ All services initialized successfully")
            return True
            
        except Exception as e:
            logger.error(f"Error initializing services: {e}")
            return False
    
    def load_classes_config(self) -> Dict[str, Any]:
        """Load classes configuration"""
        try:
            config_path = os.path.join(os.path.dirname(__file__), '..', 'conf', 'classes.json')
            with open(config_path, 'r') as f:
                return json.load(f)
        except Exception as e:
            logger.error(f"Error loading classes config: {e}")
            return {"classes": []}
    
    def scrape_all_classes(self) -> Dict[str, List[Dict[str, Any]]]:
        """Scrape guides for all classes and specializations"""
        logger.info("🚀 Starting comprehensive class scraping...")
        
        config = self.load_classes_config()
        results = {
            "successful": [],
            "failed": [],
            "total_scraped": 0
        }
        
        for class_info in config["classes"]:
            class_name = class_info["name"]
            logger.info(f"📚 Scraping class: {class_name.title()}")
            
            for spec in class_info["specializations"]:
                spec_name = spec["name"]
                logger.info(f"  └─ Scraping spec: {spec_name.title()}")
                
                try:
                    # Scrape the guide
                    scrape_result = self.guide_service.scrape_and_store_guide(
                        class_name=class_name,
                        spec_name=spec_name,
                        guide_type="overview-pve-dps"  # Default guide type
                    )
                    
                    if scrape_result["success"]:
                        results["successful"].append({
                            "class": class_name,
                            "spec": spec_name,
                            "result": scrape_result
                        })
                        results["total_scraped"] += 1
                        logger.info(f"    ✅ Successfully scraped {class_name.title()} {spec_name.title()}")
                    else:
                        results["failed"].append({
                            "class": class_name,
                            "spec": spec_name,
                            "error": scrape_result.get("error", "Unknown error")
                        })
                        logger.warning(f"    ❌ Failed to scrape {class_name.title()} {spec_name.title()}: {scrape_result.get('error')}")
                    
                    # Small delay to be respectful to the server
                    time.sleep(1)
                    
                except Exception as e:
                    results["failed"].append({
                        "class": class_name,
                        "spec": spec_name,
                        "error": str(e)
                    })
                    logger.error(f"    ❌ Exception scraping {class_name.title()} {spec_name.title()}: {e}")
        
        logger.info(f"🎉 Scraping completed!")
        logger.info(f"   ✅ Successful: {len(results['successful'])}")
        logger.info(f"   ❌ Failed: {len(results['failed'])}")
        logger.info(f"   📊 Total scraped: {results['total_scraped']}")
        
        return results
    
    async def query_about_destruction_warlock(self) -> Dict[str, Any]:
        """Query the LiteLLM service about Destruction Warlock"""
        logger.info("🔍 Querying about Destruction Warlock...")
        
        questions = [
            "What is Destruction Warlock and how does it work?",
            "What is the basic rotation for Destruction Warlock?",
            "What are the best talents for Destruction Warlock?",
            "What are the key abilities and spells for Destruction Warlock?",
            "How do I optimize DPS as a Destruction Warlock?"
        ]
        
        results = []
        
        for i, question in enumerate(questions, 1):
            logger.info(f"  Question {i}: {question}")
            
            try:
                # Use async version for better performance
                response = await self.litellm_service.ask_question_async(question)
                
                if response.success:
                    result = {
                        "question": question,
                        "answer": response.answer,
                        "sources": response.sources,
                        "metadata": response.metadata
                    }
                    results.append(result)
                    
                    logger.info(f"    ✅ Answer length: {len(response.answer)} characters")
                    logger.info(f"    📊 Duration: {response.metadata.get('duration', 0):.2f}s")
                    logger.info(f"    💰 Cost: ${response.metadata.get('cost_usd', 0):.6f}")
                    logger.info(f"    🔍 Sources: {len(response.sources)}")
                    
                    # Print a preview of the answer
                    preview = response.answer[:200] + "..." if len(response.answer) > 200 else response.answer
                    logger.info(f"    📝 Preview: {preview}")
                    
                else:
                    logger.error(f"    ❌ Failed to get answer: {response.error}")
                    results.append({
                        "question": question,
                        "error": response.error
                    })
                
                # Small delay between questions
                await asyncio.sleep(0.5)
                
            except Exception as e:
                logger.error(f"    ❌ Exception getting answer: {e}")
                results.append({
                    "question": question,
                    "error": str(e)
                })
        
        return {
            "total_questions": len(questions),
            "successful_answers": len([r for r in results if "answer" in r]),
            "failed_answers": len([r for r in results if "error" in r]),
            "results": results
        }
    
    def get_database_stats(self) -> Dict[str, Any]:
        """Get statistics about the embedding database"""
        try:
            stats = self.embedding_connector.get_stats()
            logger.info("📊 Database Statistics:")
            logger.info(f"   Total guides: {stats.get('total_guides', 0)}")
            logger.info(f"   Total chunks: {stats.get('total_chunks', 0)}")
            logger.info(f"   Classes: {stats.get('classes', [])}")
            return stats
        except Exception as e:
            logger.error(f"Error getting database stats: {e}")
            return {}
    
    def search_for_warlock_content(self) -> List[Dict[str, Any]]:
        """Search for Warlock-specific content in the database"""
        logger.info("🔍 Searching for Warlock content in database...")
        
        search_queries = [
            "destruction warlock",
            "warlock destruction spec",
            "warlock abilities",
            "warlock spells",
            "warlock rotation"
        ]
        
        all_results = []
        
        for query in search_queries:
            try:
                results = self.embedding_connector.search_guides(query, limit=5)
                logger.info(f"  Query '{query}': Found {len(results)} results")
                
                for result in results:
                    all_results.append({
                        "query": query,
                        "class_name": result["class_name"],
                        "spec_name": result["spec_name"],
                        "similarity_score": result["similarity_score"],
                        "content_preview": result["content"][:200] + "..."
                    })
                    
            except Exception as e:
                logger.error(f"  Error searching for '{query}': {e}")
        
        return all_results

async def main():
    """Main function to run the complete workflow"""
    print("🎮 WoW Class Learner - Comprehensive Scraping and Querying")
    print("=" * 60)
    
    # Check environment
    if not os.getenv("GOOGLE_API_KEY"):
        print("❌ GOOGLE_API_KEY environment variable is required")
        print("   Set it with: export GOOGLE_API_KEY='your-api-key'")
        return 1
    
    # Initialize scraper
    scraper = WoWDataScraper()
    
    # Initialize services
    if not scraper.initialize_services():
        print("❌ Failed to initialize services")
        return 1
    
    print("✅ Services initialized successfully")
    
    # Step 1: Scrape all classes
    print("\n📚 Step 1: Scraping all WoW classes...")
    scrape_results = scraper.scrape_all_classes()
    
    # Step 2: Get database statistics
    print("\n📊 Step 2: Database statistics...")
    db_stats = scraper.get_database_stats()
    
    # Step 3: Search for Warlock content
    print("\n🔍 Step 3: Searching for Warlock content...")
    warlock_search = scraper.search_for_warlock_content()
    
    # Step 4: Query about Destruction Warlock
    print("\n🔮 Step 4: Querying about Destruction Warlock...")
    query_results = await scraper.query_about_destruction_warlock()
    
    # Summary
    print("\n" + "=" * 60)
    print("📋 SUMMARY")
    print("=" * 60)
    
    print(f"📚 Scraping Results:")
    print(f"   ✅ Successful: {len(scrape_results['successful'])}")
    print(f"   ❌ Failed: {len(scrape_results['failed'])}")
    print(f"   📊 Total scraped: {scrape_results['total_scraped']}")
    
    print(f"\n📊 Database Statistics:")
    print(f"   Total guides: {db_stats.get('total_guides', 0)}")
    print(f"   Total chunks: {db_stats.get('total_chunks', 0)}")
    
    print(f"\n🔍 Warlock Search Results:")
    print(f"   Found {len(warlock_search)} relevant content pieces")
    
    print(f"\n🔮 Destruction Warlock Queries:")
    print(f"   Questions asked: {query_results['total_questions']}")
    print(f"   Successful answers: {query_results['successful_answers']}")
    print(f"   Failed answers: {query_results['failed_answers']}")
    
    # Show some example answers
    print(f"\n💡 Example Destruction Warlock Information:")
    for i, result in enumerate(query_results['results'][:2], 1):
        if "answer" in result:
            print(f"\n   Q{i}: {result['question']}")
            answer_preview = result['answer'][:300] + "..." if len(result['answer']) > 300 else result['answer']
            print(f"   A{i}: {answer_preview}")
    
    print("\n🎉 Process completed successfully!")
    return 0

if __name__ == "__main__":
    exit(asyncio.run(main())) 