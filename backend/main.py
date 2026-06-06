import logging
import shutil
import os

from time import time

from fastapi import (
    FastAPI,
    WebSocket,
    UploadFile,
    File,
    WebSocketDisconnect
)

from fastapi.middleware.cors import (
    CORSMiddleware
)

from pydantic import BaseModel

from langsmith import traceable

from backend.agents.graph import graph

from backend.memory.redis_memory import (
    get_history,
    save_turn
)

from backend.memory.pg_memory import (
    get_user_facts
)

from backend.tools.rag import (
    ingest_document
)


app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

logging.basicConfig(
    level=logging.INFO
)


# =====================================================
# REQUEST MODELS
# =====================================================

class ChatRequest(BaseModel):
    question: str
    session_id: str = "test"
    user_id: str = "user"


# =====================================================
# HEALTH
# =====================================================

@app.get("/health")
def health():

    return {
        "status": "ok"
    }


# =====================================================
# AGENT
# =====================================================

@traceable(name="chat_session")
async def run_agent(
    question,
    session_id,
    user_id
):

    history = get_history(
        session_id
    )

    history_text = "\n".join(
        [
            f"User: {h['q']}\nAI: {h['a']}"
            for h in history
        ]
    )

    facts = await get_user_facts(
        user_id
    )

    state = {
        "question": question,

        "session_id": session_id,
        "user_id": user_id,
        "company_id": "default",

        "history": history_text,
        "facts": facts,

        "route": None,
        "plan": [],

        "sql_result": None,
        "rag_result": None,
        "memory_result": None,

        "generated_sql": None,

        "answer": None,

        "confidence": None,

        "requires_human": False,

        "error": None,

        "start_time": time()
    }

    result = await graph.ainvoke(
        state
    )

    return result


# =====================================================
# CHAT API
# =====================================================

@app.post("/chat")
async def chat(
    req: ChatRequest
):

    result = await run_agent(
        req.question,
        req.session_id,
        req.user_id
    )

    save_turn(
        req.session_id,
        {
            "q": req.question,
            "a": result.get(
                "answer",
                ""
            )
        }
    )

    return {
        "answer": result.get(
            "answer"
        ),

        "route": result.get(
            "route"
        ),

        "confidence": result.get(
            "confidence"
        )
    }


# =====================================================
# DEBUG AGENT
# =====================================================

@app.post("/debug")
async def debug_agent(
    req: ChatRequest
):

    result = await run_agent(
        req.question,
        req.session_id,
        req.user_id
    )

    return result


# =====================================================
# MEMORY
# =====================================================

@app.get("/memory/{session_id}")
async def memory(
    session_id: str
):

    return {
        "history": get_history(
            session_id
        )
    }


# =====================================================
# WEBSOCKET CHAT
# =====================================================

@app.websocket("/ws")
async def websocket_endpoint(
    ws: WebSocket
):

    await ws.accept()

    try:

        while True:

            data = await ws.receive_json()

            question = data.get(
                "question",
                ""
            )

            session_id = data.get(
                "session_id",
                "default"
            )

            user_id = data.get(
                "user_id",
                "anon"
            )

            result = await run_agent(
                question,
                session_id,
                user_id
            )

            answer = result.get(
                "answer",
                "No answer generated."
            )

            await ws.send_json(
                {
                    "answer": answer,
                    "route": result.get(
                        "route"
                    ),
                    "confidence": result.get(
                        "confidence"
                    )
                }
            )

            save_turn(
                session_id,
                {
                    "q": question,
                    "a": answer
                }
            )

    except WebSocketDisconnect:

        print(
            "Client disconnected"
        )

    except Exception as e:

        print(
            "WebSocket error:",
            e
        )


# =====================================================
# DOCUMENT UPLOAD
# =====================================================

@app.post("/upload")
async def upload_document(
    file: UploadFile = File(...),
    company_id: str = "default"
):

    upload_dir = "uploads"

    os.makedirs(
        upload_dir,
        exist_ok=True
    )

    path = os.path.join(
        upload_dir,
        file.filename
    )

    with open(
        path,
        "wb"
    ) as buffer:

        shutil.copyfileobj(
            file.file,
            buffer
        )

    result = ingest_document(
        path,
        company_id
    )

    return {
        "status": "success",
        "file": file.filename,
        "result": result
    }

@app.post("/chat")
async def chat(
    req: ChatRequest
):

    result = await run_agent(
        req.question,
        req.session_id,
        req.user_id
    )

    answer = result.get(
        "answer",
        "No answer generated."
    )

    save_turn(
        req.session_id,
        {
            "q": req.question,
            "a": answer
        }
    )

    return {
        "answer": answer,
        "route": result.get("route"),
        "confidence": result.get("confidence")
    }

@app.post("/debug")
async def debug(
    req: ChatRequest
):

    result = await run_agent(
        req.question,
        req.session_id,
        req.user_id
    )

    return result