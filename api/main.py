from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from typing import List
import json
import os
from dotenv import load_dotenv
from mangum import Mangum  # ✅ Required for Vercel

from langchain_openai import ChatOpenAI
from langchain.prompts import ChatPromptTemplate
from langchain.schema import AIMessage, HumanMessage

load_dotenv()

cv_data = {}

app = FastAPI()

# ✅ CORS setup (important for frontend integration)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

llm = ChatOpenAI(model="gpt-4o-mini", streaming=True)

class ChatRequest(BaseModel):
    messages: List[str]

@app.get("/")
def root():
    return {"status": "ok"}


@app.post("/chat")
async def chat_endpoint(request: ChatRequest):
    system_prompt = """
    You are an expert software architect and design assistant. Your task is to analyze high-level user requirements and automatically design appropriate software solutions.

    Using advanced software engineering principles, you should:

    - Interpret the given user requirements clearly.
    - Identify the suitable software architecture style (e.g., microservices, layered, event-driven, serverless, etc.) and justify your choice.
    - Propose a solution architecture diagram or structured textual design including components, data flow, APIs, and databases.
    - Recommend appropriate technologies, frameworks, and design patterns for each component.
    - Explain the reasoning behind each design decision, including scalability, maintainability, performance, and security aspects.
    - Optionally, generate starter code snippets or configuration examples (in Python, Java, or TypeScript).
    """

    conversation = [AIMessage(content=system_prompt)]
    for msg in request.messages:
        conversation.append(HumanMessage(content=msg))

    def generate():
        for chunk in llm.stream(conversation):
            if chunk.content:
                yield chunk.content

    return StreamingResponse(generate(), media_type="text/plain")

# ✅ Add this line for Vercel
handler = Mangum(app)
