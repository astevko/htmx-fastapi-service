"""
HTMX-FastAPI Service

A modern web application built with FastAPI and HTMX, demonstrating
server-side rendering with dynamic interactions.

Author: Andrew Stevko
Company: Stevko Cyber Services
License: GNU General Public License v3.0 (GPL-3.0)

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program.  If not, see <https://www.gnu.org/licenses/>.

For more information about this project, visit:
https://github.com/astevko/htmx-fastapi-service
"""

import hashlib
import logging
import os
import secrets
from datetime import datetime, timedelta, timezone

import bcrypt
import pytz
import uvicorn
from fastapi import Cookie, Depends, FastAPI, Form, HTTPException, Request, status
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from fastapi.middleware.cors import CORSMiddleware
from jose import JWTError, jwt
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address

from database import init_database, test_connection
from messages import get_all_messages, store_message
from models import (
    LoginErrorResponse,
    LoginRequest,
    LoginSuccessResponse,
    Message,
    MessageRequest,
    MessageResponse,
    TokenData,
    User,
    UserResponse,
)

logging.basicConfig(level=logging.INFO)  # Changed from DEBUG for security
logger = logging.getLogger(__name__)

# Security logger for authentication events
security_logger = logging.getLogger("security")

# Rate limiting
limiter = Limiter(key_func=get_remote_address)

# JWT Configuration with refresh token
SECRET_KEY = os.getenv("SECRET_KEY")
JWT_REFRESH_SECRET = os.getenv("JWT_REFRESH_SECRET")

if not SECRET_KEY:
    raise ValueError("SECRET_KEY environment variable must be set in production")

# Generate refresh secret if not provided
if not JWT_REFRESH_SECRET:
    JWT_REFRESH_SECRET = secrets.token_urlsafe(32)
    logger.warning("JWT_REFRESH_SECRET not set, using generated key. Set this in production!")

ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30
REFRESH_TOKEN_EXPIRE_DAYS = 7


def hash_password(password: str) -> str:
    """Secure password hashing with bcrypt"""
    salt = bcrypt.gensalt()
    hashed = bcrypt.hashpw(password.encode("utf-8"), salt)
    return hashed.decode("utf-8")


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify password against bcrypt hash"""
    try:
        return bcrypt.checkpw(plain_password.encode("utf-8"), hashed_password.encode("utf-8"))
    except Exception:
        return False


# User credentials from environment variables
DEMO_USERNAME = os.getenv("DEMO_USERNAME", "user@example.com")
DEMO_PASSWORD = os.getenv("DEMO_PASSWORD", "12341234")

# Create demo user with hashed password (hash once during startup)
DEMO_USER = User(
    username=DEMO_USERNAME,
    password=hash_password(DEMO_PASSWORD),
    timezone=None,  # Will be set during login
)

app = FastAPI(title="HTMX FastAPI Service", version="0.1.0")

# Add security middleware
app.add_middleware(
    TrustedHostMiddleware, 
    allowed_hosts=["*"]  # Configure with specific domains in production
)

# Add CORS middleware with restrictive settings
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure with specific origins in production
    allow_credentials=True,
    allow_methods=["GET", "POST"],
    allow_headers=["*"],
)

# Add rate limiter to app
app.state.limiter = limiter
app.add_exception_handler(429, _rate_limit_exceeded_handler)

# Security headers middleware
@app.middleware("http")
async def add_security_headers(request: Request, call_next):
    """Add comprehensive security headers to all responses"""
    response = await call_next(request)
    
    # Content Security Policy
    csp = (
        "default-src 'self'; "
        "script-src 'self' 'unsafe-inline' https://unpkg.com https://cdn.jsdelivr.net; "
        "style-src 'self' 'unsafe-inline' https://cdn.jsdelivr.net; "
        "img-src 'self' data:; "
        "font-src 'self' https://cdn.jsdelivr.net; "
        "connect-src 'self'; "
        "frame-ancestors 'none'; "
        "base-uri 'self'; "
        "form-action 'self'"
    )
    
    # Security headers
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-Frame-Options"] = "DENY"
    response.headers["X-XSS-Protection"] = "1; mode=block"
    response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
    response.headers["Content-Security-Policy"] = csp
    response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains; preload"
    response.headers["Permissions-Policy"] = "geolocation=(), microphone=(), camera=()"
    
    return response

# Mount static files
app.mount("/static", StaticFiles(directory="static"), name="static")

# Setup templates
templates = Jinja2Templates(directory="templates")


@app.on_event("startup")
async def startup_event():
    """Initialize database and demo messages on startup"""
    try:
        # Test database connection
        if test_connection():
            logger.info("Database connection successful")
            # Initialize database tables
            init_database()
            logger.info("Database initialized successfully")
        else:
            logger.error("Database connection failed")
            raise Exception("Database connection failed")
    except Exception as e:
        logger.error(f"Failed to initialize database: {e}")
        raise

    # Add demo messages
    now = datetime.now(timezone.utc)

    # Check if we already have messages to avoid duplicates
    existing_messages = get_all_messages()
    if not existing_messages:
        # Add demo messages only if the database is empty
        store_message("This is a demo message", now - timedelta(minutes=1))
        store_message("Welcome to HTMX + FastAPI!", now - timedelta(minutes=5))
        store_message("Try adding your own message!", now - timedelta(hours=1))
        logger.info("Demo messages added")


# JWT Helper Functions
def create_access_token(data: TokenData, expires_delta: timedelta = None):
    """Create a JWT access token"""
    to_encode = data.model_dump()
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire, "type": "access"})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


def create_refresh_token(data: TokenData, expires_delta: timedelta = None):
    """Create a JWT refresh token"""
    to_encode = data.model_dump()
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS)
    to_encode.update({"exp": expire, "type": "refresh"})
    encoded_jwt = jwt.encode(to_encode, JWT_REFRESH_SECRET, algorithm=ALGORITHM)
    return encoded_jwt


def verify_token(token: str, token_type: str = "access") -> TokenData | None:
    """Verify JWT token and return TokenData"""
    try:
        secret = SECRET_KEY if token_type == "access" else JWT_REFRESH_SECRET
        payload = jwt.decode(token, secret, algorithms=[ALGORITHM])
        
        # Verify token type
        if payload.get("type") != token_type:
            return None
            
        token_data = TokenData(**payload)
        return token_data
    except JWTError:
        return None


def authenticate_user(username: str, password: str) -> User | None:
    """Authenticate user credentials"""
    if username == DEMO_USER.username and verify_password(password, DEMO_USER.password):
        return DEMO_USER
    return None


def get_current_user(jwt_token: str = Cookie(None), user_timezone: str = Cookie(None)) -> UserResponse:
    """Get current user from JWT token and verify timezone"""
    if not jwt_token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # Verify access token
    token_data = verify_token(jwt_token, "access")
    if not token_data or token_data.sub is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # Verify timezone matches
    if token_data.timezone != user_timezone:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Timezone mismatch",
            headers={"WWW-Authenticate": "Bearer"},
        )

    return UserResponse(username=token_data.sub, timezone=token_data.timezone)


def format_timestamp(dt: datetime, timezone_str: str = "UTC") -> str:
    """Format timestamp to the current time in the given timezone"""
    try:
        # Get the timezone
        tz = pytz.timezone(timezone_str)

        # Convert to the specified timezone
        localized_dt = dt.replace(tzinfo=timezone.utc).astimezone(tz)
        # now = datetime.now(tz)

        return localized_dt.strftime("%Y-%m-%d %H:%M:%S %Z")

    except Exception:
        # Fallback to simple format if timezone is invalid
        return dt.strftime("%Y-%m-%d %H:%M")


@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    """Login page"""
    return templates.TemplateResponse("index.html", {"request": request})


@app.get("/msgs", response_class=HTMLResponse)
async def messages_page(request: Request, current_user: UserResponse = Depends(get_current_user)):
    """Messages page - requires authentication"""
    return templates.TemplateResponse("msgs.html", {"request": request})


@app.post("/api/login", response_class=HTMLResponse)
@limiter.limit("5/minute")  # Rate limit login attempts
async def login(
    request: Request,
    username: str = Form(...),
    password: str = Form(...),
    user_timezone: str = Form(...),
):
    """Login endpoint that creates JWT and timezone cookies"""
    # Create LoginRequest from form data for validation
    login_data = LoginRequest(username=username, password=password, user_timezone=user_timezone)

    user = authenticate_user(login_data.username, login_data.password)
    if not user:
        # Log failed login attempt
        security_logger.warning(f"Failed login attempt for username: {login_data.username}")
        return templates.TemplateResponse(
            "login_error.html",
            {"request": request, "error": "Invalid username or password"},
        )

    # Log successful login
    security_logger.info(f"Successful login for user: {login_data.username}")

    # Create JWT tokens with timezone
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    refresh_token_expires = timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS)
    token_data = TokenData(sub=user.username, timezone=login_data.user_timezone)
    
    access_token = create_access_token(token_data, expires_delta=access_token_expires)
    refresh_token = create_refresh_token(token_data, expires_delta=refresh_token_expires)

    # Create response with HTMX redirect header
    response = HTMLResponse(content="<div>Login successful! Redirecting...</div>")
    response.headers["HX-Redirect"] = "/msgs"

    # Set JWT cookies (session-based) - SECURE SETTINGS
    response.set_cookie(
        key="jwt_token",
        value=access_token,
        httponly=True,
        secure=True,  # Always True for production
        samesite="strict",  # Stricter than "lax"
        max_age=1800,  # 30 minutes
    )

    # Set refresh token cookie (longer expiration)
    response.set_cookie(
        key="refresh_token",
        value=refresh_token,
        httponly=True,
        secure=True,
        samesite="strict",
        max_age=604800,  # 7 days
    )

    # Set timezone cookie (persistent for 1 year) - SECURE SETTINGS
    response.set_cookie(
        key="user_timezone",
        value=login_data.user_timezone,
        max_age=365 * 24 * 60 * 60,  # 1 year
        httponly=True,  # Secure - no JavaScript access
        secure=True,  # Always True for production
        samesite="strict",  # Stricter than "lax"
    )

    return response


# CREATE MESSAGE POST ENDPOINT
@app.post("/api/message", response_class=HTMLResponse)
async def create_message(
    request: Request,
    message: str = Form(...),
    current_user: UserResponse = Depends(get_current_user),
):
    """HTMX endpoint to create a message - requires authentication"""
    # Create MessageRequest from form data for validation
    message_data = MessageRequest(message=message)

    logger.debug(f"Posting message with timezone: {current_user.timezone} and message: {message_data.message}")
    now = datetime.now(timezone.utc)
    formatted_time = format_timestamp(now, current_user.timezone)

    # Store message in database
    store_message(message_data.message, now)

    return templates.TemplateResponse(
        "message_partial.html",
        {
            "request": request,
            "message": message_data.message,
            "timestamp": formatted_time,
        },
    )


# GET ALL MESSAGES GET ENDPOINT
@app.get("/api/messages", response_class=HTMLResponse)
async def get_messages(request: Request, current_user: UserResponse = Depends(get_current_user)):
    """HTMX endpoint to get all messages - requires authentication"""
    logger.debug(f"Getting messages with timezone: {current_user.timezone}")
    # TODO add pagination

    # Get messages from database as Message objects (already in newest first order)
    db_messages = get_all_messages(descending=True)

    # Convert messages to user's timezone
    messages = []
    for message in db_messages:
        formatted_time = format_timestamp(message.timestamp, current_user.timezone)
        messages.append(MessageResponse(text=message.text, timestamp=formatted_time))
    return templates.TemplateResponse("messages_list.html", {"request": request, "messages": messages})


@app.post("/api/refresh", response_class=HTMLResponse)
async def refresh_token(refresh_token: str = Cookie(None)):
    """Refresh access token using refresh token"""
    if not refresh_token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="No refresh token provided"
        )
    
    # Verify refresh token
    token_data = verify_token(refresh_token, "refresh")
    if not token_data or token_data.sub is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid refresh token"
        )
    
    # Create new access token
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    new_access_token = create_access_token(token_data, expires_delta=access_token_expires)
    
    response = HTMLResponse(content="<div>Token refreshed</div>")
    response.set_cookie(
        key="jwt_token",
        value=new_access_token,
        httponly=True,
        secure=True,
        samesite="strict",
        max_age=1800,  # 30 minutes
    )
    
    return response


@app.get("/api/logout", response_class=HTMLResponse)
async def logout():
    """Logout endpoint that clears cookies and redirects"""
    response = RedirectResponse(url="/", status_code=status.HTTP_302_FOUND)
    response.delete_cookie("jwt_token")
    response.delete_cookie("refresh_token")
    response.delete_cookie("user_timezone")
    return response


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
