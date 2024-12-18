from datetime import date, datetime
from typing import Optional

from pydantic import BaseModel, Field, EmailStr


class ContactBase(BaseModel):
    name: str = Field(max_length=30)
    surname: str = Field(max_length=30)
    email: EmailStr = Field(max_length=50)
    phone_number: str = Field(max_length=20)
    birthday: Optional[date]

    class Config:
        orm_mode = True


class ContactResponse(ContactBase):
    id: int

    class Config:
        orm_mode = True


class ContactCreate(ContactBase):
    pass


class ContactUpdate(BaseModel):
    name: str | None = Field(default=None, max_length=30)
    surname: str | None = Field(default=None, max_length=30)
    email: EmailStr | None = None
    phone_number: str | None = Field(default=None, max_length=20)
    birthday: date | None = None

class UserModel(BaseModel):
    username: str = Field(min_length=5, max_length=16)
    email: EmailStr
    password: str = Field(min_length=6, max_length=10)


class UserDb(BaseModel):
    id: int
    username: str
    email: str
    created_at: datetime
    avatar: str

    class Config:
        orm_mode = True


class UserResponse(BaseModel):
    user: UserDb
    detail: str = "User successfully created"


class TokenModel(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"

class RequestEmail(BaseModel):
    email: EmailStr