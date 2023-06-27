from typing import Optional

from pydantic import BaseModel, validator, EmailStr


class CreateUser(BaseModel):
    name: str
    password: str
    email: EmailStr

    @validator('password')
    def secure_password(cls, value):
        if len(value) < 8:
            raise ValueError('Password is too short')
        return value


class UpdateUser(BaseModel):
    name: Optional[str]
    password: Optional[str]
    email: Optional[EmailStr]

    @validator('password')
    def secure_password(cls, value):
        if len(value) < 8:
            raise ValueError('Password is too short')
        return value


class CreateAdvertisement(BaseModel):
    title: str
    description: str
    owner: str
    user_id: Optional[int]

    @validator('title')
    def validate_title(cls, value):
        if value and len(value) < 5:
            raise ValueError('Title is too short')
        return value

    @validator('description')
    def validate_description(cls, value):
        if value and len(value) < 10:
            raise ValueError('Description is too short')
        return value


class UpdateAdvertisement(BaseModel):
    title: Optional[str]
    description: Optional[str]
    owner: Optional[str]
    user_id: Optional[int]

    @validator('title')
    def validate_title(cls, value):
        if value and len(value) < 5:
            raise ValueError('Title is too short')
        return value

    @validator('description')
    def validate_description(cls, value):
        if value and len(value) < 10:
            raise ValueError('Description is too short')
        return value
