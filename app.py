from fastapi import FastAPI, Request, Form
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel
from datetime import datetime
from classify import classify_request
from retrieve import retrieve_chunks
from escalate import check_escalation
from respond import generate_response
from logs.logger_utils import log_interaction, get_logger
import os
import json

app = FastAPI()
logger = get_logger(__name__)

app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

@app.get("/", response_class=HTMLResponse)
def root(request: Request):
    logger.info("Serving chat UI")
    return templates.TemplateResponse("index.html", {"request": request})


class HelpdeskRequest(BaseModel):
    username: str
    contact: str
    request: str
    category: str


@app.post("/helpdesk")
async def handle_helpdesk(req: HelpdeskRequest):
    try:
        logger.info(f"Received helpdesk query from {req.username}")

        user_query = req.request
        username = req.username
        contact = req.contact
        category = req.category

        context_chunks = retrieve_chunks(user_query, category)
        escalate, reason = check_escalation(user_query, category)

        chat_path = f"logs/chat_sessions/{username}.json"
        os.makedirs(os.path.dirname(chat_path), exist_ok=True)

        history = []
        if os.path.exists(chat_path):
            with open(chat_path, "r", encoding="utf-8") as f:
                history = json.load(f)

        history.append({"user": user_query})
        full_context = "\n\n".join([item.get("user", item.get("bot", "")) for item in history])

        response_text = await generate_response(full_context, context_chunks, category, username)
        history.append({"bot": response_text})

        with open(chat_path, "w", encoding="utf-8") as f:
            json.dump(history, f, indent=2)

        log_interaction({
            "timestamp": datetime.now().isoformat(),
            "username": username,
            "contact": contact,
            "query": user_query,
            "category": category,
            "escalate": escalate,
            "escalation_reason": reason,
            "response": response_text
        })

        return {
            "category": category,
            "escalate": escalate,
            "response": response_text
        }

    except Exception as e:
        logger.error(f"Exception while handling helpdesk query: {e}", exc_info=True)
        return {"error": "Something went wrong. Please contact support."}


@app.post("/feedback")
async def submit_feedback(username: str = Form(...), feedback: str = Form(...)):
    try:
        logger.info(f"Feedback received from {username}")
        feedback_path = f"logs/feedback/{username}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
        os.makedirs(os.path.dirname(feedback_path), exist_ok=True)

        with open(feedback_path, "w", encoding="utf-8") as f:
            f.write(feedback.strip())

        return JSONResponse({"message": "Thank you for your feedback!"})
    except Exception as e:
        logger.error(f"Exception while saving feedback: {e}", exc_info=True)
        return JSONResponse({"message": "Failed to save feedback."}, status_code=500)
