from fastapi import APIRouter
from app.core.config import get_settings
from app.models.schemas import HealthResponse

router = APIRouter(tags=["health"])


@router.get("/health", response_model=HealthResponse)
async def health() -> HealthResponse:
    settings = get_settings()
    return HealthResponse(
        status="ok",
        app_name=settings.app_name,
        version=settings.app_version,
        ai_mode=settings.ai_mode,
        embedding_provider=settings.embedding_provider,
        vector_store_provider=settings.vector_store_provider,
    )
