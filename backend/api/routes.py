from fastapi import APIRouter, UploadFile
from backend.agents.graph import app_graph
from backend.memory.redis_memory import save_turn, get_history
from backend.tools.rag import ingest_pdf
import uuid

router = APIRouter()

@router.post("/chat")
async def chat(q: str, session_id: str = None):
    if not session_id:
        session_id = str(uuid.uuid4())

    history = get_history(session_id)

    result = app_graph.invoke({"question": q})

    save_turn(session_id, {"q": q, "a": result["result"]})

    return {"answer": result["result"], "session_id": session_id}


@router.post("/upload")
async def upload(file: UploadFile):
    path = f"/tmp/{file.filename}"
    with open(path, "wb") as f:
        f.write(await file.read())

    ingest_pdf(path)
    return {"status": "uploaded"}