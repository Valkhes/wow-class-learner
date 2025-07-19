import logging
from typing import List, Dict, Optional
import json
import os

from entities.scraper import WoWheadScraper, load_classes_data, save_scraped_data

logger = logging.getLogger(__name__)

class ScraperService:
    """Business layer service for scraping operations"""
    
    def __init__(self):
        self.scraper: Optional[WoWheadScraper] = None
        self.classes_data: List[Dict] = []
        self.is_initialized = False
    
    def initialize(self) -> bool:
        """
        Initialize the scraper service
        
        Returns:
            bool: True if initialization successful, False otherwise
        """
        try:
            logger.info("Initializing ScraperService...")
            
            # Initialize scraper
            self.scraper = WoWheadScraper()
            
            # Load classes data
            self.classes_data = load_classes_data()
            if not self.classes_data:
                logger.error("Failed to load classes data")
                return False
            
            self.is_initialized = True
            logger.info("ScraperService initialized successfully")
            return True
            
        except Exception as e:
            logger.error(f"Error initializing ScraperService: {e}")
            return False
    
    def scrape_guide(self, class_name: str, spec_name: str, guide_type: str = "overview-pve-dps") -> Dict:
        """
        Scrape a specific guide
        
        Args:
            class_name: Class name
            spec_name: Spec name
            guide_type: Guide type
            
        Returns:
            Dictionary with scraping result
        """
        if not self.is_initialized:
            return {"success": False, "error": "ScraperService not initialized"}
        
        try:
            result = self.scraper.scrape_full_guide(
                class_name=class_name.lower(),
                spec_name=spec_name.lower(),
                guide_type=guide_type
            )
            return result
            
        except Exception as e:
            logger.error(f"Error scraping guide: {e}")
            return {"success": False, "error": str(e)}
    
    def scrape_all_guides(self) -> List[Dict]:
        """
        Scrape guides for all classes and specializations
        
        Returns:
            List of scraping results
        """
        if not self.is_initialized:
            return []
        
        try:
            results = self.scraper.scrape_all_guides(self.classes_data)
            return results
            
        except Exception as e:
            logger.error(f"Error scraping all guides: {e}")
            return []
    
    def get_classes_data(self) -> List[Dict]:
        """
        Get classes data
        
        Returns:
            List of classes data
        """
        return self.classes_data
    
    def get_class_specs(self, class_name: str) -> Optional[Dict]:
        """
        Get specializations for a specific class
        
        Args:
            class_name: Class name
            
        Returns:
            Class data with specializations or None if not found
        """
        for class_data in self.classes_data:
            if class_data["name"].lower() == class_name.lower():
                return {
                    "class_name": class_data["name"],
                    "specializations": class_data["specializations"]
                }
        return None
    
    def build_guide_url(self, class_name: str, spec_name: str, guide_type: str = "overview-pve-dps") -> str:
        """
        Build guide URL
        
        Args:
            class_name: Class name
            spec_name: Spec name
            guide_type: Guide type
            
        Returns:
            Complete guide URL
        """
        if not self.is_initialized:
            return ""
        
        return self.scraper.build_guide_url(class_name, spec_name, guide_type)
    
    def save_scraped_data(self, data: List[Dict], filename: str = "scraped_guides.json") -> bool:
        """
        Save scraped data to file
        
        Args:
            data: Scraped data
            filename: Output filename
            
        Returns:
            True if successful, False otherwise
        """
        try:
            save_scraped_data(data, filename)
            return True
        except Exception as e:
            logger.error(f"Error saving scraped data: {e}")
            return False
    
    def is_ready(self) -> bool:
        """
        Check if service is ready
        
        Returns:
            True if service is initialized and ready
        """
        return self.is_initialized and self.scraper is not None 