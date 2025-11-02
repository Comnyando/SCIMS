from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.config import settings
from app.middleware.analytics import AnalyticsMiddleware
from app.routers import (
    auth,
    items,
    locations,
    ships,
    inventory,
    canonical_locations,
    blueprints,
    crafts,
    sources,
    optimization,
    goals,
    analytics,
)

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

# Add analytics middleware (logs usage events if user has consented)
app.add_middleware(AnalyticsMiddleware)

# Include routers
app.include_router(auth.router)
app.include_router(items.router)
app.include_router(locations.router)
app.include_router(ships.router)
app.include_router(inventory.router)
app.include_router(canonical_locations.router)
app.include_router(blueprints.router)
app.include_router(crafts.router)
app.include_router(sources.router)
app.include_router(optimization.router)
app.include_router(goals.router)
app.include_router(analytics.router)


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
