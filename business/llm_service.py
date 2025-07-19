import logging
import os
from typing import List, Dict, Optional, Any
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.schema import HumanMessage, SystemMessage
from langchain.prompts import ChatPromptTemplate
from langchain.schema.output_parser import StrOutputParser
from langchain.schema.runnable import RunnablePassthrough

from connector.embedding_connector import EmbeddingConnector

logger = logging.getLogger(__name__)

class LLMService:
    """Business layer service for LLM operations with RAG"""
    
    def __init__(self, embedding_connector: EmbeddingConnector):
        self.embedding_connector = embedding_connector
        self.llm = None
        self.is_initialized = False
    
    def initialize(self) -> bool:
        """
        Initialize the LLM service with Gemini 2.0 Flash
        
        Returns:
            bool: True if initialization successful, False otherwise
        """
        try:
            logger.info("Initializing LLMService...")
            
            # Check for API key
            api_key = os.getenv("GOOGLE_API_KEY")
            if not api_key:
                logger.error("GOOGLE_API_KEY environment variable not set")
                return False
            
            # Initialize Gemini 2.0 Flash
            self.llm = ChatGoogleGenerativeAI(
                model="gemini-2.0-flash-exp",
                google_api_key=api_key,
                temperature=0.1,
                max_output_tokens=2048,
            )
            
            # Initialize embedding connector if not already done
            if not self.embedding_connector.is_setup:
                if not self.embedding_connector.setup():
                    logger.error("Failed to setup embedding connector")
                    return False
            
            self.is_initialized = True
            logger.info("LLMService initialized successfully")
            return True
            
        except Exception as e:
            logger.error(f"Error initializing LLMService: {e}")
            return False
    
    def create_rag_chain(self) -> Any:
        """
        Create a RAG chain that combines retrieval and generation
        
        Returns:
            LangChain RAG chain
        """
        if not self.is_initialized:
            raise RuntimeError("LLMService not initialized")
        
        # System prompt for WoW class guide assistance
        system_prompt = """You are an expert World of Warcraft class guide assistant. 
        You help players understand class mechanics, rotations, talents, and strategies.
        
        Use the provided context from WoWhead guides to answer questions accurately.
        Always cite your sources and be specific about class/spec information.
        
        If you don't have enough context to answer a question, say so and suggest what information would be needed."""
        
        # Create the RAG chain
        rag_chain = (
            {
                "context": self._retrieve_relevant_docs,
                "question": RunnablePassthrough()
            }
            | ChatPromptTemplate.from_messages([
                ("system", system_prompt),
                ("human", "Context: {context}\n\nQuestion: {question}\n\nAnswer:")
            ])
            | self.llm
            | StrOutputParser()
        )
        
        return rag_chain
    
    def _retrieve_relevant_docs(self, question: str) -> str:
        """
        Retrieve relevant documents from the embedding database
        
        Args:
            question: User's question
            
        Returns:
            Formatted context string from relevant guides
        """
        try:
            # Search for relevant guides
            search_results = self.embedding_connector.search_guides(question, limit=5)
            
            if not search_results:
                return "No relevant guides found."
            
            # Format the context
            context_parts = []
            for result in search_results:
                guide_info = f"Class: {result['class_name']}, Spec: {result['spec_name']}"
                content = result['content'][:1000]  # Limit content length
                context_parts.append(f"[{guide_info}]\n{content}\n")
            
            return "\n".join(context_parts)
            
        except Exception as e:
            logger.error(f"Error retrieving relevant docs: {e}")
            return "Error retrieving relevant guides."
    
    def ask_question(self, question: str) -> Dict[str, Any]:
        """
        Ask a question using RAG (Retrieval-Augmented Generation)
        
        Args:
            question: User's question about WoW classes
            
        Returns:
            Dictionary with answer and metadata
        """
        if not self.is_initialized:
            return {
                "success": False,
                "error": "LLMService not initialized",
                "answer": None,
                "sources": []
            }
        
        try:
            logger.info(f"Processing question: {question}")
            
            # Create RAG chain
            rag_chain = self.create_rag_chain()
            
            # Get answer
            answer = rag_chain.invoke(question)
            
            # Get sources for attribution
            search_results = self.embedding_connector.search_guides(question, limit=3)
            sources = []
            for result in search_results:
                sources.append({
                    "class_name": result["class_name"],
                    "spec_name": result["spec_name"],
                    "similarity_score": result["similarity_score"],
                    "url": result.get("url", ""),
                    "content_preview": result["content"][:200] + "..."
                })
            
            logger.info(f"Successfully answered question with {len(sources)} sources")
            
            return {
                "success": True,
                "answer": answer,
                "sources": sources,
                "question": question
            }
            
        except Exception as e:
            logger.error(f"Error processing question: {e}")
            return {
                "success": False,
                "error": str(e),
                "answer": None,
                "sources": []
            }
    
    def get_llm_info(self) -> Dict[str, Any]:
        """
        Get information about the LLM service
        
        Returns:
            Dictionary with LLM service information
        """
        return {
            "model": "gemini-2.0-flash-exp",
            "provider": "Google",
            "initialized": self.is_initialized,
            "embedding_connector_ready": self.embedding_connector.is_setup if self.embedding_connector else False
        }
    
    def is_ready(self) -> bool:
        """
        Check if service is ready
        
        Returns:
            True if service is initialized and ready
        """
        return self.is_initialized and self.llm is not None 