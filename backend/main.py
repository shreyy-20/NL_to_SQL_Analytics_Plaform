"""
KrishiQuery FastAPI Application
Main entry point for the backend service
"""

from fastapi import FastAPI, HTTPException, Depends, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.middleware.trustedhost import TrustedHostMiddleware
import logging
from contextlib import asynccontextmanager
from prometheus_client import Counter, Histogram, generate_latest, CONTENT_TYPE_LATEST
from starlette.responses import Response

from backend.config import settings
from backend.db_connection import engine, SessionLocal
from backend.api import farmers, queries, voice, dashboard

# Configure logging
logging.basicConfig(
    level=getattr(logging, settings.LOG_LEVEL),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(settings.LOG_FILE),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# Prometheus metrics
REQUEST_COUNT = Counter('http_requests_total', 'Total HTTP requests', ['method', 'endpoint', 'status'])
REQUEST_LATENCY = Histogram('http_request_duration_seconds', 'HTTP request latency', ['method', 'endpoint'])

@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Handles startup and shutdown events
    """
    # Startup
    logger.info("Starting KrishiQuery Application...")
    logger.info(f"Environment: {settings.ENVIRONMENT}")
    logger.info(f"Database: {settings.DATABASE_URL.split('@')[1] if '@' in settings.DATABASE_URL else 'connected'}")
    
    # Initialize database connection pool
    try:
        with engine.connect() as conn:
            logger.info("Database connection successful")
    except Exception as e:
        logger.error(f"Database connection failed: {e}")
        raise
    
    # Load AI models
    try:
        from ai.intent_classifier.predict import is_model_loaded, load_intent_model
        load_intent_model()
        if is_model_loaded():
            logger.info("Intent classifier model loaded")
        else:
            logger.warning("Intent classifier not loaded, running with rule-based fallback")
    except Exception as e:
        logger.warning(f"Could not load intent model: {e}")
    
    yield
    
    # Shutdown
    logger.info("Shutting down KrishiQuery Application...")
    engine.dispose()
    logger.info("Application shutdown complete")

# Initialize FastAPI app
app = FastAPI(
    title="KrishiQuery API",
    description="Voice-Based Natural Language Query System for Indian Agriculture",
    version="1.0.0",
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc"
)

# Add middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.add_middleware(
    TrustedHostMiddleware,
    allowed_hosts=settings.ALLOWED_HOSTS
)

# Middleware for request logging and metrics
@app.middleware("http")
async def add_metrics_middleware(request: Request, call_next):
    import time
    start_time = time.time()
    
    response = await call_next(request)
    
    # Record metrics
    REQUEST_COUNT.labels(
        method=request.method,
        endpoint=request.url.path,
        status=response.status_code
    ).inc()
    
    REQUEST_LATENCY.labels(
        method=request.method,
        endpoint=request.url.path
    ).observe(time.time() - start_time)
    
    # Log request
    logger.info(
        f"{request.method} {request.url.path} - "
        f"Status: {response.status_code} - "
        f"Duration: {time.time() - start_time:.3f}s"
    )
    
    return response

# Include routers
app.include_router(farmers.router, prefix="/api/farmers", tags=["Farmers"])
app.include_router(queries.router, prefix="/api/queries", tags=["Queries"])
app.include_router(voice.router, prefix="/api/voice", tags=["Voice Services"])
app.include_router(dashboard.router, prefix="/api/dashboard", tags=["Dashboard"])

# Health check endpoint
@app.get("/health", tags=["Health"])
async def health_check():
    """Health check endpoint for monitoring"""
    health_status = {
        "status": "healthy",
        "timestamp": "2024-01-01T00:00:00Z",
        "services": {
            "database": "unknown",
            "redis": "unknown",
            "ai_models": "unknown"
        }
    }
    
    # Check database
    try:
        from sqlalchemy import text
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
            health_status["services"]["database"] = "healthy"
    except Exception as e:
        health_status["services"]["database"] = f"unhealthy: {str(e)}"
        health_status["status"] = "degraded"
    
    # Check AI models
    try:
        from ai.intent_classifier.predict import is_model_loaded
        if is_model_loaded():
            health_status["services"]["ai_models"] = "healthy"
        else:
            health_status["services"]["ai_models"] = "fallback_mode"
    except:
        health_status["services"]["ai_models"] = "unavailable"
    
    # Check Redis (if configured)
    if settings.REDIS_URL:
        try:
            import redis
            r = redis.from_url(settings.REDIS_URL)
            r.ping()
            health_status["services"]["redis"] = "healthy"
        except:
            health_status["services"]["redis"] = "unhealthy"
            health_status["status"] = "degraded"
    
    if health_status["status"] != "healthy":
        raise HTTPException(status_code=503, detail=health_status)
    
    return health_status

# Metrics endpoint for Prometheus
@app.get("/metrics", tags=["Monitoring"])
async def get_metrics():
    """Prometheus metrics endpoint"""
    return Response(content=generate_latest(), media_type=CONTENT_TYPE_LATEST)

# Root endpoint
@app.get("/", tags=["Root"])
async def root():
    """Root endpoint with API information"""
    return {
        "name": "KrishiQuery API",
        "version": "1.0.0",
        "description": "Voice-Based Natural Language Query System for Indian Agriculture",
        "documentation": "/docs",
        "health": "/health",
        "status": "operational"
    }

# Global exception handler
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    logger.error(f"Unhandled exception: {exc}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={
            "error": "Internal server error",
            "message": str(exc),
            "path": request.url.path
        }
    )

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "backend.main:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.ENVIRONMENT == "development",
        log_level=settings.LOG_LEVEL.lower()
    )
