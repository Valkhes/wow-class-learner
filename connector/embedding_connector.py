import chromadb
from chromadb.config import Settings
import logging
from typing import List, Dict, Optional, Any
from datetime import datetime
import os
import json
from sentence_transformers import SentenceTransformer
import hashlib

from connector.embedding_db import EmbeddingDBInterface

logger = logging.getLogger(__name__)

class EmbeddingConnector(EmbeddingDBInterface):
    """Embedding database connector for storing and searching document embeddings"""
    
    def __init__(self, db_path: str = "chroma_db", collection_name: str = "wow_guides"):
        self.db_path = db_path
        self.collection_name = collection_name
        self.client = None
        self.collection = None
        self.embedding_model = None
        self.is_setup = False
    
    def setup(self) -> bool:
        """Setup embedding database and collection"""
        try:
            logger.info(f"Setting up embedding database at {self.db_path}")
            
            # Create ChromaDB client with persistent storage
            self.client = chromadb.PersistentClient(
                path=self.db_path,
                settings=Settings(
                    anonymized_telemetry=False,
                    allow_reset=True
                )
            )
            
            # Get or create collection
            try:
                self.collection = self.client.get_collection(name=self.collection_name)
                logger.info(f"Loaded existing collection: {self.collection_name}")
            except:
                self.collection = self.client.create_collection(
                    name=self.collection_name,
                    metadata={"description": "WoW Class Guides"}
                )
                logger.info(f"Created new collection: {self.collection_name}")
            
            # Initialize embedding model
            logger.info("Loading sentence transformer model...")
            self.embedding_model = SentenceTransformer('all-MiniLM-L6-v2')
            
            self.is_setup = True
            logger.info("Embedding database setup completed successfully")
            return True
            
        except Exception as e:
            logger.error(f"Error setting up embedding database: {e}")
            return False
    
    def _generate_embedding(self, text: str) -> List[float]:
        """Generate embedding for text"""
        if not self.embedding_model:
            raise RuntimeError("Embedding model not initialized")
        
        # Clean and truncate text if too long
        cleaned_text = text.strip()
        if len(cleaned_text) > 8000:  # Limit text length
            cleaned_text = cleaned_text[:8000]
        
        # Generate embedding
        embedding = self.embedding_model.encode(cleaned_text)
        return embedding.tolist()
    
    def _generate_id(self, class_name: str, spec_name: str, guide_type: str) -> str:
        """Generate unique ID for guide"""
        content = f"{class_name}_{spec_name}_{guide_type}"
        return hashlib.md5(content.encode()).hexdigest()
    
    def store_guide(self, guide_data: Dict[str, Any]) -> bool:
        """Store a guide in the embedding database"""
        if not self.is_setup:
            logger.error("Embedding database not set up. Call setup() first.")
            return False
        
        try:
            if not guide_data.get("success", False):
                logger.warning("Attempting to store failed guide data")
                return False
            
            # Extract data
            class_name = guide_data.get("class_name", "")
            spec_name = guide_data.get("spec_name", "")
            guide_type = guide_data.get("guide_type", "")
            content = guide_data.get("data", {}).get("content", "")
            metadata = guide_data.get("data", {}).get("metadata", {})
            url = guide_data.get("url", "")
            
            if not content:
                logger.warning("No content to store")
                return False
            
            # Generate embedding
            embedding = self._generate_embedding(content)
            
            # Generate unique ID
            doc_id = self._generate_id(class_name, spec_name, guide_type)
            
            # Prepare metadata
            doc_metadata = {
                "class_name": class_name,
                "spec_name": spec_name,
                "guide_type": guide_type,
                "url": url,
                "title": metadata.get("title", ""),
                "description": metadata.get("description", ""),
                "stored_at": datetime.now().isoformat(),
                **metadata
            }
            
            # Store in database
            self.collection.add(
                embeddings=[embedding],
                documents=[content],
                metadatas=[doc_metadata],
                ids=[doc_id]
            )
            
            logger.info(f"Stored guide in embedding database: {class_name} - {spec_name}")
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
            doc_id = self._generate_id(class_name, spec_name, guide_type)
            
            # Query by ID
            results = self.collection.get(
                ids=[doc_id],
                include=["documents", "metadatas", "embeddings"]
            )
            
            if results["ids"]:
                metadata = results["metadatas"][0]
                content = results["documents"][0]
                
                return {
                    "class_name": metadata["class_name"],
                    "spec_name": metadata["spec_name"],
                    "guide_type": metadata["guide_type"],
                    "url": metadata["url"],
                    "content": content,
                    "metadata": metadata,
                    "stored_at": metadata["stored_at"]
                }
            else:
                logger.warning(f"Guide not found: {class_name} - {spec_name}")
                return None
                
        except Exception as e:
            logger.error(f"Error retrieving guide from embedding database: {e}")
            return None
    
    def search_guides(self, query: str, limit: int = 10) -> List[Dict[str, Any]]:
        """Search guides in the embedding database using semantic search"""
        if not self.is_setup:
            logger.error("Embedding database not set up. Call setup() first.")
            return []
        
        try:
            # Generate query embedding
            query_embedding = self._generate_embedding(query)
            
            # Search in database
            results = self.collection.query(
                query_embeddings=[query_embedding],
                n_results=limit,
                include=["documents", "metadatas", "distances"]
            )
            
            guides = []
            for i in range(len(results["ids"][0])):
                doc_id = results["ids"][0][i]
                metadata = results["metadatas"][0][i]
                content = results["documents"][0][i]
                distance = results["distances"][0][i]
                
                guides.append({
                    "id": doc_id,
                    "class_name": metadata["class_name"],
                    "spec_name": metadata["spec_name"],
                    "guide_type": metadata["guide_type"],
                    "url": metadata["url"],
                    "content": content,
                    "metadata": metadata,
                    "similarity_score": 1 - distance,  # Convert distance to similarity
                    "stored_at": metadata["stored_at"]
                })
            
            logger.info(f"Found {len(guides)} guides matching '{query}'")
            return guides
            
        except Exception as e:
            logger.error(f"Error searching guides in embedding database: {e}")
            return []
    
    def get_all_guides(self) -> List[Dict[str, Any]]:
        """Retrieve all guides from the embedding database"""
        if not self.is_setup:
            logger.error("Embedding database not set up. Call setup() first.")
            return []
        
        try:
            # Get all documents
            results = self.collection.get(
                include=["documents", "metadatas", "embeddings"]
            )
            
            guides = []
            for i in range(len(results["ids"])):
                doc_id = results["ids"][i]
                metadata = results["metadatas"][i]
                content = results["documents"][i]
                
                guides.append({
                    "id": doc_id,
                    "class_name": metadata["class_name"],
                    "spec_name": metadata["spec_name"],
                    "guide_type": metadata["guide_type"],
                    "url": metadata["url"],
                    "content": content,
                    "metadata": metadata,
                    "stored_at": metadata["stored_at"]
                })
            
            logger.info(f"Retrieved {len(guides)} guides from embedding database")
            return guides
            
        except Exception as e:
            logger.error(f"Error retrieving all guides from embedding database: {e}")
            return []
    
    def get_stats(self) -> Dict[str, Any]:
        """Get embedding database statistics"""
        if not self.is_setup:
            logger.error("Embedding database not set up. Call setup() first.")
            return {}
        
        try:
            # Get collection count
            count = self.collection.count()
            
            # Get unique classes and specs
            all_guides = self.get_all_guides()
            classes = set(guide["class_name"] for guide in all_guides)
            specs = set(guide["spec_name"] for guide in all_guides)
            
            return {
                "total_guides": count,
                "unique_classes": len(classes),
                "unique_specs": len(specs),
                "classes": list(classes),
                "specs": list(specs),
                "database_path": self.db_path,
                "collection_name": self.collection_name,
                "embedding_model": "all-MiniLM-L6-v2"
            }
            
        except Exception as e:
            logger.error(f"Error getting database stats: {e}")
            return {}
    
    def delete_guide(self, class_name: str, spec_name: str, guide_type: str = "overview-pve-dps") -> bool:
        """Delete a specific guide from the embedding database"""
        if not self.is_setup:
            logger.error("Embedding database not set up. Call setup() first.")
            return False
        
        try:
            doc_id = self._generate_id(class_name, spec_name, guide_type)
            self.collection.delete(ids=[doc_id])
            logger.info(f"Deleted guide: {class_name} - {spec_name}")
            return True
            
        except Exception as e:
            logger.error(f"Error deleting guide from embedding database: {e}")
            return False
    
    def clear_all_guides(self) -> bool:
        """Clear all guides from the embedding database"""
        if not self.is_setup:
            logger.error("Embedding database not set up. Call setup() first.")
            return False
        
        try:
            self.collection.delete(where={})
            logger.info("Cleared all guides from embedding database")
            return True
            
        except Exception as e:
            logger.error(f"Error clearing all guides from embedding database: {e}")
            return False

def create_embedding_connector(db_path: str = "chroma_db") -> EmbeddingConnector:
    """Factory function to create embedding connector"""
    return EmbeddingConnector(db_path=db_path) 