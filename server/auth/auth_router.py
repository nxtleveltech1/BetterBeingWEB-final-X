from fastapi import APIRouter, Depends, HTTPException, status, BackgroundTasks
from fastapi.security import HTTPAuthorizationCredentials
from datetime import datetime, timedelta
from typing import Dict, Any
import secrets
import os

from auth.models import (
    UserRegister, UserLogin, UserResponse, TokenResponse, 
    PasswordReset, PasswordResetConfirm, RefreshToken,
    EmailVerification, EmailVerificationConfirm
)
from main import (
    get_db, get_redis, get_current_user, get_password_hash, 
    verify_password, create_access_token, create_refresh_token,
    security, limiter, ACCESS_TOKEN_EXPIRE_MINUTES
)

auth_router = APIRouter()

async def send_verification_email(email: str, token: str):
    """Mock email sending function - implement with actual email service"""
    print(f"📧 Verification email sent to {email} with token {token}")

async def send_password_reset_email(email: str, token: str):
    """Mock email sending function - implement with actual email service"""
    print(f"🔑 Password reset email sent to {email} with token {token}")

@auth_router.post("/register", response_model=TokenResponse)
@limiter.limit("5/minute")
async def register(
    user_data: UserRegister,
    background_tasks: BackgroundTasks,
    db=Depends(get_db),
    redis=Depends(get_redis)
):
    # Check if user already exists
    existing_user = await db.fetchrow(
        "SELECT id FROM users WHERE email = $1",
        user_data.email
    )
    
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )
    
    # Hash password
    hashed_password = get_password_hash(user_data.password)
    
    # Create user
    user = await db.fetchrow(
        """
        INSERT INTO users (email, password_hash, first_name, last_name, created_at, updated_at)
        VALUES ($1, $2, $3, $4, $5, $6)
        RETURNING id, email, first_name, last_name, email_verified, created_at, updated_at
        """,
        user_data.email,
        hashed_password,
        user_data.first_name,
        user_data.last_name,
        datetime.utcnow(),
        datetime.utcnow()
    )
    
    # Generate verification token
    verification_token = secrets.token_urlsafe(32)
    await redis.setex(
        f"email_verification:{verification_token}",
        3600 * 24,  # 24 hours
        user["email"]
    )
    
    # Send verification email
    background_tasks.add_task(send_verification_email, user["email"], verification_token)
    
    # Create tokens
    access_token = create_access_token(data={"sub": str(user["id"])})
    refresh_token = create_refresh_token(data={"sub": str(user["id"])})
    
    # Store refresh token
    await redis.setex(
        f"refresh_token:{user['id']}",
        86400 * 7,  # 7 days
        refresh_token
    )
    
    user_response = UserResponse(**user)
    
    return TokenResponse(
        access_token=access_token,
        refresh_token=refresh_token,
        expires_in=ACCESS_TOKEN_EXPIRE_MINUTES * 60,
        user=user_response
    )

@auth_router.post("/login", response_model=TokenResponse)
@limiter.limit("10/minute")
async def login(
    credentials: UserLogin,
    db=Depends(get_db),
    redis=Depends(get_redis)
):
    # Get user from database
    user = await db.fetchrow(
        """
        SELECT id, email, password_hash, first_name, last_name, 
               email_verified, created_at, updated_at
        FROM users WHERE email = $1
        """,
        credentials.email
    )
    
    if not user or not verify_password(credentials.password, user["password_hash"]):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password"
        )
    
    # Create tokens
    access_token = create_access_token(data={"sub": str(user["id"])})
    refresh_token = create_refresh_token(data={"sub": str(user["id"])})
    
    # Store refresh token
    await redis.setex(
        f"refresh_token:{user['id']}",
        86400 * 7,  # 7 days
        refresh_token
    )
    
    # Update last login
    await db.execute(
        "UPDATE users SET last_login = $1 WHERE id = $2",
        datetime.utcnow(),
        user["id"]
    )
    
    user_response = UserResponse(
        id=user["id"],
        email=user["email"],
        first_name=user["first_name"],
        last_name=user["last_name"],
        email_verified=user["email_verified"],
        created_at=user["created_at"],
        updated_at=user["updated_at"]
    )
    
    return TokenResponse(
        access_token=access_token,
        refresh_token=refresh_token,
        expires_in=ACCESS_TOKEN_EXPIRE_MINUTES * 60,
        user=user_response
    )

@auth_router.post("/refresh", response_model=Dict[str, Any])
async def refresh_access_token(
    refresh_data: RefreshToken,
    redis=Depends(get_redis)
):
    try:
        from jose import jwt, JWTError
        
        payload = jwt.decode(
            refresh_data.refresh_token, 
            os.getenv("JWT_SECRET_KEY"), 
            algorithms=[os.getenv("JWT_ALGORITHM", "HS256")]
        )
        
        user_id = payload.get("sub")
        token_type = payload.get("type")
        
        if not user_id or token_type != "refresh":
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid refresh token"
            )
        
        # Check if refresh token exists in Redis
        stored_token = await redis.get(f"refresh_token:{user_id}")
        if not stored_token or stored_token != refresh_data.refresh_token:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Refresh token not found or expired"
            )
        
        # Create new access token
        new_access_token = create_access_token(data={"sub": user_id})
        
        return {
            "access_token": new_access_token,
            "token_type": "bearer",
            "expires_in": ACCESS_TOKEN_EXPIRE_MINUTES * 60
        }
        
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid refresh token"
        )

@auth_router.post("/logout")
async def logout(
    user=Depends(get_current_user),
    redis=Depends(get_redis)
):
    # Remove refresh token from Redis
    await redis.delete(f"refresh_token:{user['id']}")
    
    return {"message": "Successfully logged out"}

@auth_router.get("/me", response_model=UserResponse)
async def get_current_user_info(user=Depends(get_current_user)):
    return UserResponse(**user)

@auth_router.post("/forgot-password")
@limiter.limit("3/minute")
async def forgot_password(
    password_reset: PasswordReset,
    background_tasks: BackgroundTasks,
    db=Depends(get_db),
    redis=Depends(get_redis)
):
    # Check if user exists
    user = await db.fetchrow(
        "SELECT id, email FROM users WHERE email = $1",
        password_reset.email
    )
    
    # Always return success to prevent email enumeration
    if user:
        # Generate reset token
        reset_token = secrets.token_urlsafe(32)
        await redis.setex(
            f"password_reset:{reset_token}",
            3600,  # 1 hour
            str(user["id"])
        )
        
        # Send password reset email
        background_tasks.add_task(send_password_reset_email, user["email"], reset_token)
    
    return {"message": "If the email exists, a reset link has been sent"}

@auth_router.post("/reset-password")
async def reset_password(
    reset_data: PasswordResetConfirm,
    db=Depends(get_db),
    redis=Depends(get_redis)
):
    # Get user ID from token
    user_id = await redis.get(f"password_reset:{reset_data.token}")
    
    if not user_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid or expired reset token"
        )
    
    # Hash new password
    new_password_hash = get_password_hash(reset_data.new_password)
    
    # Update password
    await db.execute(
        "UPDATE users SET password_hash = $1, updated_at = $2 WHERE id = $3",
        new_password_hash,
        datetime.utcnow(),
        int(user_id)
    )
    
    # Delete reset token
    await redis.delete(f"password_reset:{reset_data.token}")
    
    # Invalidate all refresh tokens for this user
    await redis.delete(f"refresh_token:{user_id}")
    
    return {"message": "Password successfully reset"}

@auth_router.post("/verify-email")
async def verify_email(
    verification: EmailVerificationConfirm,
    db=Depends(get_db),
    redis=Depends(get_redis)
):
    # Get email from token
    email = await redis.get(f"email_verification:{verification.token}")
    
    if not email:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid or expired verification token"
        )
    
    # Update user verification status
    await db.execute(
        "UPDATE users SET email_verified = true, updated_at = $1 WHERE email = $2",
        datetime.utcnow(),
        email
    )
    
    # Delete verification token
    await redis.delete(f"email_verification:{verification.token}")
    
    return {"message": "Email successfully verified"}

@auth_router.post("/resend-verification")
@limiter.limit("3/minute")
async def resend_verification(
    email_request: EmailVerification,
    background_tasks: BackgroundTasks,
    db=Depends(get_db),
    redis=Depends(get_redis)
):
    # Check if user exists and is not verified
    user = await db.fetchrow(
        "SELECT id, email, email_verified FROM users WHERE email = $1",
        email_request.email
    )
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    if user["email_verified"]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already verified"
        )
    
    # Generate new verification token
    verification_token = secrets.token_urlsafe(32)
    await redis.setex(
        f"email_verification:{verification_token}",
        3600 * 24,  # 24 hours
        user["email"]
    )
    
    # Send verification email
    background_tasks.add_task(send_verification_email, user["email"], verification_token)
    
    return {"message": "Verification email sent"}