
import os
import asyncio

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from openai import AsyncOpenAI  # type: ignore[import-not-found]
from dotenv import load_dotenv

load_dotenv()

app = FastAPI(title="Tomato Chat API")

# Groq client (OpenAI-compatible)
client = AsyncOpenAI(
    api_key=os.getenv("GROQ_API_KEY"),
    base_url="https://api.groq.com/openai/v1"
)

MODEL = os.getenv("GROQ_MODEL", "openai/gpt-oss-20b")

SYSTEM_PROMPT = """
You are a customer-support executive for Tomato,
a food ordering application.

Your responsibilities:
- Answer food ordering questions.
- Help with refunds.
- Help track orders when tracking information is provided.
- Explain company policies.

Use professional and empathetic language.

Do not answer questions unrelated to Tomato's
food ordering services.
"""

# Request schema
class ChatRequest(BaseModel):
    session_id: str
    message: str


# Temporary conversation storage
conversations: dict[str, list[dict]] = {}

# Prevent concurrent requests within the same session
session_locks: dict[str, asyncio.Lock] = {}


@app.post("/api/chat")
async def chat(request: ChatRequest):

    session_id = request.session_id

    if session_id not in session_locks:
        session_locks[session_id] = asyncio.Lock()

    async with session_locks[session_id]:

        if session_id not in conversations:
            conversations[session_id] = []

        history = conversations[session_id]

        messages = [
            {"role": "system", "content": SYSTEM_PROMPT},
            *history,
            {"role": "user", "content": request.message}
        ]

        try:
            response = await client.chat.completions.create(
                model=MODEL,
                messages=messages,
                temperature=0.7
            )

            answer = response.choices[0].message.content

            if not answer:
                raise HTTPException(
                    status_code=502,
                    detail="The AI returned an empty response."
                )

            # Save conversation
            history.append({
                "role": "user",
                "content": request.message
            })

            history.append({
                "role": "assistant",
                "content": answer
            })

            return {
                "session_id": session_id,
                "reply": answer
            }

        except HTTPException:
            raise

        except Exception as e:
            raise HTTPException(
                status_code=502,
                detail="AI service temporarily unavailable."
            )


@app.delete("/api/chat/{session_id}")
async def clear_chat(session_id: str):

    conversations.pop(session_id, None)

    return {"message": "Conversation cleared"}
