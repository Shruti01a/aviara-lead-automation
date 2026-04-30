from fastapi import APIRouter
from app.models import HealthResponse
from app import config

router = APIRouter()


@router.get("/health", response_model=HealthResponse)
async def health():
    return HealthResponse(status="ok", version=config.VERSION)
