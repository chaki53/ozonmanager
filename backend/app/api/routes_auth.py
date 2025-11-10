from fastapi import APIRouter, Depends, HTTPException, status, Request
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.models.user import User
from app.core.security import verify_password, create_access_token, get_current_user, get_password_hash, require_admin
from app.schemas.auth import TokenOut, RegisterIn, ChangePasswordIn, ChangeEmailIn, UserOut

router = APIRouter(tags=["auth"])

@router.post("/auth/login", response_model=TokenOut)
def login(request: Request, form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    username = (form_data.username or "").strip().lower()
    user = db.query(User).filter(User.email == username).first()
    if not user or not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")
    if getattr(user, "is_active", True) is False:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="User is disabled")
    token = create_access_token(subject=str(user.id))
    return {"access_token": token, "token_type": "bearer"}

@router.post("/auth/register", response_model=UserOut)
def register(data: RegisterIn, db: Session = Depends(get_db), admin: User = Depends(require_admin)):
    email = data.email.lower()
    if db.query(User).filter(User.email == email).first():
        raise HTTPException(400, "Email already used")
    user = User(email=email, hashed_password=get_password_hash(data.password), role="viewer", is_active=True)
    db.add(user)
    db.commit()
    db.refresh(user)
    return UserOut(id=user.id, email=user.email, role=user.role, is_active=user.is_active)

@router.get("/auth/me", response_model=UserOut)
def me(current: User = Depends(get_current_user)):
    return UserOut(id=current.id, email=current.email, role=current.role, is_active=current.is_active)

@router.post("/auth/change-password")
def change_password(payload: ChangePasswordIn, db: Session = Depends(get_db), current: User = Depends(get_current_user)):
    if not verify_password(payload.current_password, current.hashed_password):
        raise HTTPException(400, "Wrong current password")
    current.hashed_password = get_password_hash(payload.new_password)
    db.add(current); db.commit()
    return {"ok": True}

@router.post("/auth/change-email", response_model=UserOut)
def change_email(payload: ChangeEmailIn, db: Session = Depends(get_db), current: User = Depends(get_current_user)):
    if not verify_password(payload.password, current.hashed_password):
        raise HTTPException(400, "Wrong password")
    new_email = payload.new_email.lower()
    if new_email == current.email:
        return UserOut(id=current.id, email=current.email, role=current.role, is_active=current.is_active)
    if db.query(User).filter(User.email == new_email).first():
        raise HTTPException(400, "Email already used")
    current.email = new_email
    db.add(current); db.commit(); db.refresh(current)
    return UserOut(id=current.id, email=current.email, role=current.role, is_active=current.is_active)
