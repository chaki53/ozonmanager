from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session
from typing import List
from app.db.session import get_db
from app.core.security import require_admin, get_current_user
from app.models.ozon import OzonAccount
from app.integrations.ozon_client import OzonClient

router = APIRouter(prefix="/accounts", tags=["accounts"])

class AccountIn(BaseModel):
    name: str = Field(..., min_length=2)
    client_id: str
    api_key: str
    is_active: bool = True

class AccountOut(BaseModel):
    id: int
    name: str
    is_active: bool
    last_sync_at: str | None

@router.get("/", response_model=List[AccountOut])
def list_accounts(db: Session = Depends(get_db), user=Depends(get_current_user)):
    rows = db.query(OzonAccount).order_by(OzonAccount.id.desc()).all()
    return [{"id":r.id,"name":r.name,"is_active":r.is_active,"last_sync_at":r.last_sync_at.isoformat() if r.last_sync_at else None} for r in rows]

@router.post("/", response_model=AccountOut)
def create_account(payload: AccountIn, db: Session = Depends(get_db), admin=Depends(require_admin)):
    acc = OzonAccount(name=payload.name, client_id=payload.client_id, api_key=payload.api_key, is_active=payload.is_active)
    # sanity check
    if not OzonClient(acc.client_id, acc.api_key).health():
        raise HTTPException(400, "Ozon credentials check failed")
    db.add(acc); db.commit(); db.refresh(acc)
    return {"id":acc.id,"name":acc.name,"is_active":acc.is_active,"last_sync_at":acc.last_sync_at.isoformat() if acc.last_sync_at else None}

@router.delete("/{account_id}")
def delete_account(account_id: int, db: Session = Depends(get_db), admin=Depends(require_admin)):
    acc = db.get(OzonAccount, account_id)
    if not acc: raise HTTPException(404, "Not found")
    db.delete(acc); db.commit()
    return {"ok": True}
