from fastapi import APIRouter, Depends
from app.models import EnrichRequest, EnrichResponse
from app.services import enrich_lead
from app.utils.auth import verify_api_key
from app.utils.logger import get_logger

router = APIRouter()
logger = get_logger(__name__)


@router.post("/enrich", response_model=EnrichResponse)
async def enrich(payload: EnrichRequest, api_key: str = Depends(verify_api_key)):
    logger.info(f"Enrich request for: {payload.email}")
    return await enrich_lead(payload)
