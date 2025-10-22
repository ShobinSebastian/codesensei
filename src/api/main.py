# src/api/main.py

"""
CodeSensei API
==============
FastAPI backend for the code analysis system.

Endpoints:
- POST /analyze - Analyze code with static + LLM
- POST /analyze/static - Static analysis only (fast)
- POST /explain - Get code explanation
- GET /health - Health check

Author: Shobin Sebastian
Date: November 2025
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
import os
from dotenv import load_dotenv
from src.core.orchestrator import CodeAnalysisOrchestrator
from src.analyzers.static_analyzer import StaticAnalyzer
from src.agents.llm_agent import LLMAgent

# Load environment variables
load_dotenv()

# Initialize FastAPI
app = FastAPI(
    title="CodeSensei API",
    description="AI-powered code review and analysis system",
    version="0.1.0",
    docs_url="/docs",  # Swagger UI at /docs
    redoc_url="/redoc"  # ReDoc at /redoc
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify exact origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize analyzers (do this once at startup)
orchestrator = None
static_analyzer = None
llm_agent = None


@app.on_event("startup")
async def startup_event():
    """
    Initialize analyzers when API starts.
    This runs once, not on every request (efficient!).
    """
    global orchestrator, static_analyzer, llm_agent
    
    print("🚀 Starting CodeSensei API...")
    
    try:
        # Initialize orchestrator (combines static + LLM)
        orchestrator = CodeAnalysisOrchestrator()
        print("  ✓ Orchestrator initialized")
        
        # Initialize static analyzer (backup, for static-only endpoint)
        static_analyzer = StaticAnalyzer()
        print("  ✓ Static analyzer initialized")
        
        # Try to initialize LLM agent
        try:
            llm_agent = LLMAgent()
            print("  ✓ LLM agent initialized")
        except Exception as e:
            print(f"  ⚠ LLM agent unavailable: {e}")
            llm_agent = None
        
        print("✅ API ready!")
        
    except Exception as e:
        print(f"❌ Startup failed: {e}")
        raise


# ============================================================================
# REQUEST/RESPONSE MODELS
# ============================================================================

class CodeAnalysisRequest(BaseModel):
    """Request model for code analysis."""
    code: str = Field(..., description="Python code to analyze", min_length=1)
    use_llm: bool = Field(True, description="Whether to use LLM analysis")
    max_llm_time: int = Field(30, description="Max seconds for LLM analysis", ge=5, le=60)
    
    class Config:
        schema_extra = {
            "example": {
                "code": "def divide(a, b):\n    return a / b",
                "use_llm": True,
                "max_llm_time": 30
            }
        }


class CodeExplainRequest(BaseModel):
    """Request model for code explanation."""
    code: str = Field(..., description="Python code to explain", min_length=1)
    
    class Config:
        schema_extra = {
            "example": {
                "code": "def factorial(n):\n    return 1 if n <= 1 else n * factorial(n-1)"
            }
        }


class Issue(BaseModel):
    """Model for a single code issue."""
    type: str
    severity: str
    line: int
    message: str
    explanation: Optional[str] = None
    code_snippet: Optional[str] = None
    category: Optional[str] = None
    learning_tip: Optional[str] = None
    suggested_fix: Optional[str] = None
    tool: Optional[str] = None


class AnalysisResponse(BaseModel):
    """Response model for code analysis."""
    success: bool
    issues: List[Dict[str, Any]]
    summary: Dict[str, Any]
    metadata: Dict[str, Any]


class ExplainResponse(BaseModel):
    """Response model for code explanation."""
    success: bool
    explanation: str
    code_lines: int


# ============================================================================
# API ENDPOINTS
# ============================================================================

@app.get("/")
async def root():
    """Welcome endpoint with API info."""
    return {
        "message": "Welcome to CodeSensei API",
        "version": "0.1.0",
        "status": "running",
        "docs": "/docs",
        "endpoints": {
            "analyze": "POST /analyze - Full analysis (static + LLM)",
            "static": "POST /analyze/static - Static analysis only",
            "explain": "POST /explain - Get code explanation",
            "health": "GET /health - Health check"
        }
    }


@app.get("/health")
async def health():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "environment": os.getenv("ENVIRONMENT", "development"),
        "services": {
            "static_analyzer": static_analyzer is not None,
            "llm_agent": llm_agent is not None,
            "orchestrator": orchestrator is not None
        }
    }


@app.post("/analyze", response_model=AnalysisResponse)
async def analyze_code(request: CodeAnalysisRequest):
    """
    Analyze Python code using static analysis + LLM.
    
    This is the main endpoint - combines all analysis tools.
    
    Args:
        request: Code analysis request
        
    Returns:
        Complete analysis with issues, summary, and metadata
        
    Raises:
        HTTPException: If analysis fails
    """
    if not orchestrator:
        raise HTTPException(
            status_code=503,
            detail="Analysis service not initialized"
        )
    
    try:
        # Run analysis
        result = orchestrator.analyze(
            code=request.code,
            use_llm=request.use_llm,
            max_llm_time=request.max_llm_time
        )
        
        return AnalysisResponse(
            success=True,
            issues=result['issues'],
            summary=result['summary'],
            metadata=result['metadata']
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Analysis failed: {str(e)}"
        )


@app.post("/analyze/static")
async def analyze_static_only(request: CodeAnalysisRequest):
    """
    Analyze code using ONLY static analysis (no LLM).
    
    This is faster than full analysis.
    Use when you need quick feedback.
    
    Args:
        request: Code analysis request (use_llm ignored)
        
    Returns:
        Static analysis results
    """
    if not static_analyzer:
        raise HTTPException(
            status_code=503,
            detail="Static analyzer not initialized"
        )
    
    try:
        result = static_analyzer.analyze(request.code)
        
        return {
            "success": True,
            "issues": result['issues'],
            "summary": result['summary'],
            "metadata": {
                "analysis_type": "static_only",
                "llm_used": False
            }
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Static analysis failed: {str(e)}"
        )


@app.post("/explain", response_model=ExplainResponse)
async def explain_code(request: CodeExplainRequest):
    """
    Get a beginner-friendly explanation of code.
    
    Uses LLM to explain what the code does.
    Perfect for learning!
    
    Args:
        request: Code to explain
        
    Returns:
        Plain English explanation
    """
    if not llm_agent:
        raise HTTPException(
            status_code=503,
            detail="LLM service not available. Please check GROQ_API_KEY."
        )
    
    try:
        explanation = llm_agent.explain_code(request.code)
        
        return ExplainResponse(
            success=True,
            explanation=explanation,
            code_lines=len(request.code.split('\n'))
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Explanation failed: {str(e)}"
        )


@app.get("/test/api-key")
async def test_api_key():
    """
    Test if Groq API key is loaded.
    (For debugging only - remove in production!)
    """
    api_key = os.getenv("GROQ_API_KEY")
    
    if api_key:
        return {
            "status": "API key loaded",
            "key_preview": f"{api_key[:10]}...{api_key[-4:]}",
            "length": len(api_key)
        }
    else:
        return {
            "status": "API key not found",
            "message": "Please set GROQ_API_KEY in .env file"
        }


# ============================================================================
# ERROR HANDLERS
# ============================================================================

@app.exception_handler(ValueError)
async def value_error_handler(request, exc):
    """Handle validation errors."""
    return {
        "success": False,
        "error": "Invalid input",
        "detail": str(exc)
    }


@app.exception_handler(Exception)
async def general_exception_handler(request, exc):
    """Catch-all error handler."""
    return {
        "success": False,
        "error": "Internal server error",
        "detail": str(exc)
    }


# ============================================================================
# RUN SERVER
# ============================================================================

if __name__ == "__main__":
    import uvicorn
    
    # Run server
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,  # Auto-reload on code changes
        log_level="info"
    )