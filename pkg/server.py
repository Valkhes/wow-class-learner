from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
import logging
from typing import Optional

from router.guide_router import router as guide_router
from router.llm_router import llm_router
from router.guide_handler import GuideHandler
from router.llm_handler import LLMHandler
from business.scraper_service import ScraperService
from business.guide_service import GuideService
from business.llm_service import LLMService
from connector.embedding_connector import create_embedding_connector, EmbeddingConnector

# Configure logging
logger = logging.getLogger(__name__)

class WowClassLearnerServer:
    """Main server class following Clean Architecture principles with class-based layers"""
    
    def __init__(self, host: str = "0.0.0.0", port: int = 8000):
        self.host = host
        self.port = port
        self.app = None
        
        # Layer instances
        self.embedding_connector: Optional[EmbeddingConnector] = None
        self.scraper_service: Optional[ScraperService] = None
        self.guide_service: Optional[GuideService] = None
        self.llm_service: Optional[LLMService] = None
        self.guide_handler: Optional[GuideHandler] = None
        self.llm_handler: Optional[LLMHandler] = None
        
        self.is_setup = False
    
    def setup(self) -> bool:
        """
        Setup the server components following Clean Architecture with class-based layers
        
        Returns:
            bool: True if setup successful, False otherwise
        """
        try:
            logger.info("Setting up WowClassLearnerServer with class-based layers...")
            
            # 1. Setup Connector Layer (Embedding Database)
            logger.info("Setting up connector layer (embedding database)...")
            self.embedding_connector = create_embedding_connector()
            
            # 2. Setup Business Layer Services
            logger.info("Setting up business layer services...")
            
            # Initialize ScraperService
            self.scraper_service = ScraperService()
            if not self.scraper_service.initialize():
                logger.error("Failed to initialize ScraperService")
                return False
            
            # Initialize GuideService with embedding database dependency
            self.guide_service = GuideService(self.embedding_connector)
            if not self.guide_service.initialize():
                logger.error("Failed to initialize GuideService")
                return False
            
            # Initialize LLMService with embedding database dependency
            self.llm_service = LLMService(self.embedding_connector)
            if not self.llm_service.initialize():
                logger.error("Failed to initialize LLMService")
                return False
            
            # 3. Setup Handler Layer
            logger.info("Setting up handler layer...")
            self.guide_handler = GuideHandler(self.scraper_service, self.guide_service)
            self.llm_handler = LLMHandler(self.llm_service)
            
            # 4. Create FastAPI application
            logger.info("Creating FastAPI application...")
            self.app = self._create_fastapi_app()
            
            # 5. Setup dependency injection
            self._setup_dependencies()
            
            self.is_setup = True
            logger.info("WowClassLearnerServer setup completed successfully")
            return True
            
        except Exception as e:
            logger.error(f"Error during server setup: {e}")
            return False
    
    def _create_fastapi_app(self) -> FastAPI:
        """Create and configure FastAPI application"""
        app = FastAPI(
            title="WoW Class Learner API",
            description="API for World of Warcraft class learning with RAG capabilities",
            version="1.0.0",
            docs_url="/docs",
            redoc_url="/redoc"
        )
        
        # Add CORS middleware
        app.add_middleware(
            CORSMiddleware,
            allow_origins=["*"],
            allow_credentials=True,
            allow_methods=["*"],
            allow_headers=["*"],
        )
        
        # Include routers
        app.include_router(guide_router, prefix="/api/v1")
        app.include_router(llm_router)  # LLM router already has /api/v1 prefix
        
        return app
    
    def _setup_dependencies(self):
        """Setup dependency injection for the application"""
        # Make handlers available to routers
        self.app.state.guide_handler = self.guide_handler
        self.app.state.llm_handler = self.llm_handler
    
    def run(self, reload: bool = False):
        """
        Run the FastAPI server
        
        Args:
            reload: Whether to enable auto-reload for development
        """
        if not self.is_setup:
            logger.error("Server not set up. Call setup() first.")
            return
        
        logger.info(f"Starting WowClassLearnerServer on {self.host}:{self.port}")
        
        uvicorn.run(
            self.app,
            host=self.host,
            port=self.port,
            reload=reload,
            log_level="info"
        )
    
    def get_app(self) -> Optional[FastAPI]:
        """Get the FastAPI application instance"""
        return self.app if self.is_setup else None
    
    def get_embedding_connector(self) -> Optional[EmbeddingConnector]:
        """Get the embedding connector instance"""
        return self.embedding_connector if self.is_setup else None
    
    def get_scraper_service(self) -> Optional[ScraperService]:
        """Get the scraper service instance"""
        return self.scraper_service if self.is_setup else None
    
    def get_guide_service(self) -> Optional[GuideService]:
        """Get the guide service instance"""
        return self.guide_service if self.is_setup else None
    
    def get_llm_service(self) -> Optional[LLMService]:
        """Get the LLM service instance"""
        return self.llm_service if self.is_setup else None
    
    def get_guide_handler(self) -> Optional[GuideHandler]:
        """Get the guide handler instance"""
        return self.guide_handler if self.is_setup else None
    
    def get_llm_handler(self) -> Optional[LLMHandler]:
        """Get the LLM handler instance"""
        return self.llm_handler if self.is_setup else None
    
    def get_status(self) -> dict:
        """Get server status information"""
        if not self.is_setup:
            return {"status": "not_setup", "error": "Server not initialized"}
        
        # Get status from each layer
        embedding_stats = self.embedding_connector.get_stats() if self.embedding_connector else {}
        scraper_ready = self.scraper_service.is_ready() if self.scraper_service else False
        guide_ready = self.guide_service.is_ready() if self.guide_service else False
        llm_ready = self.llm_service.is_ready() if self.llm_service else False
        
        return {
            "status": "running",
            "host": self.host,
            "port": self.port,
            "layers": {
                "connector": {
                    "embedding_database": embedding_stats
                },
                "business": {
                    "scraper_service": {"ready": scraper_ready},
                    "guide_service": {"ready": guide_ready},
                    "llm_service": {"ready": llm_ready}
                },
                "handler": {
                    "guide_handler": {"ready": self.guide_handler is not None},
                    "llm_handler": {"ready": self.llm_handler is not None}
                }
            },
            "setup_completed": self.is_setup
        }

def create_server(host: str = "0.0.0.0", port: int = 8000) -> WowClassLearnerServer:
    """
    Factory function to create WowClassLearnerServer instance
    
    Args:
        host: Server host
        port: Server port
        
    Returns:
        WowClassLearnerServer instance
    """
    return WowClassLearnerServer(host=host, port=port)

# Legacy support for direct FastAPI app creation
def create_fastapi_app() -> FastAPI:
    """Create FastAPI app for backward compatibility"""
    server = create_server()
    if server.setup():
        return server.get_app()
    else:
        raise RuntimeError("Failed to setup server") 