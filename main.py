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
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])

class ChatRequest(BaseModel):
    message: str
    session_id: str = "default"

class ChatResponse(BaseModel):
    response: str
    session_id: str

@app.get("/", response_class=HTMLResponse)
def root():
    with open("chat_ui.html", "r") as f:
        return f.read()

# ── STT: ElevenLabs Scribe (Arabic) ──────────────────────
@app.post("/transcribe")
async def transcribe(audio: UploadFile = File(...)):
    try:
        audio_bytes = await audio.read()
        logger.info(f"🎤 Received audio: {len(audio_bytes)} bytes")
        async with httpx.AsyncClient() as client:
            res = await client.post(
                "https://api.elevenlabs.io/v1/speech-to-text",
                headers={"xi-api-key": os.getenv("ELEVENLABS_API_KEY")},
                data={"model_id": "scribe_v1", "language_code": "ar"},
                files={"file": ("audio.webm", audio_bytes, "audio/webm")},
                timeout=30,
            )
            res.raise_for_status()
            data = res.json()
        transcript = data.get("text", "")
        logger.info(f"📝 Transcript: {transcript}")
        return {"text": transcript}
    except Exception as e:
        logger.error(f"Transcription error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# ── STT Streaming: WebSocket → Deepgram ──────────────────
@app.websocket("/ws/transcribe")
async def ws_transcribe(ws: WebSocket):
    await ws.accept()
    dg_key = os.getenv("DEEPGRAM_API_KEY")
    dg_url = (
        "wss://api.deepgram.com/v1/listen"
        "?model=nova-3"
        "&language=ar"
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
                            await ws.send_json({"transcript": transcript, "is_final": is_final})
                except Exception:
                    pass

            import asyncio
            recv_task = asyncio.create_task(recv_from_dg())
            try:
                while True:
                    chunk = await ws.receive_bytes()
                    await dg_ws.send(chunk)
            except WebSocketDisconnect:
                pass
            finally:
                recv_task.cancel()
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

# ── TTS: ElevenLabs (Arabic) ────────────────
@app.post("/speak")
async def speak(req: ChatRequest):
    try:
        api_key = os.getenv("ELEVENLABS_API_KEY")
        # صوت multilingual يدعم العربية - غيّره من .env إذا أردت
        voice_id = os.getenv("ELEVENLABS_VOICE_ID", "pNInz6obpgDQGcFmaJgB")
        import re
        clean = req.message
        clean = re.sub(r'\*+', '', clean)
        clean = re.sub(r'#+\s*', '', clean)
        clean = re.sub(r'^[-•–]\s*', '', clean, flags=re.MULTILINE)
        clean = re.sub(r'^\d+\.\s*', '', clean, flags=re.MULTILINE)
        clean = re.sub(r'\[[^\]]+\]\([^)]+\)', lambda m: m.group(0).split(']')[0][1:], clean)
        clean = re.sub(r'\n{2,}', '. ', clean)
        clean = re.sub(r'\n', ' ', clean)
        clean = re.sub(r'\s+', ' ', clean).strip()

        async with httpx.AsyncClient() as client:
            res = await client.post(
                f"https://api.elevenlabs.io/v1/text-to-speech/{voice_id}",
                headers={
                    "xi-api-key": api_key,
                    "Content-Type": "application/json",
                },
                json={
                    "text": clean,
                    "model_id": "eleven_multilingual_v2",
                    "voice_settings": {
                        "stability": 0.5,
                        "similarity_boost": 0.75,
                    },
                },
                timeout=30,
            )
            res.raise_for_status()
            audio_data = res.content

        logger.info(f"TTS ElevenLabs: voice={voice_id}, size={len(audio_data)} bytes")
        return StreamingResponse(iter([audio_data]), media_type="audio/mpeg")
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
