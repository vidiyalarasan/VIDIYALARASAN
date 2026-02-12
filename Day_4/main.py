import os
from fastapi import FastAPI, Form, HTTPException
from langchain_groq import ChatGroq
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from dotenv import load_dotenv
from langserve import add_routes

app=FastAPI()
llm=ChatGroq(
    model="llama-3.1-8b-instant",
    groq_api_key=os.getenv("GROQ_API_KEY")
)
add_routes(app,llm,path="/chat")
@app.get("/")
def home():
    return {"message": "FastAPI is running 🚀"}
