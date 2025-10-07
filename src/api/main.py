# src/api/main.py
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Initialize FastAPI
app = FastAPI(
    title="CodeSensei API",
    description="AI-powered code review system",
    version="0.1.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
async def root():
    return {
        "message": "Welcome to CodeSensei API",
        "version": "0.1.0",
        "status": "running"
    }

@app.get("/health")
async def health():
    return {
        "status": "healthy",
        "environment": os.getenv("ENVIRONMENT", "development")
    }

# Test endpoint to verify Groq API key is loaded
@app.get("/test/api-key")
async def test_api_key():
    api_key = os.getenv("GROQ_API_KEY")
    if api_key:
        return {
            "status": "API key loaded",
            "key_preview": f"{api_key[:10]}...{api_key[-4:]}"
        }
    else:
        return {
            "status": "API key not found",
            "message": "Please set GROQ_API_KEY in .env file"
        }