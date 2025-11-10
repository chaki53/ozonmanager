from sqlalchemy.orm import Session
from app.core.config import settings
from app.models.user import User
from app.core.security import get_password_hash

def seed_first_admin(db: Session):
    if not db.query(User).count():
        admin = User(
            email=settings.FIRST_ADMIN_EMAIL,
            hashed_password=get_password_hash(settings.FIRST_ADMIN_PASSWORD),
            role="admin",
            is_active=True,
        )
        db.add(admin)
        db.commit()
