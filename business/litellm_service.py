import logging
import os
import time
from typing import List, Dict, Optional, Any
from dataclasses import dataclass

import litellm
from litellm import completion
from prometheus_client import Counter, REGISTRY

from connector.embedding_connector import EmbeddingConnector

logger = logging.getLogger(__name__)

def get_metric(metric_type: str, name: str, *args, **kwargs):
    try:
        return REGISTRY._names_to_collectors[name]
    except KeyError:
        if metric_type == "counter":
            return Counter(name, *args, **kwargs)
        raise ValueError(f"Unknown metric type: {metric_type}")

LLM_TOKENS_USED = get_metric(
    "counter",
    "llm_tokens_used",
    "Total tokens used",
    ["model", "type"]
)

@dataclass
class LLMResponse:
    """Structured response from LLM service"""
    success: bool
    answer: Optional[str] = None
    error: Optional[str] = None
    sources: List[Dict[str, Any]] = None
    metadata: Dict[str, Any] = None

    def __post_init__(self):
        if self.sources is None:
            self.sources = []
        if self.metadata is None:
            self.metadata = {}

class LiteLLMService:
    """Business layer service for LLM operations with LiteLLM gateway"""

    def __init__(self, embedding_connector: EmbeddingConnector):
        self.embedding_connector = embedding_connector
        self.is_initialized = False
        self.model_config: Dict[str, Any] = {}
        self.cost_limits: Dict[str, float] = {}
        self.rate_limits: Dict[str, int] = {}

    def initialize(self) -> bool:
        """
        Initialize the LiteLLM service with caching, monitoring, and guardrails
        """
        try:
            logger.info("Initializing LiteLLMService...")

            # Ensure API key is set
            api_key = os.getenv("GOOGLE_API_KEY")
            if not api_key:
                logger.error("GOOGLE_API_KEY not set")
                return False

            # Enable detailed logs
            os.environ["LITELLM_LOG"] = "DEBUG"

            # Model configuration
            self.model_config = {
                "model":       "gemini/gemini-2.0-flash-exp",
                "api_key":     api_key,
                "temperature": 0.1,
                "max_tokens":  2048
            }

            # Cost & rate limits
            self.cost_limits = {
                "daily_limit":   float(os.getenv("LLM_DAILY_COST_LIMIT", "10.0")),
                "monthly_limit": float(os.getenv("LLM_MONTHLY_COST_LIMIT", "100.0"))
            }
            self.rate_limits = {
                "requests_per_minute": int(os.getenv("LLM_RATE_LIMIT_RPM", "60")),
                "requests_per_hour":   int(os.getenv("LLM_RATE_LIMIT_RPH", "1000"))
            }

            # Initialize embedding connector
            if not self.embedding_connector.is_setup:
                if not self.embedding_connector.setup():
                    logger.error("Embedding connector setup failed")
                    return False

            self.is_initialized = True
            logger.info("LiteLLMService initialized successfully")
            return True

        except Exception as e:
            logger.error(f"Initialization error: {e}")
            return False

    def ask_question(self, question: str) -> LLMResponse:
        """
        Ask a question using RAG (Retrieval-Augmented Generation)
        """
        if not self.is_initialized:
            return LLMResponse(success=False, error="Service not initialized")

        start_time = time.time()
        try:
            logger.info(f"Processing question: {question}")

            # Retrieve context docs
            context = self._retrieve_relevant_docs(question)
            system_prompt = self._create_system_prompt()
            user_prompt = f"Context: {context}\n\nQuestion: {question}\n\nAnswer:"

            # Perform the LLM call
            response = completion(
                model=self.model_config["model"],
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user",   "content": user_prompt}
                ],
                temperature=self.model_config["temperature"],
                max_tokens=self.model_config["max_tokens"],
                api_key=self.model_config["api_key"]
            )

            # Extract response data
            tokens_used = response.usage.total_tokens if response.usage else 0
            cost_usd = self._estimate_cost(tokens_used)

            # Update Prometheus metrics
            LLM_TOKENS_USED.labels(
                model=self.model_config["model"],
                type="total"
            ).inc(tokens_used)

            # Build RAG sources
            results = self.embedding_connector.search_guides(question, limit=3)
            sources = [
                {
                    "class_name":      r["class_name"],
                    "spec_name":       r["spec_name"],
                    "similarity_score":r["similarity_score"],
                    "url":             r.get("url", ""),
                    "content_preview": r["content"][:200] + "..."
                }
                for r in results
            ]

            elapsed = time.time() - start_time
            answer  = response.choices[0].message.content

            return LLMResponse(
                success=True,
                answer=answer,
                sources=sources,
                metadata={
                    "duration":   elapsed,
                    "tokens_used":tokens_used,
                    "cost_usd":   cost_usd,
                    "model":      self.model_config["model"]
                }
            )

        except Exception as e:
            duration = time.time() - start_time
            logger.error(f"Error processing question: {e}")
            return LLMResponse(success=False, error=str(e), metadata={"duration": duration})

    def _create_system_prompt(self) -> str:
        return (
            "You are an expert World of Warcraft class guide assistant. "
            "Use the provided context to answer concisely and cite sources."
        )

    def _retrieve_relevant_docs(self, question: str) -> str:
        try:
            guides = self.embedding_connector.search_guides(question, limit=5)
            if not guides:
                return "No relevant guides found."
            parts = []
            for g in guides:
                parts.append(
                    f"Class: {g['class_name']}, Spec: {g['spec_name']}\n"
                    + g["content"][:1000]
                )
            return "\n\n".join(parts)
        except Exception as e:
            logger.error(f"Doc retrieval error: {e}")
            return ""

    def _estimate_cost(self, tokens: int) -> float:
        input_cost  = (tokens * 0.7 / 1000) * 0.000075
        output_cost = (tokens * 0.3 / 1000) * 0.0003
        return input_cost + output_cost

    def get_service_info(self) -> Dict[str, Any]:
        return {
            "model":           self.model_config.get("model", "unknown"),
            "initialized":     self.is_initialized,
            "cost_limits":     self.cost_limits,
            "rate_limits":     self.rate_limits
        }

    def is_ready(self) -> bool:
        return self.is_initialized
