from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from typing import Dict, Any, Optional
import logging

from router.litellm_handler import LiteLLMHandler
from business.litellm_service import LiteLLMService
from business.monitoring_service import MonitoringService

logger = logging.getLogger(__name__)

# Pydantic models for request/response
class QuestionRequest(BaseModel):
    question: str

class QuestionResponse(BaseModel):
    success: bool
    answer: Optional[str] = None
    error: Optional[str] = None
    sources: list = []
    metadata: Dict[str, Any] = {}

class StatusResponse(BaseModel):
    success: bool
    litellm_service: Dict[str, Any]
    ready: bool
    features: Dict[str, Any]

class TestResponse(BaseModel):
    success: bool
    test_question: str
    llm_working: bool
    response_received: bool
    sources_found: int
    cache_hit: bool
    duration: float
    tokens_used: int
    cost_usd: float

class CostSummaryResponse(BaseModel):
    success: bool
    cost_summary: Dict[str, Any]

class PerformanceMetricsResponse(BaseModel):
    success: bool
    performance_metrics: Dict[str, Any]

# Router setup
litellm_router = APIRouter(prefix="/litellm", tags=["LiteLLM"])

# Dependency injection
def get_litellm_handler() -> LiteLLMHandler:
    """Dependency to get LiteLLM handler"""
    # This would typically be injected from your main app
    # For now, we'll create a placeholder
    from connector.embedding_connector import EmbeddingConnector
    from business.litellm_service import LiteLLMService
    
    embedding_connector = EmbeddingConnector()
    litellm_service = LiteLLMService(embedding_connector)
    litellm_service.initialize()
    
    return LiteLLMHandler(litellm_service)

def get_monitoring_service() -> MonitoringService:
    """Dependency to get monitoring service"""
    return MonitoringService()



@litellm_router.post("/ask-sync", response_model=QuestionResponse)
def ask_question_sync(
    request: QuestionRequest,
    handler: LiteLLMHandler = Depends(get_litellm_handler)
) -> QuestionResponse:
    """
    Ask a question using LiteLLM with RAG, caching, and monitoring (synchronous)
    
    Args:
        request: Question request
        handler: LiteLLM handler
        
    Returns:
        QuestionResponse with answer and metadata
    """
    try:
        result = handler.ask_question(request.question)
        return QuestionResponse(**result)
    except Exception as e:
        logger.error(f"Error in ask_question_sync endpoint: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@litellm_router.get("/status", response_model=StatusResponse)
def get_status(
    handler: LiteLLMHandler = Depends(get_litellm_handler)
) -> StatusResponse:
    """
    Get LiteLLM service status and information
    
    Args:
        handler: LiteLLM handler
        
    Returns:
        StatusResponse with service information
    """
    try:
        result = handler.get_litellm_status()
        return StatusResponse(**result)
    except Exception as e:
        logger.error(f"Error in get_status endpoint: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@litellm_router.get("/test", response_model=TestResponse)
def test_connection(
    handler: LiteLLMHandler = Depends(get_litellm_handler)
) -> TestResponse:
    """
    Test LiteLLM connection with a simple question
    
    Args:
        handler: LiteLLM handler
        
    Returns:
        TestResponse with test results
    """
    try:
        result = handler.test_litellm_connection()
        return TestResponse(**result)
    except Exception as e:
        logger.error(f"Error in test_connection endpoint: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@litellm_router.get("/cost-summary", response_model=CostSummaryResponse)
def get_cost_summary(
    handler: LiteLLMHandler = Depends(get_litellm_handler)
) -> CostSummaryResponse:
    """
    Get cost summary for LLM usage
    
    Args:
        handler: LiteLLM handler
        
    Returns:
        CostSummaryResponse with cost information
    """
    try:
        result = handler.get_cost_summary()
        return CostSummaryResponse(**result)
    except Exception as e:
        logger.error(f"Error in get_cost_summary endpoint: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@litellm_router.get("/performance", response_model=PerformanceMetricsResponse)
def get_performance_metrics(
    handler: LiteLLMHandler = Depends(get_litellm_handler)
) -> PerformanceMetricsResponse:
    """
    Get performance metrics for LLM calls
    
    Args:
        handler: LiteLLM handler
        
    Returns:
        PerformanceMetricsResponse with performance metrics
    """
    try:
        result = handler.get_performance_metrics()
        return PerformanceMetricsResponse(**result)
    except Exception as e:
        logger.error(f"Error in get_performance_metrics endpoint: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# Monitoring endpoints
@litellm_router.get("/metrics")
def get_prometheus_metrics(
    monitoring_service: MonitoringService = Depends(get_monitoring_service)
) -> str:
    """
    Get Prometheus metrics for LLM usage
    
    Args:
        monitoring_service: Monitoring service
        
    Returns:
        Prometheus metrics in text format
    """
    try:
        return monitoring_service.get_metrics()
    except Exception as e:
        logger.error(f"Error in get_prometheus_metrics endpoint: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@litellm_router.get("/metrics/content-type")
def get_metrics_content_type(
    monitoring_service: MonitoringService = Depends(get_monitoring_service)
) -> str:
    """
    Get content type for Prometheus metrics
    
    Args:
        monitoring_service: Monitoring service
        
    Returns:
        Content type string
    """
    return monitoring_service.get_metrics_content_type()

@litellm_router.get("/usage-summary")
def get_usage_summary(
    monitoring_service: MonitoringService = Depends(get_monitoring_service)
) -> Dict[str, Any]:
    """
    Get usage summary for LLM calls
    
    Args:
        monitoring_service: Monitoring service
        
    Returns:
        Dictionary with usage summary
    """
    try:
        return monitoring_service.get_usage_summary()
    except Exception as e:
        logger.error(f"Error in get_usage_summary endpoint: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@litellm_router.get("/cost-analysis")
def get_cost_analysis(
    monitoring_service: MonitoringService = Depends(get_monitoring_service)
) -> Dict[str, Any]:
    """
    Get cost analysis for LLM usage
    
    Args:
        monitoring_service: Monitoring service
        
    Returns:
        Dictionary with cost analysis
    """
    try:
        return monitoring_service.get_cost_analysis()
    except Exception as e:
        logger.error(f"Error in get_cost_analysis endpoint: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@litellm_router.get("/health")
def get_health_status(
    monitoring_service: MonitoringService = Depends(get_monitoring_service)
) -> Dict[str, Any]:
    """
    Get health status of the monitoring service
    
    Args:
        monitoring_service: Monitoring service
        
    Returns:
        Dictionary with health status
    """
    try:
        return monitoring_service.get_health_status()
    except Exception as e:
        logger.error(f"Error in get_health_status endpoint: {e}")
        raise HTTPException(status_code=500, detail=str(e)) 