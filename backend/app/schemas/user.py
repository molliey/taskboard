
from pydantic import BaseModel, EmailStr, Field, ConfigDict
from datetime import datetime
from typing import Optional

# Base schema with common user fields
class UserBase(BaseModel):
    """Base user schema with common fields."""
    email: EmailStr
    username: str = Field(..., min_length=3, max_length=50)
    full_name: Optional[str] = Field(None, max_length=100)

# Schema for creating a new user
class UserCreate(UserBase):
    """Schema for user registration."""
    password: str = Field(..., min_length=6)

# Schema for updating user information
class UserUpdate(BaseModel):
    """Schema for updating user profile."""
    email: Optional[EmailStr] = None
    username: Optional[str] = Field(None, min_length=3, max_length=50)
    full_name: Optional[str] = Field(None, min_length=1, max_length=100)
    password: Optional[str] = Field(None, min_length=6)

# Schema for user stored in database (internal use)
class UserInDB(UserBase):
    """Internal schema including database fields."""
    id: int
    is_active: bool
    created_at: datetime
    updated_at: datetime
    hashed_password: str
    
    model_config = ConfigDict(from_attributes=True)

# Schema for API responses (public)
class User(BaseModel):
    """Public user schema for API responses."""
    id: int
    email: EmailStr
    username: str
    full_name: Optional[str] = None
    
    model_config = ConfigDict(from_attributes=True)

# Authentication schemas
class UserLogin(BaseModel):
    """Schema for login request."""
    email: EmailStr
    password: str

class Token(BaseModel):
    """Schema for JWT token response."""
    access_token: str
    token_type: str = "bearer"

class TokenData(BaseModel):
    """Schema for decoded token data."""
    username: Optional[str] = None
