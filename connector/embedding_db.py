import json
import logging
from typing import List, Dict, Optional, Any
from datetime import datetime
import os
from abc import ABC, abstractmethod

logger = logging.getLogger(__name__)

class EmbeddingDBInterface(ABC):
    """Abstract interface for embedding database operations"""
    
    @abstractmethod
    def setup(self) -> bool:
        """Setup the embedding database"""
        pass
    
    @abstractmethod
    def store_guide(self, guide_data: Dict[str, Any]) -> bool:
        """Store a guide in the embedding database"""
        pass
    
    @abstractmethod
    def get_guide(self, class_name: str, spec_name: str, guide_type: str = "overview-pve-dps") -> Optional[Dict[str, Any]]:
        """Retrieve a specific guide from the database"""
        pass
    
    @abstractmethod
    def search_guides(self, query: str, limit: int = 10) -> List[Dict[str, Any]]:
        """Search guides by query"""
        pass
    
    @abstractmethod
    def get_all_guides(self) -> List[Dict[str, Any]]:
        """Get all guides from the database"""
        pass
    
    @abstractmethod
    def get_stats(self) -> Dict[str, Any]:
        """Get database statistics"""
        pass

class FileBasedEmbeddingDB(EmbeddingDBInterface):
    """File-based implementation of embedding database"""
    
    def __init__(self, storage_dir: str = "embedding_db"):
        self.storage_dir = storage_dir
        self.is_setup = False
    
    def setup(self) -> bool:
        """Setup the embedding database directory"""
        try:
            if not os.path.exists(self.storage_dir):
                os.makedirs(self.storage_dir)
                logger.info(f"Created embedding database directory: {self.storage_dir}")
            
            # Create metadata file
            metadata_file = os.path.join(self.storage_dir, "metadata.json")
            if not os.path.exists(metadata_file):
                metadata = {
                    "created_at": datetime.now().isoformat(),
                    "total_guides": 0,
                    "classes": {},
                    "last_updated": None
                }
                with open(metadata_file, "w") as f:
                    json.dump(metadata, f, indent=2)
            
            self.is_setup = True
            logger.info("Embedding database setup completed successfully")
            return True
            
        except Exception as e:
            logger.error(f"Error setting up embedding database: {e}")
            return False
    
    def store_guide(self, guide_data: Dict[str, Any]) -> bool:
        """Store a guide in the embedding database"""
        if not self.is_setup:
            logger.error("Embedding database not set up. Call setup() first.")
            return False
        
        try:
            if not guide_data.get("success", False):
                logger.warning("Attempting to store failed guide data")
                return False
            
            # Extract relevant data
            class_name = guide_data.get("class_name", "")
            spec_name = guide_data.get("spec_name", "")
            guide_type = guide_data.get("guide_type", "")
            
            # Create filename
            filename = f"{class_name}_{spec_name}_{guide_type}.json"
            filepath = os.path.join(self.storage_dir, filename)
            
            # Prepare data for storage
            storage_data = {
                "class_name": class_name,
                "spec_name": spec_name,
                "guide_type": guide_type,
                "url": guide_data.get("url", ""),
                "content": guide_data.get("data", {}).get("content", ""),
                "metadata": guide_data.get("data", {}).get("metadata", {}),
                "timestamp": guide_data.get("data", {}).get("timestamp", datetime.now().timestamp()),
                "stored_at": datetime.now().isoformat()
            }
            
            # Save to file
            with open(filepath, "w", encoding="utf-8") as f:
                json.dump(storage_data, f, indent=2, ensure_ascii=False)
            
            # Update metadata
            self._update_metadata(class_name)
            
            logger.info(f"Stored guide in embedding database: {filename}")
            return True
            
        except Exception as e:
            logger.error(f"Error storing guide in embedding database: {e}")
            return False
    
    def get_guide(self, class_name: str, spec_name: str, guide_type: str = "overview-pve-dps") -> Optional[Dict[str, Any]]:
        """Retrieve a specific guide from the embedding database"""
        if not self.is_setup:
            logger.error("Embedding database not set up. Call setup() first.")
            return None
        
        try:
            filename = f"{class_name}_{spec_name}_{guide_type}.json"
            filepath = os.path.join(self.storage_dir, filename)
            
            if not os.path.exists(filepath):
                logger.warning(f"Guide not found in embedding database: {filename}")
                return None
            
            with open(filepath, "r", encoding="utf-8") as f:
                return json.load(f)
                
        except Exception as e:
            logger.error(f"Error retrieving guide from embedding database: {e}")
            return None
    
    def search_guides(self, query: str, limit: int = 10) -> List[Dict[str, Any]]:
        """Search guides in the embedding database"""
        if not self.is_setup:
            logger.error("Embedding database not set up. Call setup() first.")
            return []
        
        guides = self.get_all_guides()
        matching_guides = []
        
        query_lower = query.lower()
        
        for guide in guides:
            content = guide.get("content", "").lower()
            class_name = guide.get("class_name", "").lower()
            spec_name = guide.get("spec_name", "").lower()
            
            # Simple keyword matching
            if (query_lower in content or 
                query_lower in class_name or 
                query_lower in spec_name):
                matching_guides.append(guide)
        
        # Sort by relevance (simple implementation)
        matching_guides.sort(key=lambda x: x.get("content", "").lower().count(query_lower), reverse=True)
        
        return matching_guides[:limit]
    
    def get_all_guides(self) -> List[Dict[str, Any]]:
        """Retrieve all guides from the embedding database"""
        if not self.is_setup:
            logger.error("Embedding database not set up. Call setup() first.")
            return []
        
        guides = []
        
        try:
            for filename in os.listdir(self.storage_dir):
                if filename.endswith(".json") and filename != "metadata.json":
                    filepath = os.path.join(self.storage_dir, filename)
                    with open(filepath, "r", encoding="utf-8") as f:
                        guides.append(json.load(f))
            
            logger.info(f"Retrieved {len(guides)} guides from embedding database")
            return guides
            
        except Exception as e:
            logger.error(f"Error retrieving all guides from embedding database: {e}")
            return []
    
    def get_stats(self) -> Dict[str, Any]:
        """Get embedding database statistics"""
        if not self.is_setup:
            logger.error("Embedding database not set up. Call setup() first.")
            return {"error": "Database not set up"}
        
        try:
            metadata_file = os.path.join(self.storage_dir, "metadata.json")
            if os.path.exists(metadata_file):
                with open(metadata_file, "r") as f:
                    metadata = json.load(f)
            else:
                metadata = {"total_guides": 0, "classes": {}, "last_updated": None}
            
            # Update with current stats
            files = [f for f in os.listdir(self.storage_dir) if f.endswith(".json") and f != "metadata.json"]
            metadata["total_guides"] = len(files)
            metadata["storage_directory"] = self.storage_dir
            
            return metadata
            
        except Exception as e:
            logger.error(f"Error getting embedding database stats: {e}")
            return {"error": str(e)}
    
    def _update_metadata(self, class_name: str):
        """Update metadata with new guide"""
        try:
            metadata_file = os.path.join(self.storage_dir, "metadata.json")
            
            if os.path.exists(metadata_file):
                with open(metadata_file, "r") as f:
                    metadata = json.load(f)
            else:
                metadata = {"total_guides": 0, "classes": {}, "last_updated": None}
            
            # Update counts
            metadata["classes"][class_name] = metadata["classes"].get(class_name, 0) + 1
            metadata["last_updated"] = datetime.now().isoformat()
            
            # Count total guides
            files = [f for f in os.listdir(self.storage_dir) if f.endswith(".json") and f != "metadata.json"]
            metadata["total_guides"] = len(files)
            
            # Save updated metadata
            with open(metadata_file, "w") as f:
                json.dump(metadata, f, indent=2)
                
        except Exception as e:
            logger.error(f"Error updating metadata: {e}")

def create_embedding_db() -> EmbeddingDBInterface:
    """Factory function to create embedding database instance"""
    return FileBasedEmbeddingDB() 