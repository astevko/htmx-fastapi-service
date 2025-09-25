from fastapi import FastAPI, Request, Form
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
import uvicorn

app = FastAPI(title="HTMX FastAPI Service", version="0.1.0")

# Mount static files
app.mount("/static", StaticFiles(directory="static"), name="static")

# Setup templates
templates = Jinja2Templates(directory="templates")

@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    """Home page with HTMX demo"""
    return templates.TemplateResponse("index.html", {"request": request})

@app.post("/api/message", response_class=HTMLResponse)
async def create_message(request: Request, message: str = Form(...)):
    """HTMX endpoint to create a message"""
    return templates.TemplateResponse("message_partial.html", {
        "request": request,
        "message": message,
        "timestamp": "Just now"
    })

@app.get("/api/messages", response_class=HTMLResponse)
async def get_messages(request: Request):
    """HTMX endpoint to get all messages"""
    messages = [
        {"text": "Welcome to HTMX + FastAPI!", "timestamp": "Just now"},
        {"text": "This is a demo message", "timestamp": "1 minute ago"},
    ]
    return templates.TemplateResponse("messages_list.html", {
        "request": request,
        "messages": messages
    })

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
