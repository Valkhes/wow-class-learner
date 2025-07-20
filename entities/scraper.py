import requests
from bs4 import BeautifulSoup
import logging
import json
import os
from typing import List, Dict, Optional, Any
from urllib.parse import urljoin, urlparse
import time
import re

logger = logging.getLogger(__name__)

class WoWheadScraper:
    """Entity for scraping WoWhead class guides"""
    
    def __init__(self):
        self.base_url = "https://www.wowhead.com"
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        })
    
    def build_guide_url(self, class_name: str, spec_name: str, guide_type: str = "overview-pve-dps") -> str:
        """
        Build the URL for a specific guide
        
        Args:
            class_name: Class name (e.g., 'warrior')
            spec_name: Spec name (e.g., 'arms')
            guide_type: Guide type (e.g., 'overview-pve-dps')
            
        Returns:
            Complete guide URL
        """
        return f"{self.base_url}/guide/classes/{class_name}/{spec_name}/{guide_type}"
    
    def scrape_page(self, url: str) -> Optional[BeautifulSoup]:
        """
        Scrape a single page
        
        Args:
            url: URL to scrape
            
        Returns:
            BeautifulSoup object or None if failed
        """
        try:
            logger.info(f"Scraping: {url}")
            response = self.session.get(url, timeout=10)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            return soup
            
        except Exception as e:
            logger.error(f"Error scraping {url}: {e}")
            return None
    
    def extract_guide_content(self, soup: BeautifulSoup) -> Dict[str, Any]:
        """
        Extract guide content from BeautifulSoup object
        
        Args:
            soup: BeautifulSoup object
            
        Returns:
            Dictionary with extracted content and metadata
        """
        try:
            # Extract title
            title_elem = soup.find('h1')
            title = title_elem.get_text().strip() if title_elem else "Unknown Title"
            
            # Extract main content
            content_elem = soup.find('div', class_='guide-content')
            if not content_elem:
                content_elem = soup.find('div', class_='content')
            
            if content_elem:
                # Remove script and style elements
                for script in content_elem(["script", "style"]):
                    script.decompose()
                
                # Get text content
                content = content_elem.get_text(separator='\n', strip=True)
                
                # Clean up content
                content = re.sub(r'\n\s*\n', '\n\n', content)  # Remove extra newlines
                content = re.sub(r'\s+', ' ', content)  # Normalize whitespace
                content = content.strip()
                
            else:
                content = "No content found"
            
            # Extract metadata
            metadata = {
                "title": title,
                "description": soup.find('meta', {'name': 'description'})
                .get('content', '') if soup.find('meta', {'name': 'description'}) else "",
                "keywords": soup.find('meta', {'name': 'keywords'})
                .get('content', '') if soup.find('meta', {'name': 'keywords'}) else "",
                "author": soup.find('meta', {'name': 'author'})
                .get('content', '') if soup.find('meta', {'name': 'author'}) else "",
            }
            
            return {
                "content": content,
                "metadata": metadata
            }
            
        except Exception as e:
            logger.error(f"Error extracting content: {e}")
            return {
                "content": "Error extracting content",
                "metadata": {"error": str(e)}
            }
    
    def scrape_full_guide(self, class_name: str, spec_name: str, guide_type: str = "overview-pve-dps") -> Dict[str, Any]:
        """
        Scrape a complete guide for a class/spec combination
        
        Args:
            class_name: Class name
            spec_name: Spec name
            guide_type: Guide type
            
        Returns:
            Dictionary with scraping result
        """
        try:
            # Build URL
            url = self.build_guide_url(class_name, spec_name, guide_type)
            
            # Scrape the page
            soup = self.scrape_page(url)
            if not soup:
                return {
                    "success": False,
                    "error": f"Failed to scrape {url}",
                    "url": url,
                    "class_name": class_name,
                    "spec_name": spec_name,
                    "guide_type": guide_type
                }
            
            # Extract content
            extracted_data = self.extract_guide_content(soup)
            
            # Prepare result
            result = {
                "success": True,
                "url": url,
                "class_name": class_name,
                "spec_name": spec_name,
                "guide_type": guide_type,
                "data": extracted_data
            }
            
            logger.info(f"Successfully scraped guide for {class_name} - {spec_name}")
            return result
            
        except Exception as e:
            logger.error(f"Error scraping guide for {class_name} - {spec_name}: {e}")
            return {
                "success": False,
                "error": str(e),
                "url": self.build_guide_url(class_name, spec_name, guide_type),
                "class_name": class_name,
                "spec_name": spec_name,
                "guide_type": guide_type
            }
    
    def scrape_all_guides(self, classes_data: List[Dict]) -> List[Dict[str, Any]]:
        """
        Scrape guides for all classes and specializations
        
        Args:
            classes_data: List of classes with their specializations
            
        Returns:
            List of scraping results
        """
        results = []
        total_guides = 0
        
        for class_data in classes_data:
            class_name = class_data["name"]
            specializations = class_data["specializations"]
            
            logger.info(f"Scraping guides for {class_name} ({len(specializations)} specs)")
            
            for spec in specializations:
                spec_name = spec["name"]
                total_guides += 1
                
                logger.info(f"Scraping guide {total_guides}: {class_name} - {spec_name}")
                
                # Scrape the guide
                result = self.scrape_full_guide(class_name, spec_name)
                results.append(result)
                
                # Add a small delay to be respectful to the server
                time.sleep(1)
        
        logger.info(f"Completed scraping {len(results)} guides")
        return results

def load_classes_data() -> List[Dict]:
    """
    Load classes data from JSON file
    
    Returns:
        List of classes with their specializations
    """
    try:
        classes_file = os.path.join("conf", "classes.json")
        with open(classes_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        # Extract the classes list from the JSON structure
        classes_data = data.get("classes", [])
        
        logger.info(f"Loaded {len(classes_data)} classes from {classes_file}")
        return classes_data
        
    except Exception as e:
        logger.error(f"Error loading classes data: {e}")
        return []

def save_scraped_data(data: List[Dict], filename: str = "scraped_guides.json") -> bool:
    """
    Save scraped data to JSON file in the data folder
    
    Args:
        data: Scraped data to save
        filename: Output filename
        
    Returns:
        True if successful, False otherwise
    """
    try:
        # Ensure data directory exists
        data_dir = "data"
        os.makedirs(data_dir, exist_ok=True)
        
        # Save file to data directory
        filepath = os.path.join(data_dir, filename)
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        
        logger.info(f"Saved {len(data)} guides to {filepath}")
        return True
        
    except Exception as e:
        logger.error(f"Error saving scraped data: {e}")
        return False 