from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from sqlalchemy.orm import Session
from app.db.session import get_db_session
from app.models.account import Account
from app.core.rbac import require_role
from app.api.deps import get_current_user
from app.services.ozon_client import OzonClient

router = APIRouter(prefix="/accounts", tags=["accounts"])

class AccountIn(BaseModel):
    name: str
    ozon_client_id: str
    ozon_api_key: str
    tz: str | None = "Europe/Moscow"

class AccountOut(BaseModel):
    id: str
    name: str
    tz: str

@router.get("", response_model=list[AccountOut])
def list_accounts(db: Session = Depends(get_db_session), user=Depends(get_current_user)):
    rows = db.query(Account).all()
    return [AccountOut(id=str(r.id), name=r.name, tz=r.tz) for r in rows]

@router.post("", dependencies=[Depends(require_role("manager"))])
def create_account(payload: AccountIn, db: Session = Depends(get_db_session)):
    acc = Account(name=payload.name, ozon_client_id=payload.ozon_client_id,
                  ozon_api_key_enc=payload.ozon_api_key, tz=payload.tz or "Europe/Moscow")
    db.add(acc); db.commit()
    return {"ok": True}

@router.delete("/{account_id}", dependencies=[Depends(require_role("admin"))])
def delete_account(account_id: str, db: Session = Depends(get_db_session)):
    acc = db.query(Account).get(account_id)
    if not acc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="not found")
    db.delete(acc); db.commit()
    return {"ok": True}

class TestPayload(BaseModel):
    ozon_client_id: str
    ozon_api_key: str

@router.post("/test", dependencies=[Depends(require_role("manager"))])
def test_account(payload: TestPayload):
    try:
        client = OzonClient(payload.ozon_client_id, payload.ozon_api_key)
        data = client.list_warehouses()
        return {"ok": True, "warehouses": len(data)}
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"auth_failed: {e}")
