
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from main import run_agent

app = FastAPI(title="AI Agent API")

# Allow frontend requests
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5500",
        "http://127.0.0.1:5500",
        "http://localhost:8000",
        "http://127.0.0.1:8000"
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class ChatRequest(BaseModel):
    message: str


class ChatResponse(BaseModel):
    response: str


@app.get("/")
def home():
    return {"message": "AI Agent API is running!"}


@app.post("/chat", response_model=ChatResponse)
def chat(request: ChatRequest):

    if not request.message.strip():
        return {"response": "Please enter a message."}

    try:
        answer = run_agent(request.message)

        return {"response": answer or "I couldn't generate a response."}

    except Exception as e:
        return {"response": f"Something went wrong: {str(e)}"}
