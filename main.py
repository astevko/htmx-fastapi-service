from fastapi import FastAPI, Request, Form, Query
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from datetime import datetime, timedelta, timezone
import pytz
import uvicorn
import logging

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

app = FastAPI(title="HTMX FastAPI Service", version="0.1.0")

# Mount static files
app.mount("/static", StaticFiles(directory="static"), name="static")

# Setup templates
templates = Jinja2Templates(directory="templates")

def format_timestamp(dt: datetime, timezone_str: str = "UTC") -> str:
    """Format timestamp to the current time in the given timezone"""
    try:
        # Get the timezone
        tz = pytz.timezone(timezone_str)
        
        # Convert to the specified timezone
        localized_dt = dt.replace(tzinfo=timezone.utc).astimezone(tz)
        now = datetime.now(tz)

        return localized_dt.strftime("%Y-%m-%d %H:%M:%S %Z")

    except Exception:
        # Fallback to simple format if timezone is invalid
        return dt.strftime("%Y-%m-%d %H:%M")

@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    """Home page with HTMX demo"""
    return templates.TemplateResponse("index.html", {"request": request})

@app.post("/api/message", response_class=HTMLResponse)
async def create_message(request: Request, message: str = Form(...), user_timezone: str = Form("UTC")):
    logger.debug(f"Posting message with timezone: {user_timezone} and message: {message}")
    """HTMX endpoint to create a message"""
    now = datetime.now(timezone.utc)
    formatted_time = format_timestamp(now, user_timezone)
    
    return templates.TemplateResponse("message_partial.html", {
        "request": request,
        "message": message,
        "timestamp": formatted_time
    })

@app.get("/api/messages", response_class=HTMLResponse)
async def get_messages(request: Request, user_timezone: str = Query("UTC")):
    logger.debug(f"Getting messages with timezone: {user_timezone}")
    """HTMX endpoint to get all messages"""
    # Sample messages with actual timestamps
    now = datetime.now(timezone.utc)
    messages = [
        {
            "text": "This is a demo message", 
            "timestamp": format_timestamp(now - timedelta(minutes=1), user_timezone)
        },
        {
            "text": "Welcome to HTMX + FastAPI!", 
            "timestamp": format_timestamp(now - timedelta(minutes=5), user_timezone)
        },
        {
            "text": "Try adding your own message!", 
            "timestamp": format_timestamp(now - timedelta(hours=1), user_timezone)
        },
    ]
    return templates.TemplateResponse("messages_list.html", {
        "request": request,
        "messages": messages
    })

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
