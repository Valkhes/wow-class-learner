import logging
import re
from typing import Dict, Any, Optional

from business.litellm_service import LiteLLMService, LLMResponse
from connector.embedding_connector import EmbeddingConnector

logger = logging.getLogger(__name__)

class LiteLLMHandler:
    """Handler layer for LiteLLM operations with monitoring and caching"""
    
    def __init__(self, litellm_service: LiteLLMService):
        self.litellm_service = litellm_service
        # Content filtering: List of inappropriate words to filter out
        self.inappropriate_words = {
            'hack', 'cheat', 'exploit', 'glitch', 'bug', 'dupe', 'bot', 'macro',
            'script', 'automation', 'third_party', 'unauthorized', 'illegal',
            'spam', 'advertisement', 'promotion', 'commercial', 'sell', 'buy',
            'trade', 'gold', 'currency', 'real_money', 'rmt', 'account_share'
        }
        
        # System prompt extraction attempts
        self.prompt_extraction_attempts = {
            'prompt', 'system', 'instruction', 'role', 'persona', 'identity',
            'what are you', 'who are you', 'tell me about yourself', 'your prompt',
            'system prompt', 'instructions', 'configuration', 'settings'
        }
    
    def _check_content_filter(self, question: str) -> Dict[str, Any]:
        """
        Check if question contains inappropriate content
        
        Args:
            question: User's question
            
        Returns:
            Dictionary with filter result (blocked: bool, reason: str)
        """
        # Convert to lowercase for case-insensitive matching
        question_lower = question.lower()
        
        # Check for inappropriate words
        found_words = []
        for word in self.inappropriate_words:
            if word in question_lower:
                found_words.append(word)
        
        if found_words:
            return {
                "blocked": True,
                "reason": f"Question contains inappropriate content: {', '.join(found_words)}",
                "found_words": found_words
            }
        
        # Check for system prompt extraction attempts
        for attempt in self.prompt_extraction_attempts:
            if attempt in question_lower:
                return {
                    "blocked": True,
                    "reason": "This type of question is not allowed for security reasons",
                    "blocked_type": "prompt_extraction"
                }
        
        # Check for excessive special characters (potential spam)
        special_char_ratio = len(re.findall(r'[!@#$%^&*()_+\-=\[\]{};\':"\\|,.<>/?]', question)) / len(question) if question else 0
        if special_char_ratio > 0.3:  # More than 30% special characters
            return {
                "blocked": True,
                "reason": "Question contains too many special characters (potential spam)",
                "special_char_ratio": special_char_ratio
            }
        
        return {"blocked": False, "reason": ""}
    
    def ask_question(self, question: str) -> Dict[str, Any]:
        """
        Handle asking a question to the LLM with RAG and monitoring
        
        Args:
            question: User's question about WoW classes
            
        Returns:
            Dictionary with response data including monitoring info
        """
        try:
            logger.info(f"Handling question with LiteLLM: {question}")
            
            # Validate input
            if not question or not question.strip():
                return {
                    "success": False,
                    "error": "Question cannot be empty",
                    "answer": None,
                    "sources": [],
                    "metadata": {}
                }
            
            # Guardrails: Check question length
            question_length = len(question.strip())
            if question_length > 200:
                return {
                    "success": False,
                    "error": f"Question too long. Maximum 200 characters allowed. Current length: {question_length}",
                    "answer": None,
                    "sources": [],
                    "metadata": {"question_length": question_length, "max_length": 200}
                }
            
            # Guardrails: Check content filter
            content_filter_result = self._check_content_filter(question.strip())
            if content_filter_result["blocked"]:
                return {
                    "success": False,
                    "error": content_filter_result["reason"],
                    "answer": None,
                    "sources": [],
                    "metadata": {"content_filtered": True, "filter_reason": content_filter_result["reason"]}
                }
            
            # Process question through LiteLLM service
            result: LLMResponse = self.litellm_service.ask_question(question.strip())
            
            # Convert LLMResponse to dictionary format
            response_dict = {
                "success": result.success,
                "answer": result.answer,
                "error": result.error,
                "sources": result.sources,
                "metadata": result.metadata
            }
            
            return response_dict
            
        except Exception as e:
            logger.error(f"Error handling question with LiteLLM: {e}")
            return {
                "success": False,
                "error": f"Internal server error: {str(e)}",
                "answer": None,
                "sources": [],
                "metadata": {"duration": 0}
            }
    

    
    def get_litellm_status(self) -> Dict[str, Any]:
        """
        Get LiteLLM service status and information
        
        Returns:
            Dictionary with LiteLLM service status
        """
        try:
            service_info = self.litellm_service.get_service_info()
            
            return {
                "success": True,
                "litellm_service": service_info,
                "ready": self.litellm_service.is_ready(),
                "features": {
                    "caching": service_info.get("cache_enabled", False),
                    "cost_monitoring": True,
                    "rate_limiting": True,
                    "prometheus_metrics": True
                }
            }
            
        except Exception as e:
            logger.error(f"Error getting LiteLLM status: {e}")
            return {
                "success": False,
                "error": f"Error getting LiteLLM status: {str(e)}",
                "litellm_service": None,
                "ready": False,
                "features": {}
            }
    
    def test_litellm_connection(self) -> Dict[str, Any]:
        """
        Test LiteLLM connection with a simple question
        
        Returns:
            Dictionary with test result
        """
        try:
            # Simple test question
            test_question = "What is the basic rotation for Fury Warrior?"
            result: LLMResponse = self.litellm_service.ask_question(test_question)
            
            return {
                "success": True,
                "test_question": test_question,
                "llm_working": result.success,
                "response_received": result.answer is not None,
                "sources_found": len(result.sources),
                "cache_hit": result.metadata.get("cache_hit", False),
                "duration": result.metadata.get("duration", 0),
                "tokens_used": result.metadata.get("tokens_used", 0),
                "cost_usd": result.metadata.get("cost_usd", 0.0)
            }
            
        except Exception as e:
            logger.error(f"Error testing LiteLLM connection: {e}")
            return {
                "success": False,
                "error": f"LiteLLM connection test failed: {str(e)}",
                "llm_working": False,
                "response_received": False,
                "sources_found": 0,
                "cache_hit": False,
                "duration": 0,
                "tokens_used": 0,
                "cost_usd": 0.0
            }
    
    def get_cost_summary(self) -> Dict[str, Any]:
        """
        Get cost summary for LLM usage
        
        Returns:
            Dictionary with cost summary
        """
        try:
            # This would typically query a database or metrics storage
            # For now, we return a placeholder
            return {
                "success": True,
                "cost_summary": {
                    "total_cost_usd": 0.0,
                    "daily_cost_usd": 0.0,
                    "monthly_cost_usd": 0.0,
                    "cost_by_model": {},
                    "budget_limits": self.litellm_service.cost_limits
                }
            }
            
        except Exception as e:
            logger.error(f"Error getting cost summary: {e}")
            return {
                "success": False,
                "error": f"Error getting cost summary: {str(e)}",
                "cost_summary": {}
            }
    
    def get_performance_metrics(self) -> Dict[str, Any]:
        """
        Get performance metrics for LLM calls
        
        Returns:
            Dictionary with performance metrics
        """
        try:
            # This would typically query metrics storage
            # For now, we return a placeholder
            return {
                "success": True,
                "performance_metrics": {
                    "average_response_time": 0.0,
                    "cache_hit_rate": 0.0,
                    "error_rate": 0.0,
                    "requests_per_minute": 0,
                    "total_requests": 0
                }
            }
            
        except Exception as e:
            logger.error(f"Error getting performance metrics: {e}")
            return {
                "success": False,
                "error": f"Error getting performance metrics: {str(e)}",
                "performance_metrics": {}
            } 