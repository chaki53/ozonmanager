from fastapi import APIRouter, Depends
from app.services.sync import force_sync_all
from app.core.rbac import require_role

router = APIRouter(prefix="/sync", tags=["sync"])

@router.post("/run", dependencies=[Depends(require_role("manager"))])
def run_sync():
    force_sync_all()
    return {"ok": True}
