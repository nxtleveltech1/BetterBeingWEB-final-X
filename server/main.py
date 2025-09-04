from fastapi import FastAPI, Depends, HTTPException, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from fastapi.middleware.gzip import GZipMiddleware
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from fastapi.responses import JSONResponse
from fastapi.openapi.utils import get_openapi
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
from slowapi.middleware import SlowAPIMiddleware
import asyncpg
import redis.asyncio as redis
from jose import JWTError, jwt
from passlib.context import CryptContext
from datetime import datetime, timedelta
from typing import Optional, List, Dict, Any
import os
from dotenv import load_dotenv
import logging
from contextlib import asynccontextmanager

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Security
security = HTTPBearer()
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# Rate limiting
limiter = Limiter(key_func=get_remote_address)

# JWT settings
SECRET_KEY = os.getenv("JWT_SECRET_KEY", "your-secret-key-change-in-production")
ALGORITHM = os.getenv("JWT_ALGORITHM", "HS256")
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "30"))
REFRESH_TOKEN_EXPIRE_DAYS = int(os.getenv("REFRESH_TOKEN_EXPIRE_DAYS", "7"))

# Database and Redis connections
pool = None
redis_client = None

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    global pool, redis_client
    
    try:
        # Initialize database pool
        pool = await asyncpg.create_pool(
            dsn=os.getenv("DATABASE_URL"),
            min_size=int(os.getenv("DB_MIN_CONNECTIONS", "2")),
            max_size=int(os.getenv("DB_MAX_CONNECTIONS", "20")),
            timeout=int(os.getenv("DB_CONNECTION_TIMEOUT", "30")),
            command_timeout=int(os.getenv("DB_QUERY_TIMEOUT", "30"))
        )
        logger.info("✅ Database pool initialized")
    except Exception as e:
        logger.error(f"❌ Failed to initialize database pool: {e}")
        pool = None
    
    try:
        # Initialize Redis
        redis_client = redis.from_url(
            os.getenv("REDIS_URL", "redis://localhost:6379"),
            password=os.getenv("REDIS_PASSWORD"),
            db=int(os.getenv("REDIS_DB", "0")),
            encoding="utf-8",
            decode_responses=True
        )
        await redis_client.ping()
        logger.info("✅ Redis client initialized")
    except Exception as e:
        logger.error(f"❌ Failed to initialize Redis: {e}")
        redis_client = None
    
    yield
    
    # Shutdown
    if pool:
        await pool.close()
        logger.info("✅ Database pool closed")
    
    if redis_client:
        await redis_client.close()
        logger.info("✅ Redis client closed")

# Create FastAPI app
app = FastAPI(
    title="BetterBeingWEB API",
    description="Backend API for BetterBeingWEB e-commerce platform",
    version="1.0.0",
    lifespan=lifespan
)

# Add rate limiting middleware
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)
app.add_middleware(SlowAPIMiddleware)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=os.getenv("CORS_ORIGINS", "http://localhost:3000,http://localhost:3001").split(","),
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Security middleware
app.add_middleware(
    TrustedHostMiddleware,
    allowed_hosts=os.getenv("ALLOWED_HOSTS", "localhost,127.0.0.1").split(",")
)

# Compression middleware
app.add_middleware(GZipMiddleware, minimum_size=1000)

# Routers (mounted after middleware)
try:
    from routers import auth as legacy_auth  # optional legacy router with prefix inside
except Exception:
    legacy_auth = None

try:
    from products.products_router import products_router
except Exception:
    products_router = None

try:
    from cart.cart_router import cart_router
except Exception:
    cart_router = None

try:
    from promos.promo_router import promos_router
except Exception:
    promos_router = None

if legacy_auth is not None:
    try:
        app.include_router(legacy_auth.router)  # has its own /api/auth prefix
    except Exception:
        pass

if products_router is not None:
    try:
        app.include_router(products_router, prefix="/api/products", tags=["products"])
    except Exception:
        pass

if cart_router is not None:
    try:
        app.include_router(cart_router, prefix="/api/cart", tags=["cart"])
    except Exception:
        pass

if promos_router is not None:
    try:
        app.include_router(promos_router, tags=["promotions"])
    except Exception:
        pass

# Dependency for database connection
async def get_db():
    if not pool:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Database not available"
        )
    async with pool.acquire() as connection:
        yield connection

# Dependency for Redis
async def get_redis():
    if not redis_client:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Redis not available"
        )
    return redis_client

# Password utilities
def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password):
    return pwd_context.hash(password)

# JWT utilities
def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def create_refresh_token(data: dict):
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS)
    to_encode.update({"exp": expire, "type": "refresh"})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db=Depends(get_db)
):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    try:
        payload = jwt.decode(credentials.credentials, SECRET_KEY, algorithms=[ALGORITHM])
        user_id: str = payload.get("sub")
        if user_id is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception
    
    # Fetch user from database
    user = await db.fetchrow(
        "SELECT id, email, first_name, last_name, email_verified FROM users WHERE id = $1",
        int(user_id)
    )
    
    if user is None:
        raise credentials_exception
    
    return {
        "id": user["id"],
        "email": user["email"],
        "first_name": user["first_name"],
        "last_name": user["last_name"],
        "email_verified": user["email_verified"]
    }

# Health endpoints (do not hard-depend on DB/Redis)
@app.get("/api/health")
@app.get("/health")
async def health_check():
    db_healthy = False
    redis_healthy = False

    # Database check
    global pool, redis_client
    if pool:
        try:
            async with pool.acquire() as conn:
                await conn.execute("SELECT 1")
                db_healthy = True
        except Exception:
            db_healthy = False

    # Redis check
    if redis_client:
        try:
            await redis_client.ping()
            redis_healthy = True
        except Exception:
            redis_healthy = False

    return {
        "status": "healthy" if db_healthy and redis_healthy else "degraded",
        "services": {
            "database": "healthy" if db_healthy else "unhealthy",
            "redis": "healthy" if redis_healthy else "unhealthy",
        },
        "timestamp": datetime.utcnow().isoformat(),
    }

# Custom OpenAPI schema
def custom_openapi():
    if app.openapi_schema:
        return app.openapi_schema
    
    openapi_schema = get_openapi(
        title=app.title,
        version=app.version,
        description=app.description,
        routes=app.routes,
    )
    
    # Add security schemes
    openapi_schema["components"]["securitySchemes"] = {
        "BearerAuth": {
            "type": "http",
            "scheme": "bearer",
            "bearerFormat": "JWT"
        }
    }
    
    app.openapi_schema = openapi_schema
    return app.openapi_schema

app.openapi = custom_openapi

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        app,
        host=os.getenv("HOST", "0.0.0.0"),
        port=int(os.getenv("PORT", "8000")),
        reload=os.getenv("ENV", "development") == "development"
    )
