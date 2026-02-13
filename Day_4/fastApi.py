import os
from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from langchain_groq import ChatGroq
from dotenv import load_dotenv

load_dotenv()

app = FastAPI()

templates = Jinja2Templates(directory="templates")
app.mount("/static", StaticFiles(directory="static"), name="static")

llm = ChatGroq(
    model="llama-3.1-8b-instant",
    groq_api_key=os.getenv("GROQ_API_KEY")
)

# ------------------------
# Landing Page
# ------------------------
@app.get("/", response_class=HTMLResponse)
def landing(request: Request):
    return templates.TemplateResponse("landing.html", {"request": request})


# ------------------------
# Chat Page
# ------------------------
@app.get("/chat", response_class=HTMLResponse)
def chat_page(request: Request):
    return templates.TemplateResponse("chat.html", {"request": request})


# ------------------------
# API Endpoint
# ------------------------
class QuestionRequest(BaseModel):
    question: str

@app.post("/ask")
def ask(request: QuestionRequest):
    try:
        response = llm.invoke(request.question)
        return {"answer": response.content}
    except Exception as e:
        return {"answer": f"Error: {str(e)}"}
