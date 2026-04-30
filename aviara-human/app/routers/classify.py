from fastapi import APIRouter, Depends
from app.models import ClassifyRequest, ClassifyResponse
from app.services import classify_intent
from app.utils.auth import verify_api_key
from app.utils.logger import get_logger

router = APIRouter()
logger = get_logger(__name__)


@router.post("/classify", response_model=ClassifyResponse)
async def classify(payload: ClassifyRequest, api_key: str = Depends(verify_api_key)):
    logger.info(f"Classify request: {payload.message[:60]}")
    return await classify_intent(payload)
