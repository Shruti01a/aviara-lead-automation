from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from app.routers import enrich_router, classify_router, health_router
from app import config
from app.utils.logger import get_logger

logger = get_logger(__name__)

app = FastAPI(
    title=config.APP_NAME,
    version=config.VERSION,
    description="AI-powered lead enrichment and intent classification API"
)


# register routes
app.include_router(enrich_router)
app.include_router(classify_router)
app.include_router(health_router)


# catch-all error handler so we never leak stack traces
@app.exception_handler(Exception)
async def global_error_handler(request: Request, exc: Exception):
    logger.error(f"Unhandled error on {request.url.path}: {exc}")
    return JSONResponse(
        status_code=500,
        content={"detail": "Something went wrong. Please try again."}
    )


@app.get("/")
async def root():
    return {"message": f"{config.APP_NAME} is running", "docs": "/docs"}


logger.info(f"{config.APP_NAME} v{config.VERSION} started")
