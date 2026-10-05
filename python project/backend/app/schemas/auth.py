from pydantic import BaseModel, EmailStr, Field


class UserLogin(BaseModel):
    username_or_email: str = Field(..., min_length=3, max_length=255)
    password: str = Field(..., min_length=8, max_length=255)


class UserRegister(BaseModel):
    username: str = Field(..., min_length=3, max_length=50)
    email: EmailStr
    full_name: str = Field(..., min_length=2, max_length=200)
    password: str = Field(..., min_length=8, max_length=255)


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"


class TokenData(BaseModel):
    user_id: str | None = None
    username: str | None = None
    role: str | None = None


class UserResponse(BaseModel):
    id: str
    username: str
    email: str
    full_name: str
    role: str
    is_active: bool = True
    is_verified: bool = False

    model_config = {"from_attributes": True}
