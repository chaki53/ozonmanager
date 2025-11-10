from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from datetime import datetime, timedelta, timezone
from app.db.session import get_db
from app.core.security import get_current_user
from app.models.user import User
from app.models.ozon import OzonAccount
from app.services.ozon_sync import sync_analytics

router = APIRouter(prefix="/sync", tags=["sync"])

def require_manager(user: User = Depends(get_current_user)) -> User:
    if user.role not in ("admin","manager"):
        raise HTTPException(403, "Managers/Admins only")
    return user

@router.post("/run")
def run_sync(account_id: int | None = None, date_from: str | None = None, date_to: str | None = None, db: Session = Depends(get_db), _: User = Depends(require_manager)):
    if not date_to: date_to = datetime.now(timezone.utc).date().isoformat()
    if not date_from:
        date_from = (datetime.fromisoformat(date_to) - timedelta(days=30)).date().isoformat()
    accounts = []
    if account_id:
        acc = db.get(OzonAccount, account_id)
        if not acc: raise HTTPException(404, "Account not found")
        accounts = [acc]
    else:
        accounts = db.query(OzonAccount).filter(OzonAccount.is_active == True).all()
    total = 0
    for acc in accounts:
        total += sync_analytics(db, acc, date_from, date_to)
    return {"ok": True, "accounts": len(accounts), "inserted": total, "range": [date_from, date_to]}
