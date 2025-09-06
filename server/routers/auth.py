from fastapi import APIRouter, Depends, HTTPException, status, Body, Response, Request
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel, EmailStr, validator
from typing import Optional, Dict, Any
from datetime import datetime, timedelta
import asyncpg
from jose import JWTError, jwt
from passlib.context import CryptContext
import os
import logging
from slowapi import Limiter
from slowapi.util import get_remote_address

from main import get_db, get_redis, create_access_token, create_refresh_token, verify_password, get_password_hash

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/auth", tags=["authentication"])
security = HTTPBearer()
limiter = Limiter(key_func=get_remote_address)

# JWT settings
SECRET_KEY = os.getenv("JWT_SECRET_KEY", "your-secret-key-change-in-production")
ALGORITHM = os.getenv("JWT_ALGORITHM", "HS256")
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "30"))
REFRESH_TOKEN_EXPIRE_DAYS = int(os.getenv("REFRESH_TOKEN_EXPIRE_DAYS", "7"))

# Pydantic models
class UserRegister(BaseModel):
    email: EmailStr
    password: str
    first_name: str
    last_name: str
    marketing_consent: Optional[bool] = False
    
    @validator('password')
    def validate_password(cls, v):
        if len(v) < 8:
            raise ValueError('Password must be at least 8 characters long')
        if not any(char.isdigit() for char in v):
            raise ValueError('Password must contain at least one number')
        if not any(char.isupper() for char in v):
            raise ValueError('Password must contain at least one uppercase letter')
        return v

class UserLogin(BaseModel):
    email: EmailStr
    password: str

class Token(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"

class UserResponse(BaseModel):
    id: int
    email: str
    first_name: str
    last_name: str
    email_verified: bool
    created_at: datetime

class ProfileUpdate(BaseModel):
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    phone: Optional[str] = None
    date_of_birth: Optional[str] = None
    gender: Optional[str] = None
    marketing_consent: Optional[bool] = None

class PasswordChange(BaseModel):
    current_password: str
    new_password: str
    
    @validator('new_password')
    def validate_new_password(cls, v):
        if len(v) < 8:
            raise ValueError('Password must be at least 8 characters long')
        if not any(char.isdigit() for char in v):
            raise ValueError('Password must contain at least one number')
        if not any(char.isupper() for char in v):
            raise ValueError('Password must contain at least one uppercase letter')
        return v

@router.post("/register", response_model=Dict[str, Any], status_code=status.HTTP_201_CREATED)
@limiter.limit("5/minute")
async def register_user(
    request: Request,
    user_data: UserRegister,
    db=Depends(get_db)
):
    """Register a new user"""
    
    # Check if user already exists
    existing_user = await db.fetchrow(
        "SELECT id FROM users WHERE email = $1",
        user_data.email
    )
    
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User with this email already exists"
        )
    
    # Hash password
    hashed_password = get_password_hash(user_data.password)
    
    # Create user
    try:
        user = await db.fetchrow("""
            INSERT INTO users (email, password, first_name, last_name, marketing_consent)
            VALUES ($1, $2, $3, $4, $5)
            RETURNING id, email, first_name, last_name, email_verified, created_at
        """, user_data.email, hashed_password, user_data.first_name, user_data.last_name, user_data.marketing_consent)
        
        # Create tokens
        access_token = create_access_token({"sub": str(user["id"])})
        refresh_token = create_refresh_token({"sub": str(user["id"])})
        
        # Store refresh token in Redis
        redis_client = await get_redis()
        await redis_client.setex(
            f"refresh_token:{user['id']}",
            timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS),
            refresh_token
        )
        
        return {
            "success": True,
            "message": "User registered successfully. Please check your email to verify your account.",
            "user": {
                "id": user["id"],
                "email": user["email"],
                "first_name": user["first_name"],
                "last_name": user["last_name"],
                "email_verified": user["email_verified"],
                "created_at": user["created_at"]
            },
            "tokens": {
                "access_token": access_token,
                "refresh_token": refresh_token,
                "token_type": "bearer"
            }
        }
        
    except Exception as e:
        logger.error(f"Registration error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create user"
        )

@router.post("/login", response_model=Dict[str, Any])
@limiter.limit("5/minute")
async def login_user(
    request: Request,
    login_data: UserLogin,
    db=Depends(get_db)
):
    """Login user"""
    
    # Find user
    user = await db.fetchrow(
        "SELECT id, email, password, first_name, last_name, email_verified FROM users WHERE email = $1",
        login_data.email
    )
    
    if not user or not verify_password(login_data.password, user["password"]):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password"
        )
    
    # Create tokens
    access_token = create_access_token({"sub": str(user["id"])})
    refresh_token = create_refresh_token({"sub": str(user["id"])})
    
    # Store refresh token in Redis
    redis_client = await get_redis()
    await redis_client.setex(
        f"refresh_token:{user['id']}",
        timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS),
        refresh_token
    )
    
    # Update last login
    await db.execute(
        "UPDATE users SET last_login = $1 WHERE id = $2",
        datetime.utcnow(), user["id"]
    )
    
    return {
        "success": True,
        "message": "Login successful",
        "user": {
            "id": user["id"],
            "email": user["email"],
            "first_name": user["first_name"],
            "last_name": user["last_name"],
            "email_verified": user["email_verified"]
        },
        "tokens": {
            "access_token": access_token,
            "refresh_token": refresh_token,
            "token_type": "bearer"
        },
        "requires_email_verification": not user["email_verified"]
    }

@router.post("/refresh", response_model=Token)
@limiter.limit("10/minute")
async def refresh_token(
    request: Request,
    refresh_token: str = Body(..., embed=True),
    db=Depends(get_db)
):
    """Refresh access token"""
    
    try:
        # Verify refresh token
        payload = jwt.decode(refresh_token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id = payload.get("sub")
        token_type = payload.get("type")
        
        if not user_id or token_type != "refresh":
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid refresh token"
            )
        
        # Verify refresh token exists in Redis
        redis_client = await get_redis()
        stored_token = await redis_client.get(f"refresh_token:{user_id}")
        
        if not stored_token or stored_token != refresh_token:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Refresh token invalid or expired"
            )
        
        # Create new tokens
        new_access_token = create_access_token({"sub": user_id})
        new_refresh_token = create_refresh_token({"sub": user_id})
        
        # Update refresh token in Redis
        await redis_client.setex(
            f"refresh_token:{user_id}",
            timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS),
            new_refresh_token
        )
        
        return {
            "access_token": new_access_token,
            "refresh_token": new_refresh_token,
            "token_type": "bearer"
        }
        
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid refresh token"
        )

@router.post("/logout")
@limiter.limit("10/minute")
async def logout_user(
    request: Request,
    refresh_token: str = Body(..., embed=True),
    db=Depends(get_db)
):
    """Logout user (invalidate refresh token)"""
    
    try:
        payload = jwt.decode(refresh_token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id = payload.get("sub")
        
        if user_id:
            redis_client = await get_redis()
            await redis_client.delete(f"refresh_token:{user_id}")
        
        return {"success": True, "message": "Logged out successfully"}
        
    except JWTError:
        # Even if token is invalid, consider it logged out
        return {"success": True, "message": "Logged out successfully"}

@router.get("/me", response_model=Dict[str, Any])
async def get_current_user_profile(
    current_user: Dict[str, Any] = Depends(get_current_user),
    db=Depends(get_db)
):
    """Get current user profile"""
    
    user = await db.fetchrow("""
        SELECT id, email, first_name, last_name, phone, date_of_birth, gender, 
               marketing_consent, email_verified, two_factor_enabled, 
               profile_image_url, created_at, last_login
        FROM users WHERE id = $1
    """, current_user["id"])
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    return {
        "success": True,
        "user": {
            "id": user["id"],
            "email": user["email"],
            "first_name": user["first_name"],
            "last_name": user["last_name"],
            "phone": user["phone"],
            "date_of_birth": user["date_of_birth"],
            "gender": user["gender"],
            "marketing_consent": user["marketing_consent"],
            "email_verified": user["email_verified"],
            "two_factor_enabled": user["two_factor_enabled"],
            "profile_image_url": user["profile_image_url"],
            "created_at": user["created_at"],
            "last_login": user["last_login"]
        }
    }

@router.put("/profile", response_model=Dict[str, Any])
async def update_user_profile(
    profile_data: ProfileUpdate,
    current_user: Dict[str, Any] = Depends(get_current_user),
    db=Depends(get_db)
):
    """Update user profile"""
    
    # Build update query dynamically
    update_fields = {}
    if profile_data.first_name is not None:
        update_fields["first_name"] = profile_data.first_name
    if profile_data.last_name is not None:
        update_fields["last_name"] = profile_data.last_name
    if profile_data.phone is not None:
        update_fields["phone"] = profile_data.phone
    if profile_data.date_of_birth is not None:
        update_fields["date_of_birth"] = profile_data.date_of_birth
    if profile_data.gender is not None:
        update_fields["gender"] = profile_data.gender
    if profile_data.marketing_consent is not None:
        update_fields["marketing_consent"] = profile_data.marketing_consent
    
    if not update_fields:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No fields to update"
        )
    
    update_fields["updated_at"] = datetime.utcnow()
    
    # Build SQL query
    set_clause = ", ".join([f"{field} = ${i+1}" for i, field in enumerate(update_fields)])
    values = list(update_fields.values()) + [current_user["id"]]
    
    try:
        user = await db.fetchrow(f"""
            UPDATE users 
            SET {set_clause}
            WHERE id = ${len(update_fields) + 1}
            RETURNING id, email, first_name, last_name, phone, date_of_birth, 
                     gender, marketing_consent, updated_at
        """, *values)
        
        return {
            "success": True,
            "message": "Profile updated successfully",
            "user": {
                "id": user["id"],
                "email": user["email"],
                "first_name": user["first_name"],
                "last_name": user["last_name"],
                "phone": user["phone"],
                "date_of_birth": user["date_of_birth"],
                "gender": user["gender"],
                "marketing_consent": user["marketing_consent"],
                "updated_at": user["updated_at"]
            }
        }
        
    except Exception as e:
        logger.error(f"Profile update error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update profile"
        )

@router.post("/change-password", response_model=Dict[str, Any])
@limiter.limit("5/minute")
async def change_password(
    request: Request,
    password_data: PasswordChange,
    current_user: Dict[str, Any] = Depends(get_current_user),
    db=Depends(get_db)
):
    """Change user password"""
    
    # Get current password
    user = await db.fetchrow(
        "SELECT password FROM users WHERE id = $1",
        current_user["id"]
    )
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    # Verify current password
    if not verify_password(password_data.current_password, user["password"]):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Current password is incorrect"
        )
    
    # Hash new password
    new_hashed_password = get_password_hash(password_data.new_password)
    
    # Update password
    try:
        await db.execute(
            "UPDATE users SET password = $1, updated_at = $2 WHERE id = $3",
            new_hashed_password, datetime.utcnow(), current_user["id"]
        )
        
        # Invalidate all refresh tokens
        redis_client = await get_redis()
        await redis_client.delete(f"refresh_token:{current_user['id']}")
        
        return {
            "success": True,
            "message": "Password changed successfully. Please login again on other devices."
        }
        
    except Exception as e:
        logger.error(f"Password change error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to change password"
        )