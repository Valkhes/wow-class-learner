from fastapi import APIRouter, Request, HTTPException, Depends
from pydantic import BaseModel, Field
from typing import Dict, Any, Optional

from router.llm_handler import LLMHandler

# Pydantic models for request/response
class QuestionRequest(BaseModel):
    question: str = Field(..., description="Question about WoW classes", min_length=1, max_length=1000)

class QuestionResponse(BaseModel):
    success: bool
    answer: Optional[str] = None
    sources: list = []
    question: Optional[str] = None
    error: Optional[str] = None

class LLMStatusResponse(BaseModel):
    success: bool
    llm_service: Optional[Dict[str, Any]] = None
    ready: bool = False
    error: Optional[str] = None

class TestResponse(BaseModel):
    success: bool
    test_question: Optional[str] = None
    llm_working: bool = False
    response_received: bool = False
    sources_found: int = 0
    error: Optional[str] = None

# Create router
llm_router = APIRouter(prefix="/api/v1/llm", tags=["LLM"])

def get_llm_handler(request: Request) -> LLMHandler:
    """Dependency to get LLM handler from request state"""
    handler = getattr(request.app.state, "llm_handler", None)
    if not handler:
        raise HTTPException(status_code=500, detail="LLM handler not available")
    return handler

@llm_router.post("/ask", response_model=QuestionResponse)
async def ask_question(
    request_data: QuestionRequest,
    llm_handler: LLMHandler = Depends(get_llm_handler)
):
    """
    Ask a question about WoW classes using LLM with RAG
    
    This endpoint uses Retrieval-Augmented Generation (RAG) to:
    1. Search the embedding database for relevant guides
    2. Use Gemini 2.0 Flash to generate an answer based on the retrieved context
    3. Return the answer with source attribution
    """
    try:
        result = llm_handler.ask_question(request_data.question)
        
        return QuestionResponse(
            success=result["success"],
            answer=result.get("answer"),
            sources=result.get("sources", []),
            question=result.get("question"),
            error=result.get("error")
        )
        
    except Exception as e:
        return QuestionResponse(
            success=False,
            error=f"Internal server error: {str(e)}"
        )

@llm_router.get("/status", response_model=LLMStatusResponse)
async def get_llm_status(
    llm_handler: LLMHandler = Depends(get_llm_handler)
):
    """
    Get LLM service status and configuration information
    """
    try:
        result = llm_handler.get_llm_status()
        
        return LLMStatusResponse(
            success=result["success"],
            llm_service=result.get("llm_service"),
            ready=result.get("ready", False),
            error=result.get("error")
        )
        
    except Exception as e:
        return LLMStatusResponse(
            success=False,
            error=f"Error getting LLM status: {str(e)}"
        )

@llm_router.post("/test", response_model=TestResponse)
async def test_llm_connection(
    llm_handler: LLMHandler = Depends(get_llm_handler)
):
    """
    Test LLM connection with a simple question
    
    This endpoint tests if the LLM service is working properly
    by asking a test question and checking the response.
    """
    try:
        result = llm_handler.test_llm_connection()
        
        return TestResponse(
            success=result["success"],
            test_question=result.get("test_question"),
            llm_working=result.get("llm_working", False),
            response_received=result.get("response_received", False),
            sources_found=result.get("sources_found", 0),
            error=result.get("error")
        )
        
    except Exception as e:
        return TestResponse(
            success=False,
            error=f"Error testing LLM connection: {str(e)}"
        )

@llm_router.get("/health")
async def llm_health_check(
    llm_handler: LLMHandler = Depends(get_llm_handler)
):
    """
    Simple health check for LLM service
    """
    try:
        status = llm_handler.get_llm_status()
        return {
            "status": "healthy" if status["ready"] else "unhealthy",
            "llm_ready": status["ready"],
            "service": "LLM Service"
        }
    except Exception as e:
        return {
            "status": "error",
            "error": str(e),
            "service": "LLM Service"
        } 