import logging
from typing import Dict, List, Optional, Any
from fastapi import HTTPException

from business.scraper_service import ScraperService
from business.guide_service import GuideService

logger = logging.getLogger(__name__)

class GuideHandler:
    """Handler for guide-related HTTP requests"""
    
    def __init__(self, scraper_service: ScraperService, guide_service: GuideService):
        self.scraper_service = scraper_service
        self.guide_service = guide_service
    
    def scrape_guide(self, class_name: str, spec_name: str, guide_type: str = "overview-pve-dps") -> Dict[str, Any]:
        """
        Handle scraping a specific guide
        
        Args:
            class_name: Class name
            spec_name: Spec name
            guide_type: Guide type
            
        Returns:
            Dictionary with scraping result
        """
        try:
            result = self.scraper_service.scrape_guide(class_name, spec_name, guide_type)
            
            if result["success"]:
                return {
                    "success": True,
                    "message": f"Successfully scraped guide for {class_name} - {spec_name}",
                    "data": result.get("data"),
                    "url": result.get("url")
                }
            else:
                return {
                    "success": False,
                    "message": f"Failed to scrape guide: {result.get('error', 'Unknown error')}",
                    "url": result.get("url")
                }
                
        except Exception as e:
            logger.error(f"Error in scrape_guide handler: {e}")
            raise HTTPException(status_code=500, detail=f"Error scraping guide: {str(e)}")
    
    def scrape_all_guides(self, save_to_file: bool = True, filename: str = "scraped_guides.json", 
                         store_in_embedding_db: bool = True) -> Dict[str, Any]:
        """
        Handle scraping all guides
        
        Args:
            save_to_file: Whether to save to file
            filename: Output filename
            store_in_embedding_db: Whether to store in embedding database
            
        Returns:
            Dictionary with scraping results
        """
        try:
            # Scrape all guides
            results = self.scraper_service.scrape_all_guides()
            
            # Count successful scrapes
            successful_scrapes = sum(1 for result in results if result["success"])
            total_scrapes = len(results)
            
            # Save to file if requested
            file_saved = False
            if save_to_file:
                file_saved = self.scraper_service.save_scraped_data(results, filename)
            
            # Store in embedding database if requested
            embedding_db_result = None
            if store_in_embedding_db:
                embedding_db_result = self.guide_service.store_all_guides(results)
            
            response_data = {
                "total_scrapes": total_scrapes,
                "successful_scrapes": successful_scrapes,
                "results": results
            }
            
            if embedding_db_result:
                response_data["embedding_db"] = embedding_db_result
            
            if file_saved:
                response_data["file_saved"] = True
                response_data["filename"] = filename
            
            return {
                "success": True,
                "message": f"Scraped {successful_scrapes}/{total_scrapes} guides successfully",
                "data": response_data
            }
            
        except Exception as e:
            logger.error(f"Error in scrape_all_guides handler: {e}")
            raise HTTPException(status_code=500, detail=f"Error scraping all guides: {str(e)}")
    
    def get_classes(self) -> Dict[str, Any]:
        """
        Handle getting all classes
        
        Returns:
            Dictionary with classes data
        """
        try:
            classes_data = self.scraper_service.get_classes_data()
            return {"classes": classes_data}
        except Exception as e:
            logger.error(f"Error in get_classes handler: {e}")
            raise HTTPException(status_code=500, detail=f"Error loading classes: {str(e)}")
    
    def get_class_specs(self, class_name: str) -> Dict[str, Any]:
        """
        Handle getting specializations for a class
        
        Args:
            class_name: Class name
            
        Returns:
            Dictionary with class specs
        """
        try:
            class_specs = self.scraper_service.get_class_specs(class_name)
            if class_specs:
                return class_specs
            else:
                raise HTTPException(status_code=404, detail=f"Class '{class_name}' not found")
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Error in get_class_specs handler: {e}")
            raise HTTPException(status_code=500, detail=f"Error loading class specs: {str(e)}")
    
    def store_guide_in_embedding_db(self, class_name: str, spec_name: str, guide_type: str = "overview-pve-dps") -> Dict[str, Any]:
        """
        Handle scraping and storing a guide in embedding database
        
        Args:
            class_name: Class name
            spec_name: Spec name
            guide_type: Guide type
            
        Returns:
            Dictionary with result
        """
        try:
            # First scrape the guide
            result = self.scraper_service.scrape_guide(class_name, spec_name, guide_type)
            
            if not result["success"]:
                return {
                    "success": False,
                    "message": f"Failed to scrape guide: {result.get('error', 'Unknown error')}"
                }
            
            # Store in embedding database
            storage_success = self.guide_service.store_guide(result)
            
            if storage_success:
                return {
                    "success": True,
                    "message": f"Successfully scraped and stored guide for {class_name} - {spec_name}",
                    "data": result.get("data")
                }
            else:
                return {
                    "success": False,
                    "message": "Guide scraped but failed to store in embedding database"
                }
                
        except Exception as e:
            logger.error(f"Error in store_guide_in_embedding_db handler: {e}")
            raise HTTPException(status_code=500, detail=f"Error storing guide: {str(e)}")
    
    def get_guide_from_embedding_db(self, class_name: str, spec_name: str, guide_type: str = "overview-pve-dps") -> Dict[str, Any]:
        """
        Handle retrieving a guide from embedding database
        
        Args:
            class_name: Class name
            spec_name: Spec name
            guide_type: Guide type
            
        Returns:
            Dictionary with guide data
        """
        try:
            guide_data = self.guide_service.get_guide(class_name, spec_name, guide_type)
            
            if guide_data:
                return {
                    "success": True,
                    "message": f"Retrieved guide for {class_name} - {spec_name}",
                    "data": guide_data
                }
            else:
                return {
                    "success": False,
                    "message": f"Guide not found for {class_name} - {spec_name}"
                }
                
        except Exception as e:
            logger.error(f"Error in get_guide_from_embedding_db handler: {e}")
            raise HTTPException(status_code=500, detail=f"Error retrieving guide: {str(e)}")
    
    def search_guides_in_embedding_db(self, query: str, limit: int = 10) -> Dict[str, Any]:
        """
        Handle searching guides in embedding database
        
        Args:
            query: Search query
            limit: Maximum number of results
            
        Returns:
            Dictionary with search results
        """
        try:
            results = self.guide_service.search_guides(query, limit)
            
            return {
                "success": True,
                "message": f"Found {len(results)} guides matching '{query}'",
                "data": {"results": results, "query": query, "limit": limit}
            }
            
        except Exception as e:
            logger.error(f"Error in search_guides_in_embedding_db handler: {e}")
            raise HTTPException(status_code=500, detail=f"Error searching guides: {str(e)}")
    
    def get_embedding_db_stats(self) -> Dict[str, Any]:
        """
        Handle getting embedding database statistics
        
        Returns:
            Dictionary with database stats
        """
        try:
            stats = self.guide_service.get_database_stats()
            
            return {
                "success": True,
                "message": "Retrieved embedding database statistics",
                "stats": stats
            }
            
        except Exception as e:
            logger.error(f"Error in get_embedding_db_stats handler: {e}")
            raise HTTPException(status_code=500, detail=f"Error getting database stats: {str(e)}")
    
    def get_all_guides_from_embedding_db(self) -> Dict[str, Any]:
        """
        Handle getting all guides from embedding database
        
        Returns:
            Dictionary with all guides
        """
        try:
            guides = self.guide_service.get_all_guides()
            
            return {
                "success": True,
                "message": f"Retrieved {len(guides)} guides from embedding database",
                "data": {"guides": guides, "total_count": len(guides)}
            }
            
        except Exception as e:
            logger.error(f"Error in get_all_guides_from_embedding_db handler: {e}")
            raise HTTPException(status_code=500, detail=f"Error retrieving all guides: {str(e)}")
    
    def force_update_guide_in_embedding_db(self, class_name: str, spec_name: str, guide_type: str = "overview-pve-dps") -> Dict[str, Any]:
        """
        Handle force updating a guide in embedding database (re-scrape and replace)
        
        Args:
            class_name: Class name
            spec_name: Spec name
            guide_type: Guide type
            
        Returns:
            Dictionary with result
        """
        try:
            # First scrape the guide
            result = self.scraper_service.scrape_guide(class_name, spec_name, guide_type)
            
            if not result["success"]:
                return {
                    "success": False,
                    "message": f"Failed to scrape guide: {result.get('error', 'Unknown error')}"
                }
            
            # Force update in embedding database (will replace existing)
            storage_success = self.guide_service.store_guide(result)
            
            if storage_success:
                return {
                    "success": True,
                    "message": f"Successfully force updated guide for {class_name} - {spec_name}",
                    "data": result.get("data")
                }
            else:
                return {
                    "success": False,
                    "message": "Guide scraped but failed to update in embedding database"
                }
                
        except Exception as e:
            logger.error(f"Error in force_update_guide_in_embedding_db handler: {e}")
            raise HTTPException(status_code=500, detail=f"Error force updating guide: {str(e)}")
    
    def get_guide_last_updated(self, class_name: str, spec_name: str, guide_type: str = "overview-pve-dps") -> Dict[str, Any]:
        """
        Handle getting the last updated timestamp for a guide
        
        Args:
            class_name: Class name
            spec_name: Spec name
            guide_type: Guide type
            
        Returns:
            Dictionary with last updated info
        """
        try:
            guide_data = self.guide_service.get_guide(class_name, spec_name, guide_type)
            
            if guide_data:
                return {
                    "success": True,
                    "message": f"Retrieved last updated info for {class_name} - {spec_name}",
                    "data": {
                        "class_name": class_name,
                        "spec_name": spec_name,
                        "guide_type": guide_type,
                        "last_updated": guide_data.get("stored_at"),
                        "url": guide_data.get("url")
                    }
                }
            else:
                return {
                    "success": False,
                    "message": f"Guide not found for {class_name} - {spec_name}"
                }
                
        except Exception as e:
            logger.error(f"Error in get_guide_last_updated handler: {e}")
            raise HTTPException(status_code=500, detail=f"Error getting last updated info: {str(e)}")
    
    def delete_guide_from_embedding_db(self, class_name: str, spec_name: str, guide_type: str = "overview-pve-dps") -> Dict[str, Any]:
        """
        Handle deleting a guide from embedding database
        
        Args:
            class_name: Class name
            spec_name: Spec name
            guide_type: Guide type
            
        Returns:
            Dictionary with result
        """
        try:
            success = self.guide_service.delete_guide(class_name, spec_name, guide_type)
            
            if success:
                return {
                    "success": True,
                    "message": f"Successfully deleted guide for {class_name} - {spec_name}"
                }
            else:
                return {
                    "success": False,
                    "message": f"Failed to delete guide for {class_name} - {spec_name}"
                }
                
        except Exception as e:
            logger.error(f"Error in delete_guide_from_embedding_db handler: {e}")
            raise HTTPException(status_code=500, detail=f"Error deleting guide: {str(e)}")
    
    def clear_all_guides_from_embedding_db(self) -> Dict[str, Any]:
        """
        Handle clearing all guides from embedding database
        
        Returns:
            Dictionary with result
        """
        try:
            success = self.guide_service.clear_all_guides()
            
            if success:
                return {
                    "success": True,
                    "message": "Successfully cleared all guides from embedding database"
                }
            else:
                return {
                    "success": False,
                    "message": "Failed to clear all guides from embedding database"
                }
                
        except Exception as e:
            logger.error(f"Error in clear_all_guides_from_embedding_db handler: {e}")
            raise HTTPException(status_code=500, detail=f"Error clearing all guides: {str(e)}") 