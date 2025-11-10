from fastapi import Depends, HTTPException, status
from app.api.deps import get_current_user

ROLE_ORDER = {"viewer": 0, "manager": 1, "admin": 2}

def require_role(min_role: str):
    def _role_guard(user=Depends(get_current_user)):
        if ROLE_ORDER.get(user.role, -1) < ROLE_ORDER[min_role]:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="forbidden")
        return user
    return _role_guard
