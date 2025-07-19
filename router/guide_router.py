from fastapi import APIRouter, HTTPException, Depends, Request
from pydantic import BaseModel
from typing import Optional, List
import json
import os

from router.guide_handler import GuideHandler

router = APIRouter(tags=["guides"])

class FetchGuideRequest(BaseModel):
    """Request model for fetching a guide"""
    class_name: Optional[str] = None
    spec_name: Optional[str] = None

class FetchGuideResponse(BaseModel):
    """Response model for guide fetch"""
    message: str
    guide_data: Optional[dict] = None

class ScrapeGuideRequest(BaseModel):
    """Request model for scraping a specific guide"""
    class_name: str
    spec_name: str
    guide_type: Optional[str] = "overview-pve-dps"

class ScrapeAllGuidesRequest(BaseModel):
    """Request model for scraping all guides"""
    save_to_file: Optional[bool] = True
    filename: Optional[str] = "scraped_guides.json"
    store_in_embedding_db: Optional[bool] = True

class ScrapeResponse(BaseModel):
    """Response model for scraping operations"""
    success: bool
    message: str
    data: Optional[dict] = None
    url: Optional[str] = None

class EmbeddingDBRequest(BaseModel):
    """Request model for embedding database operations"""
    class_name: Optional[str] = None
    spec_name: Optional[str] = None
    query: Optional[str] = None
    limit: Optional[int] = 10

class EmbeddingDBResponse(BaseModel):
    """Response model for embedding database operations"""
    success: bool
    message: str
    data: Optional[dict] = None
    stats: Optional[dict] = None

# Dependency injection function
def get_guide_handler(request: Request) -> GuideHandler:
    """Get guide handler from request state"""
    return request.app.state.guide_handler

@router.post("/fetch_guide", response_model=FetchGuideResponse)
async def fetch_guide(request: FetchGuideRequest):
    """
    Fetch a guide for a specific class and spec.
    Currently does nothing as requested.
    """
    # TODO: Implement guide fetching logic
    return FetchGuideResponse(
        message="Guide fetch endpoint created - implementation pending",
        guide_data=None
    )

@router.post("/scrape_guide", response_model=ScrapeResponse)
async def scrape_guide(request: ScrapeGuideRequest, handler: GuideHandler = Depends(get_guide_handler)):
    """
    Scrape a specific guide from WoWhead
    """
    result = handler.scrape_guide(request.class_name, request.spec_name, request.guide_type)
    
    return ScrapeResponse(
        success=result["success"],
        message=result["message"],
        data=result.get("data"),
        url=result.get("url")
    )

@router.post("/scrape_all_guides", response_model=ScrapeResponse)
async def scrape_all_guides(request: ScrapeAllGuidesRequest, handler: GuideHandler = Depends(get_guide_handler)):
    """
    Scrape guides for all classes and specializations
    """
    result = handler.scrape_all_guides(
        save_to_file=request.save_to_file,
        filename=request.filename,
        store_in_embedding_db=request.store_in_embedding_db
    )
    
    return ScrapeResponse(
        success=result["success"],
        message=result["message"],
        data=result.get("data")
    )

@router.get("/classes", response_model=dict)
async def get_classes(handler: GuideHandler = Depends(get_guide_handler)):
    """
    Get all available classes and specializations
    """
    return handler.get_classes()

@router.get("/classes/{class_name}/specs")
async def get_class_specs(class_name: str, handler: GuideHandler = Depends(get_guide_handler)):
    """
    Get specializations for a specific class
    """
    return handler.get_class_specs(class_name)

# Embedding Database Endpoints

@router.post("/embedding/store_guide", response_model=EmbeddingDBResponse)
async def store_guide_in_embedding_db(request: ScrapeGuideRequest, handler: GuideHandler = Depends(get_guide_handler)):
    """
    Scrape and store a specific guide in embedding database
    """
    result = handler.store_guide_in_embedding_db(request.class_name, request.spec_name, request.guide_type)
    
    return EmbeddingDBResponse(
        success=result["success"],
        message=result["message"],
        data=result.get("data")
    )

@router.get("/embedding/guide/{class_name}/{spec_name}", response_model=EmbeddingDBResponse)
async def get_guide_from_embedding_db(class_name: str, spec_name: str, 
                                     guide_type: str = "overview-pve-dps",
                                     handler: GuideHandler = Depends(get_guide_handler)):
    """
    Retrieve a specific guide from embedding database
    """
    result = handler.get_guide_from_embedding_db(class_name, spec_name, guide_type)
    
    return EmbeddingDBResponse(
        success=result["success"],
        message=result["message"],
        data=result.get("data")
    )

@router.get("/embedding/search", response_model=EmbeddingDBResponse)
async def search_guides_in_embedding_db(query: str, limit: int = 10, handler: GuideHandler = Depends(get_guide_handler)):
    """
    Search guides in embedding database
    """
    result = handler.search_guides_in_embedding_db(query, limit)
    
    return EmbeddingDBResponse(
        success=result["success"],
        message=result["message"],
        data=result.get("data")
    )

@router.get("/embedding/stats", response_model=EmbeddingDBResponse)
async def get_embedding_db_stats(handler: GuideHandler = Depends(get_guide_handler)):
    """
    Get embedding database statistics
    """
    result = handler.get_embedding_db_stats()
    
    return EmbeddingDBResponse(
        success=result["success"],
        message=result["message"],
        stats=result.get("stats")
    )

@router.get("/embedding/all_guides", response_model=EmbeddingDBResponse)
async def get_all_guides_from_embedding_db(handler: GuideHandler = Depends(get_guide_handler)):
    """
    Get all guides from embedding database
    """
    result = handler.get_all_guides_from_embedding_db()
    
    return EmbeddingDBResponse(
        success=result["success"],
        message=result["message"],
        data=result.get("data")
    ) 

@router.post("/embedding/force_update_guide", response_model=EmbeddingDBResponse)
async def force_update_guide_in_embedding_db(request: ScrapeGuideRequest, handler: GuideHandler = Depends(get_guide_handler)):
    """
    Force update a specific guide in embedding database (re-scrape and replace)
    """
    result = handler.force_update_guide_in_embedding_db(request.class_name, request.spec_name, request.guide_type)
    
    return EmbeddingDBResponse(
        success=result["success"],
        message=result["message"],
        data=result.get("data")
    )

@router.get("/embedding/guide/{class_name}/{spec_name}/last_updated", response_model=EmbeddingDBResponse)
async def get_guide_last_updated(class_name: str, spec_name: str, 
                                guide_type: str = "overview-pve-dps",
                                handler: GuideHandler = Depends(get_guide_handler)):
    """
    Get the last updated timestamp for a specific guide
    """
    result = handler.get_guide_last_updated(class_name, spec_name, guide_type)
    
    return EmbeddingDBResponse(
        success=result["success"],
        message=result["message"],
        data=result.get("data")
    )

@router.delete("/embedding/guide/{class_name}/{spec_name}", response_model=EmbeddingDBResponse)
async def delete_guide_from_embedding_db(class_name: str, spec_name: str, 
                                        guide_type: str = "overview-pve-dps",
                                        handler: GuideHandler = Depends(get_guide_handler)):
    """
    Delete a specific guide from embedding database
    """
    result = handler.delete_guide_from_embedding_db(class_name, spec_name, guide_type)
    
    return EmbeddingDBResponse(
        success=result["success"],
        message=result["message"],
        data=result.get("data")
    )

@router.post("/embedding/clear_all", response_model=EmbeddingDBResponse)
async def clear_all_guides_from_embedding_db(handler: GuideHandler = Depends(get_guide_handler)):
    """
    Clear all guides from embedding database
    """
    result = handler.clear_all_guides_from_embedding_db()
    
    return EmbeddingDBResponse(
        success=result["success"],
        message=result["message"],
        data=result.get("data")
    ) 