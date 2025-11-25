from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from .agents import build_agent
from .db import init_db
import os

app = FastAPI(title="Context-Engineered Agent API")
agent = build_agent()

class UserMessage(BaseModel):
    user_id: str
    message: str


@app.on_event("startup")
async def startup_event():
    # Ensure DB is initialized (only creates and seeds sample data)
    init_db()


@app.post("/chat")
async def chat(msg: UserMessage):
    try:
        response, state = agent.create_runtime(state={"user_id": msg.user_id, "messages": []}).run(msg.message), {}
        return {"response": response}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))