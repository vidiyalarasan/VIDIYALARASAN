from fastapi import FastAPI
from pydantic import BaseModel
from langchain_groq import ChatGroq
from dotenv import load_dotenv
import os
from fastapi.middleware.cors import CORSMiddleware

load_dotenv()

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

llm = ChatGroq(
    model="llama-3.1-8b-instant",
    groq_api_key=os.getenv("GROQ_API_KEY")
)


class Message(BaseModel):
    role: str
    content: str


class ChatRequest(BaseModel):
    messages: list[Message]


@app.post("/ask")
async def ask(request: ChatRequest):
    formatted_messages = [
        (msg.role, msg.content) for msg in request.messages
    ]

    response = llm.invoke(formatted_messages)

    return {"answer": response.content}
