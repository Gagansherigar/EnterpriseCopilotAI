import logging
import asyncio
from fastapi import FastAPI, WebSocket
from backend.agents.graph import graph
from backend.memory.redis_memory import get_history, save_turn
from backend.memory.pg_memory import get_user_facts
from langsmith import traceable
from fastapi import UploadFile, File
import shutil
from backend.tools.rag import ingest_pdf
from fastapi.middleware.cors import CORSMiddleware
from fastapi import WebSocket, WebSocketDisconnect

app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
logging.basicConfig(level=logging.INFO)


@app.get("/health")
def health():
    return {"status": "ok"}


@traceable(name="chat_session")
async def run_agent(question, session_id, user_id):
    history = get_history(session_id)

    history_text = "\n".join(
        [f"User: {h['q']}\nAI: {h['a']}" for h in history]
    )

    facts = await get_user_facts(user_id)   # ✅ FIX HERE

    state = {
        "question": question,
        "history": history_text,
        "facts": facts
    }

    result = await graph.ainvoke(state)
    return result["answer"]


@app.websocket("/ws")
async def websocket_endpoint(ws: WebSocket):
    await ws.accept()

    try:
        while True:
            data = await ws.receive_json()

            q = data.get("question", "")
            session_id = data.get("session_id", "default")
            user_id = data.get("user_id", "anon")

            answer = await run_agent(q, session_id, user_id)
            await ws.send_json({"answer": answer})

            save_turn(session_id, {"q": q, "a": answer})

    except WebSocketDisconnect:
        print("Client disconnected")

    except Exception as e:
        print("WebSocket error:", e)

@app.post("/upload")
async def upload_pdf(file: UploadFile = File(...), company_id: str = "default"):
    path = f"/tmp/{file.filename}"

    with open(path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    result = ingest_pdf(path, company_id)

    return result