from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from core import chat

app = FastAPI()

# Allow frontend to connect
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class ChatRequest(BaseModel):
    message: str


@app.post("/chat")
async def chat_endpoint(req: ChatRequest):
    history = []  # optional: make this stateful later
    history = chat(req.message, history)
    response = {"response": history[-1]["content"]}
    print(response)
    return response
