import logging
from typing import Dict, Any, Optional

from business.llm_service import LLMService
from connector.embedding_connector import EmbeddingConnector

logger = logging.getLogger(__name__)

class LLMHandler:
    """Handler layer for LLM operations"""
    
    def __init__(self, llm_service: LLMService):
        self.llm_service = llm_service
    
    def ask_question(self, question: str) -> Dict[str, Any]:
        """
        Handle asking a question to the LLM with RAG
        
        Args:
            question: User's question about WoW classes
            
        Returns:
            Dictionary with response data
        """
        try:
            logger.info(f"Handling question: {question}")
            
            # Validate input
            if not question or not question.strip():
                return {
                    "success": False,
                    "error": "Question cannot be empty",
                    "answer": None,
                    "sources": []
                }
            
            # Process question through LLM service
            result = self.llm_service.ask_question(question.strip())
            
            return result
            
        except Exception as e:
            logger.error(f"Error handling question: {e}")
            return {
                "success": False,
                "error": f"Internal server error: {str(e)}",
                "answer": None,
                "sources": []
            }
    
    def get_llm_status(self) -> Dict[str, Any]:
        """
        Get LLM service status and information
        
        Returns:
            Dictionary with LLM service status
        """
        try:
            llm_info = self.llm_service.get_llm_info()
            
            return {
                "success": True,
                "llm_service": llm_info,
                "ready": self.llm_service.is_ready()
            }
            
        except Exception as e:
            logger.error(f"Error getting LLM status: {e}")
            return {
                "success": False,
                "error": f"Error getting LLM status: {str(e)}",
                "llm_service": None,
                "ready": False
            }
    
    def test_llm_connection(self) -> Dict[str, Any]:
        """
        Test LLM connection with a simple question
        
        Returns:
            Dictionary with test result
        """
        try:
            # Simple test question
            test_question = "What is the basic rotation for Fury Warrior?"
            result = self.llm_service.ask_question(test_question)
            
            return {
                "success": True,
                "test_question": test_question,
                "llm_working": result["success"],
                "response_received": result["answer"] is not None,
                "sources_found": len(result.get("sources", []))
            }
            
        except Exception as e:
            logger.error(f"Error testing LLM connection: {e}")
            return {
                "success": False,
                "error": f"LLM connection test failed: {str(e)}",
                "llm_working": False,
                "response_received": False,
                "sources_found": 0
            } 