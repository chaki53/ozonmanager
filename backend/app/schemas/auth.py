from pydantic import BaseModel, EmailStr, Field

class TokenOut(BaseModel):
    access_token: str
    token_type: str = "bearer"

class RegisterIn(BaseModel):
    email: EmailStr
    password: str = Field(min_length=6, max_length=128)

class ChangePasswordIn(BaseModel):
    current_password: str
    new_password: str = Field(min_length=6, max_length=128)

class ChangeEmailIn(BaseModel):
    password: str
    new_email: EmailStr

class UserOut(BaseModel):
    id: int
    email: EmailStr
    role: str
    is_active: bool
