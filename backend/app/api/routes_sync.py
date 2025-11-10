from fastapi import APIRouter, Depends, Body
from typing import List, Optional
from app.core.rbac import require_role
from app.services.sync import sync_accounts

router = APIRouter(prefix="/sync", tags=["sync"])

@router.post("/run", dependencies=[Depends(require_role("manager"))])
def run_sync(payload: dict = Body(None)):
    # payload: { "account_ids": [..], "sales_days": 14 }
    account_ids: Optional[List[str]] = None
    sales_days = 14
    if payload:
        account_ids = payload.get("account_ids")
        sales_days = payload.get("sales_days", 14)
    sync_accounts(account_ids=account_ids, sales_days=sales_days)
    return {"ok": True}
