import logging
from typing import List, Dict, Optional, Any
from connector.embedding_db import EmbeddingDBInterface

logger = logging.getLogger(__name__)

class GuideService:
    """Business layer service for guide operations"""
    
    def __init__(self, embedding_db: EmbeddingDBInterface):
        self.embedding_db = embedding_db
        self.is_initialized = False
    
    def initialize(self) -> bool:
        """
        Initialize the guide service
        
        Returns:
            bool: True if initialization successful, False otherwise
        """
        try:
            logger.info("Initializing GuideService...")
            
            # Setup embedding database
            if not self.embedding_db.setup():
                logger.error("Failed to setup embedding database")
                return False
            
            self.is_initialized = True
            logger.info("GuideService initialized successfully")
            return True
            
        except Exception as e:
            logger.error(f"Error initializing GuideService: {e}")
            return False
    
    def store_guide(self, guide_data: Dict[str, Any]) -> bool:
        """
        Store a guide in the embedding database
        
        Args:
            guide_data: Guide data from scraper
            
        Returns:
            True if successful, False otherwise
        """
        if not self.is_initialized:
            logger.error("GuideService not initialized")
            return False
        
        try:
            return self.embedding_db.store_guide(guide_data)
        except Exception as e:
            logger.error(f"Error storing guide: {e}")
            return False
    
    def store_all_guides(self, guides_data: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Store multiple guides in the embedding database
        
        Args:
            guides_data: List of guide data
            
        Returns:
            Dictionary with storage results
        """
        if not self.is_initialized:
            return {"error": "GuideService not initialized"}
        
        try:
            results = {
                "total_guides": len(guides_data),
                "successful_stores": 0,
                "failed_stores": 0,
                "stored_files": []
            }
            
            for guide_data in guides_data:
                if self.embedding_db.store_guide(guide_data):
                    results["successful_stores"] += 1
                    results["stored_files"].append(
                        f"{guide_data.get('class_name', '')}_{guide_data.get('spec_name', '')}"
                    )
                else:
                    results["failed_stores"] += 1
            
            logger.info(f"Storage complete: {results['successful_stores']}/{results['total_guides']} guides stored")
            return results
            
        except Exception as e:
            logger.error(f"Error storing all guides: {e}")
            return {"error": str(e)}
    
    def get_guide(self, class_name: str, spec_name: str, guide_type: str = "overview-pve-dps") -> Optional[Dict[str, Any]]:
        """
        Retrieve a specific guide from the embedding database
        
        Args:
            class_name: Class name
            spec_name: Spec name
            guide_type: Guide type
            
        Returns:
            Guide data if found, None otherwise
        """
        if not self.is_initialized:
            logger.error("GuideService not initialized")
            return None
        
        try:
            return self.embedding_db.get_guide(class_name, spec_name, guide_type)
        except Exception as e:
            logger.error(f"Error retrieving guide: {e}")
            return None
    
    def search_guides(self, query: str, limit: int = 10) -> List[Dict[str, Any]]:
        """
        Search guides in the embedding database
        
        Args:
            query: Search query
            limit: Maximum number of results
            
        Returns:
            List of matching guides
        """
        if not self.is_initialized:
            logger.error("GuideService not initialized")
            return []
        
        try:
            return self.embedding_db.search_guides(query, limit)
        except Exception as e:
            logger.error(f"Error searching guides: {e}")
            return []
    
    def get_all_guides(self) -> List[Dict[str, Any]]:
        """
        Retrieve all guides from the embedding database
        
        Returns:
            List of all stored guides
        """
        if not self.is_initialized:
            logger.error("GuideService not initialized")
            return []
        
        try:
            return self.embedding_db.get_all_guides()
        except Exception as e:
            logger.error(f"Error retrieving all guides: {e}")
            return []
    
    def get_database_stats(self) -> Dict[str, Any]:
        """
        Get embedding database statistics
        
        Returns:
            Dictionary with database statistics
        """
        if not self.is_initialized:
            return {"error": "GuideService not initialized"}
        
        try:
            return self.embedding_db.get_stats()
        except Exception as e:
            logger.error(f"Error getting database stats: {e}")
            return {"error": str(e)}
    
    def is_ready(self) -> bool:
        """
        Check if service is ready
        
        Returns:
            True if service is initialized and ready
        """
        return self.is_initialized
    
    def delete_guide(self, class_name: str, spec_name: str, guide_type: str = "overview-pve-dps") -> bool:
        """
        Delete a specific guide from the embedding database
        
        Args:
            class_name: Class name
            spec_name: Spec name
            guide_type: Guide type
            
        Returns:
            True if successful, False otherwise
        """
        if not self.is_initialized:
            logger.error("GuideService not initialized")
            return False
        
        try:
            return self.embedding_db.delete_guide(class_name, spec_name, guide_type)
        except Exception as e:
            logger.error(f"Error deleting guide: {e}")
            return False
    
    def clear_all_guides(self) -> bool:
        """
        Clear all guides from the embedding database
        
        Returns:
            True if successful, False otherwise
        """
        if not self.is_initialized:
            logger.error("GuideService not initialized")
            return False
        
        try:
            return self.embedding_db.clear_all_guides()
        except Exception as e:
            logger.error(f"Error clearing all guides: {e}")
            return False 