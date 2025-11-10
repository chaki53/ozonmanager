import os
from app.models.user import User
from app.db.session import SessionLocal
try:
    from app.core.security import get_password_hash
except Exception:
    from app.core.password import get_password_hash  # fallback

def seed_first_admin(session: SessionLocal):
    email = os.getenv("FIRST_ADMIN_EMAIL", "admin@local").strip().lower()
    password = os.getenv("FIRST_ADMIN_PASSWORD", "admin123")
    user = session.query(User).filter(User.email == email).first()
    if user:
        return
    u = User(email=email, hashed_password=get_password_hash(password), role="admin", is_active=True)
    session.add(u)
    session.commit()
