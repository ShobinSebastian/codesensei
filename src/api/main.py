# src/api/main.py(UPDATED)

"""
CodeSensei API - Complete Feature Set
======================================
FastAPI backend with code analysis, explanation, and debugging.

Version: 0.3.0
Features:
- Analysis (Day 1-7): /analyze, /analyze/static
- Explainer (Day 8-10): /explain, /explain/concepts, /explain/complexity
- Debugger (Day 11-14): /debug, /debug/quick, /debug/fix

CodeSensei API - Production Version
====================================
FastAPI backend with logging, metrics, and monitoring.

Version: 0.3.0 (Production Ready)
"""

from fastapi import FastAPI, HTTPException, Request, Response
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import PlainTextResponse
from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any, Literal
import os
import time
import uuid
from dotenv import load_dotenv

from src.core.orchestrator import CodeAnalysisOrchestrator
from src.analyzers.static_analyzer import StaticAnalyzer
from src.agents.llm_agent import LLMAgent
from src.features.code_explainer import CodeExplainer
from src.features.bug_debugger import BugDebugger

# Import logging and metrics
from src.utils.logger import setup_logging, get_logger, RequestLogger
from src.utils.metrics import (
    track_request, get_metrics, init_metrics,
    REQUEST_COUNT, ACTIVE_REQUESTS, UPTIME_SECONDS
)

# Load environment variables
load_dotenv()

# Setup logging
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
LOG_FILE = os.getenv("LOG_FILE", "logs/api.log")
setup_logging(log_level=LOG_LEVEL, log_file=LOG_FILE, json_format=True)

# Get logger
logger = get_logger(__name__, context={
    "service": "codesensei-api",
    "version": "0.3.0"
})

# Initialize FastAPI
app = FastAPI(
    title="CodeSensei API",
    description="AI-powered code review, analysis, explanation, and debugging system",
    version="0.3.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Track startup time
START_TIME = time.time()

# Global instances
orchestrator = None
static_analyzer = None
llm_agent = None
code_explainer = None
bug_debugger = None


# ============================================================================
# MIDDLEWARE
# ============================================================================

@app.middleware("http")
async def logging_middleware(request: Request, call_next):
    """Log all requests and responses."""
    request_id = str(uuid.uuid4())
    request.state.request_id = request_id
    
    # Log request
    RequestLogger.log_request(
        logger,
        request_id=request_id,
        method=request.method,
        path=request.url.path,
        client_ip=request.client.host
    )
    
    # Process request
    start_time = time.time()
    
    try:
        response = await call_next(request)
        duration_ms = (time.time() - start_time) * 1000
        
        # Log response
        RequestLogger.log_response(
            logger,
            request_id=request_id,
            status_code=response.status_code,
            duration_ms=duration_ms,
            response_size=0  # FastAPI doesn't expose this easily
        )
        
        return response
        
    except Exception as e:
        duration_ms = (time.time() - start_time) * 1000
        logger.exception(
            "Request failed",
            request_id=request_id,
            duration_ms=duration_ms
        )
        raise


# ============================================================================
# STARTUP/SHUTDOWN
# ============================================================================

@app.on_event("startup")
async def startup_event():
    """Initialize all services on startup."""
    global orchestrator, static_analyzer, llm_agent, code_explainer, bug_debugger
    
    logger.info("Starting CodeSensei API", version="0.3.0")
    
    # Initialize metrics
    environment = os.getenv("ENVIRONMENT", "development")
    init_metrics(version="0.3.0", environment=environment)
    
    try:
        # Core services
        orchestrator = CodeAnalysisOrchestrator()
        logger.info("Orchestrator initialized")
        
        static_analyzer = StaticAnalyzer()
        logger.info("Static analyzer initialized")
        
        # Try to initialize LLM services
        try:
            llm_agent = LLMAgent()
            code_explainer = CodeExplainer(llm_agent)
            bug_debugger = BugDebugger(static_analyzer, llm_agent)
            logger.info("LLM services initialized")
        except Exception as e:
            logger.warning(f"LLM services unavailable: {e}")
            llm_agent = None
            code_explainer = None
            bug_debugger = None
        
        logger.info("API ready", environment=environment)
        
    except Exception as e:
        logger.critical(f"Startup failed: {e}")
        raise


@app.on_event("shutdown")
async def shutdown_event():
    """Cleanup on shutdown."""
    logger.info("Shutting down CodeSensei API")


# ============================================================================
# REQUEST/RESPONSE MODELS
# ============================================================================

class CodeAnalysisRequest(BaseModel):
    code: str = Field(..., description="Python code to analyze", min_length=1)
    use_llm: bool = Field(True, description="Whether to use LLM analysis")
    max_llm_time: int = Field(30, description="Max seconds for LLM", ge=5, le=60)


class CodeExplainRequest(BaseModel):
    code: str = Field(..., description="Python code to explain", min_length=1)
    detail_level: Literal["basic", "medium", "detailed"] = Field("medium")


class DebugRequest(BaseModel):
    code: str = Field(..., description="Buggy Python code", min_length=1)
    error_message: Optional[str] = Field(None)


# ============================================================================
# MAIN ENDPOINTS
# ============================================================================

@app.get("/")
async def root():
    """Welcome endpoint."""
    logger.info("Root endpoint accessed")
    return {
        "message": "Welcome to CodeSensei API v0.3.0",
        "version": "0.3.0",
        "status": "running",
        "docs": "/docs",
        "metrics": "/metrics",
        "health": "/health"
    }


@app.get("/health")
async def health():
    """Health check endpoint."""
    uptime = time.time() - START_TIME
    UPTIME_SECONDS.set(uptime)
    
    return {
        "status": "healthy",
        "version": "0.3.0",
        "uptime_seconds": round(uptime, 2),
        "services": {
            "static_analyzer": static_analyzer is not None,
            "llm_agent": llm_agent is not None,
            "orchestrator": orchestrator is not None,
            "code_explainer": code_explainer is not None,
            "bug_debugger": bug_debugger is not None
        }
    }


@app.get("/metrics", response_class=PlainTextResponse)
async def metrics():
    """Prometheus metrics endpoint."""
    return get_metrics()


# ============================================================================
# ANALYSIS ENDPOINTS
# ============================================================================

@app.post("/analyze")
@track_request("/analyze")
async def analyze_code(request: CodeAnalysisRequest):
    """Analyze Python code."""
    logger.info("Analysis requested", use_llm=request.use_llm, code_lines=len(request.code.split('\n')))
    
    if not orchestrator:
        logger.error("Orchestrator not initialized")
        raise HTTPException(503, "Analysis service not initialized")
    
    try:
        result = orchestrator.analyze(
            code=request.code,
            use_llm=request.use_llm,
            max_llm_time=request.max_llm_time
        )
        
        logger.info(
            "Analysis completed",
            issues_found=result['summary']['total'],
            duration=result['metadata']['execution_time']
        )
        
        return {
            "success": True,
            "issues": result['issues'],
            "summary": result['summary'],
            "metadata": result['metadata']
        }
        
    except Exception as e:
        logger.exception("Analysis failed")
        raise HTTPException(500, f"Analysis failed: {str(e)}")


@app.post("/explain")
@track_request("/explain")
async def explain_code(request: CodeExplainRequest):
    """Explain code."""
    logger.info("Explanation requested", detail_level=request.detail_level)
    
    if not code_explainer:
        raise HTTPException(503, "Code explainer not available")
    
    try:
        result = code_explainer.explain(
            code=request.code,
            detail_level=request.detail_level
        )
        
        logger.info("Explanation completed", concepts=len(result['concepts']))
        
        return {
            "success": True,
            **result
        }
        
    except Exception as e:
        logger.exception("Explanation failed")
        raise HTTPException(500, f"Explanation failed: {str(e)}")


@app.post("/debug")
@track_request("/debug")
async def debug_code(request: DebugRequest):
    """Debug code."""
    logger.info("Debug requested", has_error_message=request.error_message is not None)
    
    if not bug_debugger:
        raise HTTPException(503, "Bug debugger not available")
    
    try:
        result = bug_debugger.debug(
            code=request.code,
            error_message=request.error_message
        )
        
        logger.info("Debug completed", bugs_found=len(result['bugs_found']))
        
        return {
            "success": True,
            **result
        }
        
    except Exception as e:
        logger.exception("Debugging failed")
        raise HTTPException(500, f"Debugging failed: {str(e)}")


# ============================================================================
# RUN SERVER
# ============================================================================

if __name__ == "__main__":
    import uvicorn
    
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )