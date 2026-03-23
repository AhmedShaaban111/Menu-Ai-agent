from dotenv import load_dotenv
load_dotenv()
 
from contextlib import asynccontextmanager
from fastapi import FastAPI, HTTPException, UploadFile, File, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse, StreamingResponse
from pydantic import BaseModel
from loguru import logger
import httpx
import websockets
import json
import os
 
agent = None
 
@asynccontextmanager
async def lifespan(app: FastAPI):
    global agent
    from src.database.chroma_db import get_menu_db
    from src.agent.menu_agent import create_menu_agent
 
    logger.info("🍽️  Loading menu into vector database...")
    db = get_menu_db()
    if db.count() == 0:
        count = db.ingest()
        logger.info(f"✅ Ingested {count} menu items")
    else:
        logger.info(f"✅ Menu already loaded ({db.count()} items)")
 
    logger.info("🤖 Creating menu agent...")
    agent = create_menu_agent()
    logger.info("✅ Agent ready!")
    yield
 
app = FastAPI(title="🍽️ Menu AI Agent", lifespan=lifespan)
 
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)
 
class ChatRequest(BaseModel):
    message: str
    session_id: str = "default"
 
class ChatResponse(BaseModel):
    response: str
    session_id: str
 
# ── HTML UI ───────────────────────────────────────────────
@app.get("/", response_class=HTMLResponse)
def root():
    with open("chat_ui.html", "r") as f:
        return f.read()
 
# ── STT Batch: Deepgram Nova-3 ────────────────────────────
@app.post("/transcribe")
async def transcribe(audio: UploadFile = File(...)):
    """حوّل ملف صوتي لنص — بيتستخدم كـ fallback."""
    try:
        audio_bytes = await audio.read()
        async with httpx.AsyncClient() as client:
            res = await client.post(
                "https://api.deepgram.com/v1/listen",
                params={"model": "nova-3", "language": "en", "punctuate": "true", "smart_format": "true"},
                headers={
                    "Authorization": f"Token {os.getenv('DEEPGRAM_API_KEY')}",
                    "Content-Type": audio.content_type or "audio/webm",
                },
                content=audio_bytes,
                timeout=30,
            )
            data = res.json()
        transcript = (
            data.get("results", {})
                .get("channels", [{}])[0]
                .get("alternatives", [{}])[0]
                .get("transcript", "")
        )
        return {"text": transcript}
    except Exception as e:
        logger.error(f"STT error: {e}")
        raise HTTPException(status_code=500, detail=str(e))
 
# ── STT Streaming: WebSocket proxy to Deepgram ────────────
@app.websocket("/ws/transcribe")
async def ws_transcribe(ws: WebSocket):
    """
    WebSocket بيستقبل audio chunks من المتصفح
    ويبعتهم لـ Deepgram streaming
    ويرجع interim + final transcripts في real-time
    """
    await ws.accept()
    dg_key = os.getenv("DEEPGRAM_API_KEY")
 
    dg_url = (
        "wss://api.deepgram.com/v1/listen"
        "?model=nova-3"
        "&language=en"
        "&punctuate=true"
        "&smart_format=true"
        "&interim_results=true"
        "&endpointing=100"
    )
 
    try:
        async with websockets.connect(
            dg_url,
            additional_headers={"Authorization": f"Token {dg_key}"}
        ) as dg_ws:
 
            async def recv_from_dg():
                """استقبل من Deepgram وابعت للمتصفح."""
                try:
                    async for msg in dg_ws:
                        data = json.loads(msg)
                        transcript = (
                            data.get("channel", {})
                                .get("alternatives", [{}])[0]
                                .get("transcript", "")
                        )
                        is_final = data.get("is_final", False)
 
                        if transcript:
                            await ws.send_json({
                                "transcript": transcript,
                                "is_final": is_final,
                            })
                except Exception:
                    pass
 
            import asyncio
            recv_task = asyncio.create_task(recv_from_dg())
 
            # استقبل audio من المتصفح وابعت لـ Deepgram
            try:
                while True:
                    chunk = await ws.receive_bytes()
                    await dg_ws.send(chunk)
            except WebSocketDisconnect:
                pass
            finally:
                recv_task.cancel()
                # أبلغ Deepgram إن الـ stream خلص
                try:
                    await dg_ws.send(json.dumps({"type": "CloseStream"}))
                except Exception:
                    pass
 
    except Exception as e:
        logger.error(f"WS STT error: {e}")
        try:
            await ws.send_json({"error": str(e)})
        except Exception:
            pass
 
# ── TTS: Deepgram Aura Nova ───────────────────────────────
@app.post("/speak")
async def speak(req: ChatRequest):
    """حوّل النص لصوت باستخدام Deepgram TTS."""
    try:
        async with httpx.AsyncClient() as client:
            res = await client.post(
                "https://api.deepgram.com/v1/speak",
                params={"model": "aura-2-thalia-en", "encoding": "linear16", "sample_rate": "24000"},
                headers={
                    "Authorization": f"Token {os.getenv('DEEPGRAM_API_KEY')}",
                    "Content-Type": "application/json",
                },
                json={"text": req.message},
                timeout=30,
            )
        logger.info(f"TTS response: status={res.status_code}, content-type={res.headers.get('content-type')}, size={len(res.content)}")
        return StreamingResponse(iter([res.content]), media_type="audio/wav")
    except Exception as e:
        logger.error(f"TTS error: {e}")
        raise HTTPException(status_code=500, detail=str(e))
 
# ── Chat ──────────────────────────────────────────────────
@app.post("/chat", response_model=ChatResponse)
def chat(req: ChatRequest):
    if agent is None:
        raise HTTPException(status_code=503, detail="Agent not ready")
    try:
        from src.agent.menu_agent import chat_with_agent
        response = chat_with_agent(agent, req.message, req.session_id)
        return ChatResponse(response=response, session_id=req.session_id)
    except Exception as e:
        logger.error(f"Chat error: {e}")
        raise HTTPException(status_code=500, detail=str(e))
 
@app.get("/menu")
def get_full_menu():
    from src.data.menu_data import MENU_ITEMS
    return {"items": [item.model_dump() for item in MENU_ITEMS]}
 