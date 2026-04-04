from fastapi import APIRouter, Depends

from app.dependencies import get_config_store
from app.schemas.contracts import HealthIndexConfigDTO
from backend.app.services.health_config_store.health_config_store import HealthConfigStore

router = APIRouter(prefix="/config")


@router.get("/health-index", response_model=HealthIndexConfigDTO)
async def get_health_index_config(
    config_store: HealthConfigStore = Depends(get_config_store),
) -> HealthIndexConfigDTO:
    return config_store.get()


@router.put("/health-index", response_model=HealthIndexConfigDTO)
async def update_health_index_config(
    payload: HealthIndexConfigDTO,
    config_store: HealthConfigStore = Depends(get_config_store),
) -> HealthIndexConfigDTO:
    return config_store.update(payload)
