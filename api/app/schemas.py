from pydantic import BaseModel, EmailStr, Field
from datetime import datetime
from typing import Optional

class UserBase(BaseModel):
    email: EmailStr
    name: str
    surname: str

class UserCreate(UserBase):
    password: str

class User(UserBase):
    id: int
    create_date: datetime
    last_login_date: Optional[datetime]

    class Config:
        from_attributes = True
        orm_mode = True

class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    email: Optional[str] = None

class PasswordBase(BaseModel):
    hesap_yeri: str
    username: str
    password: str = Field(..., description="Encrypted password")

class PasswordCreate(PasswordBase):
    pass

class Password(PasswordBase):
    id: int
    user_id: int

    class Config:
        from_attributes = True  # This enables ORM mode