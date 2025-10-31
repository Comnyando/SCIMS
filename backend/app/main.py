from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.config import settings

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


@app.get("/")
def read_root():
    return {
        "status": "ok",
        "app": settings.app_name,
        "environment": settings.environment,
        "version": "0.1.0"
    }


@app.get("/api/v1")
def read_api_root():
    return {
        "status": "ok",
        "app": settings.app_name,
        "environment": settings.environment,
        "version": "0.1.0",
        "api": "v1"
    }


@app.get("/health")
def health_check():
    return {"status": "healthy"}


@app.get("/api/v1/health")
def api_health_check():
    return {"status": "healthy"}
