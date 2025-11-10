from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from sqlalchemy.orm import Session
from app.db.session import get_db_session
from app.core.rbac import require_role
from app.models.setting import Setting

router = APIRouter(prefix="/settings", tags=["settings"])

class KV(BaseModel):
    key: str
    value: str

@router.get("")
def list_settings(db: Session = Depends(get_db_session), _: str = Depends(require_role("admin"))):
    rows = db.query(Setting).all()
    return [{"key": r.key, "value": r.value} for r in rows]

@router.get("/{key}")
def get_setting(key: str, db: Session = Depends(get_db_session), _: str = Depends(require_role("admin"))):
    s = db.query(Setting).filter(Setting.key == key).first()
    if not s:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="not found")
    return {"key": s.key, "value": s.value}

@router.post("")
def upsert_settings(items: list[KV], db: Session = Depends(get_db_session), _: str = Depends(require_role("admin"))):
    for kv in items:
        s = db.query(Setting).filter(Setting.key == kv.key).first()
        if not s:
            s = Setting(key=kv.key, value=kv.value)
            db.add(s)
        else:
            s.value = kv.value
    db.commit()
    return {"ok": True}
