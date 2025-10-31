﻿from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.config import settings
from app.routers import auth

app = FastAPI(
    title="SCIMS API",
    description="Star Citizen Inventory Management System API",
    version="0.1.0",
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(auth.router)


@app.get("/")
def read_root():
    """Root endpoint - redirects to API root for consistency."""
    return {
        "status": "ok",
        "app": settings.app_name,
        "environment": settings.environment,
        "version": "0.1.0",
        "api": "v1",
        "docs": "/docs",
    }


@app.get("/api/v1")
def read_api_root():
    """API root endpoint - provides API information."""
    return {
        "status": "ok",
        "app": settings.app_name,
        "environment": settings.environment,
        "version": "0.1.0",
        "api": "v1",
        "docs": "/docs",
    }


@app.get("/health")
def health_check():
    """
    Health check endpoint for container orchestration and load balancers.

    This endpoint is used by:
    - Docker health checks
    - Kubernetes liveness/readiness probes
    - Load balancers to determine if the service is healthy

    Returns 200 if the application is running.
    """
    return {"status": "healthy"}
