from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import structlog
from starlette.responses import Response

from backend.src.interface.api.v1.endpoints import auth, tasks, task_lists, checklists
from backend.src.infrastructure.logging.configure import configure_logging
from backend.src.config import settings
from backend.src.infrastructure.scripts.init_db import init_db_data
from backend.src.infrastructure.middleware.rate_limiter import limiter
from starlette.requests import Request
from prometheus_fastapi_instrumentator import Instrumentator
from slowapi.middleware import SlowAPIMiddleware
from slowapi.errors import RateLimitExceeded
from slowapi import _rate_limit_exceeded_handler

configure_logging()
log = structlog.get_logger(__name__)

@asynccontextmanager
async def lifespan(app: FastAPI):
    log.info("Startup: Initializing database")
    await init_db_data()
    log.info("Startup: Default data initialized")
    yield
    log.info("Shutdown: Cleaning up")

app = FastAPI(
    title="Task Tracker API",
    description="API for a modern task tracking application.",
    version="1.0.0",
    lifespan=lifespan,
)

# CORS Middleware - MUST be added BEFORE other middleware
# For development, allow all origins
cors_origins = settings.BACKEND_CORS_ORIGINS if settings.BACKEND_CORS_ORIGINS and len(settings.BACKEND_CORS_ORIGINS) > 0 else ["*"]
log.info("CORS origins configured", origins=cors_origins, count=len(cors_origins))

app.add_middleware(
    CORSMiddleware,
    allow_origins=cors_origins,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS", "PATCH"],
    allow_headers=["*"],
    expose_headers=["*"],
)

# Instrumentator for Prometheus metrics
Instrumentator().instrument(app).expose(app)

# Set limiter in app state for use in routes
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)
app.add_middleware(SlowAPIMiddleware)

@app.middleware("http")
async def add_correlation_id(request: Request, call_next):
    # Handle OPTIONS requests for CORS preflight
    if request.method == "OPTIONS":
        response = Response()
        response.headers["Access-Control-Allow-Origin"] = request.headers.get("Origin", "*")
        response.headers["Access-Control-Allow-Methods"] = "GET, POST, PUT, DELETE, OPTIONS, PATCH"
        response.headers["Access-Control-Allow-Headers"] = "*"
        response.headers["Access-Control-Allow-Credentials"] = "true"
        return response
    
    # In a real app, you'd want a more robust way to generate this
    correlation_id = request.headers.get("X-Request-ID", "local-dev-request")
    
    structlog.contextvars.bind_contextvars(correlation_id=correlation_id)
    try:
        response = await call_next(request)
        response.headers["X-Correlation-ID"] = correlation_id
        return response
    finally:
        structlog.contextvars.clear_contextvars()

# Health check endpoint
@app.get("/health")
async def health_check():
    return {"status": "healthy", "service": "Task Tracker API"}

# API Routers
app.include_router(auth.router, prefix="/api/v1/auth", tags=["Authentication"])
app.include_router(tasks.router, prefix="/api/v1/tasks", tags=["Tasks"])
app.include_router(task_lists.router, prefix="/api/v1/task-lists", tags=["Task Lists"])
app.include_router(checklists.router, prefix="/api/v1", tags=["Checklists"])

