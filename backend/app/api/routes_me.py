from fastapi import APIRouter, Depends
from pydantic import BaseModel
from sqlalchemy.orm import Session
from app.api.deps import get_current_user
from app.db.session import get_db_session
from app.models.user import User

router = APIRouter(prefix="/me", tags=["me"])

class ChatPayload(BaseModel):
    telegram_chat_id: str

@router.post("/telegram")
def set_telegram_chat(payload: ChatPayload, user=Depends(get_current_user), db: Session = Depends(get_db_session)):
    u: User = db.query(User).filter(User.id == user.id).first()
    u.telegram_chat_id = payload.telegram_chat_id
    db.commit()
    return {"ok": True}
