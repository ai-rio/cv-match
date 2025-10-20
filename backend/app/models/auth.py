"""Authentication models for the CV-Match backend."""

from pydantic import BaseModel
from typing import Optional

class User(BaseModel):
    """User model for authentication."""
    
    id: str
    email: str
    is_active: bool = True
    
    class Config:
        """Pydantic configuration."""
        orm_mode = True

class UserCreate(BaseModel):
    """User creation model."""
    
    email: str
    password: str

class UserUpdate(BaseModel):
    """User update model."""
    
    email: Optional[str] = None
    is_active: Optional[bool] = None