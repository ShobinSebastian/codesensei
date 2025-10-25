# src/api/main.py - UPDATED with Code Explainer

"""
CodeSensei API - Updated with Code Explainer
=============================================
FastAPI backend with code analysis + explanation features.

New Endpoints (Day 8-10):
- POST /explain - Explain code (basic/medium/detailed)
- POST /explain/concepts - Extract key concepts
- POST /explain/complexity - Analyze complexity

Author: Shobin Sebastian
Date: November 2025
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any, Literal
import os
from dotenv import load_dotenv
from src.core.orchestrator import CodeAnalysisOrchestrator
from src.analyzers.static_analyzer import StaticAnalyzer
from src.agents.llm_agent import LLMAgent
from src.features.code_explainer import CodeExplainer

# Load environment variables
load_dotenv()

# Initialize FastAPI
app = FastAPI(
    title="CodeSensei API",
    description="AI-powered code review, analysis, and explanation system",
    version="0.2.0",
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

# Global instances
orchestrator = None
static_analyzer = None
llm_agent = None
code_explainer = None


@app.on_event("startup")
async def startup_event():
    """Initialize all services on startup."""
    global orchestrator, static_analyzer, llm_agent, code_explainer
    
    print("🚀 Starting CodeSensei API v0.2.0...")
    
    try:
        # Core services
        orchestrator = CodeAnalysisOrchestrator()
        print("  ✓ Orchestrator initialized")
        
        static_analyzer = StaticAnalyzer()
        print("  ✓ Static analyzer initialized")
        
        # Try to initialize LLM services
        try:
            llm_agent = LLMAgent()
            code_explainer = CodeExplainer(llm_agent)
            print("  ✓ LLM services initialized")
        except Exception as e:
            print(f"  ⚠ LLM services unavailable: {e}")
            llm_agent = None
            code_explainer = None
        
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
    max_llm_time: int = Field(30, description="Max seconds for LLM", ge=5, le=60)


class CodeExplainRequest(BaseModel):
    """Request model for code explanation."""
    code: str = Field(..., description="Python code to explain", min_length=1)
    detail_level: Literal["basic", "medium", "detailed"] = Field(
        "medium",
        description="Level of detail in explanation"
    )
    
    class Config:
        schema_extra = {
            "example": {
                "code": "def factorial(n):\n    return 1 if n <= 1 else n * factorial(n-1)",
                "detail_level": "medium"
            }
        }


class ConceptsRequest(BaseModel):
    """Request for concept extraction."""
    code: str = Field(..., description="Python code to analyze")


class ExplainResponse(BaseModel):
    """Response model for code explanation."""
    success: bool
    overview: str
    line_by_line: List[Dict[str, str]] = []
    concepts: List[Dict[str, str]] = []
    complexity: Dict[str, Any] = {}
    learning_path: List[Dict[str, str]] = []
    metadata: Dict[str, Any] = {}


# ============================================================================
# ORIGINAL ENDPOINTS (from Day 1-7)
# ============================================================================

@app.get("/")
async def root():
    """Welcome endpoint with API info."""
    return {
        "message": "Welcome to CodeSensei API v0.2.0",
        "version": "0.2.0",
        "status": "running",
        "features": {
            "code_analysis": "Analyze code for bugs and issues",
            "code_explanation": "Explain code in simple terms (NEW!)",
            "concept_extraction": "Identify programming concepts (NEW!)",
            "complexity_analysis": "Measure code complexity (NEW!)"
        },
        "docs": "/docs"
    }


@app.get("/health")
async def health():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "version": "0.2.0",
        "services": {
            "static_analyzer": static_analyzer is not None,
            "llm_agent": llm_agent is not None,
            "orchestrator": orchestrator is not None,
            "code_explainer": code_explainer is not None
        }
    }


@app.post("/analyze")
async def analyze_code(request: CodeAnalysisRequest):
    """Analyze Python code (static + LLM)."""
    if not orchestrator:
        raise HTTPException(503, "Analysis service not initialized")
    
    try:
        result = orchestrator.analyze(
            code=request.code,
            use_llm=request.use_llm,
            max_llm_time=request.max_llm_time
        )
        
        return {
            "success": True,
            "issues": result['issues'],
            "summary": result['summary'],
            "metadata": result['metadata']
        }
        
    except Exception as e:
        raise HTTPException(500, f"Analysis failed: {str(e)}")


@app.post("/analyze/static")
async def analyze_static_only(request: CodeAnalysisRequest):
    """Static analysis only (faster)."""
    if not static_analyzer:
        raise HTTPException(503, "Static analyzer not initialized")
    
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
        raise HTTPException(500, f"Static analysis failed: {str(e)}")


# ============================================================================
# NEW ENDPOINTS (Day 8-10: Code Explainer)
# ============================================================================

@app.post("/explain", response_model=ExplainResponse)
async def explain_code(request: CodeExplainRequest):
    """
    Explain code in beginner-friendly language.
    
    New endpoint for Day 8-10 feature!
    
    Detail levels:
    - basic: One-sentence summary
    - medium: Overview + key concepts
    - detailed: Full explanation + line-by-line + learning path
    
    Args:
        request: Code and detail level
        
    Returns:
        Comprehensive explanation with concepts and learning path
    """
    if not code_explainer:
        raise HTTPException(
            503,
            "Code explainer not available. Check GROQ_API_KEY."
        )
    
    try:
        result = code_explainer.explain(
            code=request.code,
            detail_level=request.detail_level
        )
        
        return ExplainResponse(
            success=True,
            overview=result['overview'],
            line_by_line=result.get('line_by_line', []),
            concepts=result['concepts'],
            complexity=result['complexity'],
            learning_path=result['learning_path'],
            metadata=result['metadata']
        )
        
    except Exception as e:
        raise HTTPException(500, f"Explanation failed: {str(e)}")


@app.post("/explain/concepts")
async def extract_concepts(request: ConceptsRequest):
    """
    Extract programming concepts from code.
    
    Identifies what concepts are being used (loops, functions, etc.)
    
    Args:
        request: Code to analyze
        
    Returns:
        List of concepts with descriptions
    """
    if not code_explainer:
        raise HTTPException(503, "Code explainer not available")
    
    try:
        concepts = code_explainer._identify_concepts(request.code)
        
        return {
            "success": True,
            "concepts": concepts,
            "count": len(concepts)
        }
        
    except Exception as e:
        raise HTTPException(500, f"Concept extraction failed: {str(e)}")


@app.post("/explain/complexity")
async def analyze_complexity(request: ConceptsRequest):
    """
    Analyze code complexity.
    
    Returns complexity metrics and interpretation.
    
    Args:
        request: Code to analyze
        
    Returns:
        Complexity metrics with human-readable interpretation
    """
    if not code_explainer:
        raise HTTPException(503, "Code explainer not available")
    
    try:
        complexity = code_explainer._analyze_complexity(request.code)
        
        return {
            "success": True,
            "complexity": complexity
        }
        
    except Exception as e:
        raise HTTPException(500, f"Complexity analysis failed: {str(e)}")


@app.post("/explain/quick")
async def quick_explain(request: ConceptsRequest):
    """
    Quick one-sentence explanation.
    
    Fastest endpoint - just tells you what the code does.
    
    Args:
        request: Code to explain
        
    Returns:
        One-sentence explanation
    """
    if not llm_agent:
        raise HTTPException(503, "LLM service not available")
    
    try:
        explanation = llm_agent.explain_code(request.code)
        
        return {
            "success": True,
            "explanation": explanation,
            "code_lines": len(request.code.split('\n'))
        }
        
    except Exception as e:
        raise HTTPException(500, f"Quick explanation failed: {str(e)}")


# ============================================================================
# HELPER ENDPOINTS
# ============================================================================

@app.get("/features")
async def list_features():
    """List all available features and endpoints."""
    return {
        "analysis": {
            "analyze": "POST /analyze - Full code analysis",
            "static": "POST /analyze/static - Static analysis only"
        },
        "explanation": {
            "explain": "POST /explain - Detailed code explanation",
            "concepts": "POST /explain/concepts - Extract concepts",
            "complexity": "POST /explain/complexity - Analyze complexity",
            "quick": "POST /explain/quick - One-sentence explanation"
        },
        "utility": {
            "health": "GET /health - Service health check",
            "features": "GET /features - This endpoint"
        }
    }


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