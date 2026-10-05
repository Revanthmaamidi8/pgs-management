from pydantic import BaseModel, EmailStr, Field


class UserCreate(BaseModel):
    username: str = Field(..., min_length=3, max_length=50)
    email: EmailStr
    full_name: str = Field(..., min_length=2, max_length=200)
    password: str = Field(..., min_length=8, max_length=255)


class UserOut(BaseModel):
    id: str
    username: str
    email: str
    full_name: str
    is_active: bool

    model_config = {"from_attributes": True}
