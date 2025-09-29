import hashlib
import logging
import os
import secrets
from datetime import datetime, timedelta, timezone

import pytz
import uvicorn
from fastapi import Cookie, Depends, FastAPI, Form, HTTPException, Request, status
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from jose import JWTError, jwt

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

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

# JWT Configuration
SECRET_KEY = os.getenv("SECRET_KEY", secrets.token_urlsafe(32))
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30


# TODO improve Simple password hashing for demo (use proper hashing in production)
def hash_password(password: str) -> str:
    """Simple password hashing for demo purposes"""
    return hashlib.sha256(password.encode()).hexdigest()


# Demo user credentials (in production, use a proper database)
DEMO_USER = User(
    username="user@example.com",
    password=hash_password("12341234"),
    timezone=None,  # Will be set during login
)

app = FastAPI(title="HTMX FastAPI Service", version="0.1.0")

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
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


def verify_password(plain_password, hashed_password):
    """Verify a password against its hash"""
    return hash_password(plain_password) == hashed_password


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

    try:
        payload = jwt.decode(jwt_token, SECRET_KEY, algorithms=[ALGORITHM])
        token_data = TokenData(**payload)

        if token_data.sub is None:
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

    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token",
            headers={"WWW-Authenticate": "Bearer"},
        )


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
        return templates.TemplateResponse(
            "login_error.html",
            {"request": request, "error": "Invalid username or password"},
        )

    # Create JWT token with timezone
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    token_data = TokenData(sub=user.username, timezone=login_data.user_timezone)
    access_token = create_access_token(token_data, expires_delta=access_token_expires)

    # Create response with HTMX redirect header
    response = HTMLResponse(content="<div>Login successful! Redirecting...</div>")
    response.headers["HX-Redirect"] = "/msgs"

    # Set JWT cookie (session-based)
    response.set_cookie(
        key="jwt_token",
        value=access_token,
        httponly=True,
        secure=False,  # Set to True in production with HTTPS
        samesite="lax",
    )

    # Set timezone cookie (persistent for 1 year)
    response.set_cookie(
        key="user_timezone",
        value=login_data.user_timezone,
        max_age=365 * 24 * 60 * 60,  # 1 year
        httponly=False,  # Allow JavaScript access for HTMX
        secure=False,  # Set to True in production with HTTPS
        samesite="lax",
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


@app.get("/api/logout", response_class=HTMLResponse)
async def logout():
    """Logout endpoint that clears cookies and redirects"""
    response = RedirectResponse(url="/", status_code=status.HTTP_302_FOUND)
    response.delete_cookie("jwt_token")
    response.delete_cookie("user_timezone")
    return response


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
