from fastapi import APIRouter
from app.services.sync import force_sync_all

router = APIRouter(prefix="/sync", tags=["sync"])

@router.post("/run")
def run_sync():
    # Простая ручная синхронизация без авторизации для MVP (в проде повесить RBAC)
    force_sync_all()
    return {"ok": True}
