import os
from datetime import datetime
from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import ValidationError

from database.config import Base, get_db, engine
from backend.routes.auth import router as auth_router
from backend.routes.documents import router as documents_router
from backend.routes.conversations import router as conversations_router

# Initialize FastAPI app
app = FastAPI(
    title="DocMind",
    description="AI-powered document management and conversational assistant",
    version="1.0.0",
)

# CORS middleware
origins = os.getenv("CORS_ORIGINS", "http://localhost:3000").split(",")
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(auth_router, prefix="/api")
app.include_router(documents_router, prefix="/api")
app.include_router(conversations_router, prefix="/api")

# Auto-mounted AI router — ai/routes.py exposes /api/ai/* (it carries its own prefix)
from ai.routes import router as ai_router
app.include_router(ai_router)

# Global exception handlers
@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    return JSONResponse(
        status_code=exc.status_code,
        content={"detail": exc.detail},
    )

@app.exception_handler(ValidationError)
async def validation_exception_handler(request: Request, exc: ValidationError):
    return JSONResponse(
        status_code=422,
        content={"detail": exc.errors()},
    )

@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception):
    return JSONResponse(
        status_code=500,
        content={"detail": "Internal server error"},
    )

# Health check endpoint
@app.get("/health")
async def health_check():
    return {"status": "ok", "timestamp": datetime.utcnow().isoformat()}

# Lifespan context manager for startup/shutdown
@app.on_event("startup")
async def startup_event():
    # Import and register pgvector adapter before creating tables
    try:
        from pgvector.psycopg2 import register_vector
        import psycopg2.extensions
        # Get a raw connection from the engine to register the vector type
        with engine.connect() as conn:
            # Execute a simple query to ensure connection is active
            conn.execute("SELECT 1")
            # Register vector adapter for psycopg2
            register_vector(conn.connection)
    except ImportError:
        # pgvector not installed, but we can still proceed
        pass
    except Exception as e:
        # Log but don't fail startup if vector registration fails
        print(f"Warning: Could not register pgvector adapter: {e}")
    
    # Run database migrations - only create tables once
    Base.metadata.create_all(bind=engine)

@app.on_event("shutdown")
async def shutdown_event():
    # Perform any necessary cleanup
    pass