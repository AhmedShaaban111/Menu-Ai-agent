from dotenv import load_dotenv
load_dotenv()

from contextlib import asynccontextmanager
from fastapi import FastAPI, HTTPException, UploadFile, File, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse, StreamingResponse
from pydantic import BaseModel
from loguru import logger
from groq import Groq
from src.database.chroma_db import get_menu_db
from src.agent.menu_agent import create_menu_agent, chat_with_agent
import os, io, tempfile, subprocess

agent       = None
groq_client = None

@asynccontextmanager
async def lifespan(app: FastAPI):
    global agent, groq_client
    logger.info("🍽️  Loading menu into vector database...")
    db = get_menu_db()
    if db.count() == 0:
        count = db.ingest()
        logger.info(f"✅ Ingested {count} menu items")
    else:
        logger.info(f"✅ Menu already loaded ({db.count()} items)")
    logger.info("🤖 Creating menu agent...")
    agent       = create_menu_agent()
    groq_client = Groq(api_key=os.getenv("GROQ_API_KEY"))
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


WHISPER_PROMPT = (
    "This is a restaurant ordering conversation. "
    "The customer may mention food items such as burger, pizza, pasta, fries, milkshake, lemonade. "
    "They may also mention sizes like small, medium, large, single, double, "
    "and add-ons like extra cheese, bacon, avocado, mushrooms."
)

def denoise_audio(input_bytes: bytes, input_ext: str = "webm") -> bytes:
    with tempfile.NamedTemporaryFile(suffix=f".{input_ext}", delete=False) as inp:
        inp.write(input_bytes)
        inp_path = inp.name
    out_path = inp_path.replace(f".{input_ext}", "_clean.wav")
    cmd = [
        "ffmpeg", "-y", "-i", inp_path,
        "-af", "highpass=f=200,lowpass=f=3000,afftdn=nf=-25,dynaudnorm",
        "-ar", "16000", "-ac", "1", out_path
    ]
    result = subprocess.run(cmd, capture_output=True)
    if result.returncode != 0:
        logger.warning(f"FFmpeg failed, using original: {result.stderr.decode()}")
        os.unlink(inp_path)
        return input_bytes
    with open(out_path, "rb") as f:
        clean_audio = f.read()
    os.unlink(inp_path)
    os.unlink(out_path)
    return clean_audio


@app.get("/", response_class=HTMLResponse)
def root():
    with open("chat_ui.html", "r") as f:
        return f.read()


@app.post("/transcribe")
async def transcribe(audio: UploadFile = File(...)):
    try:
        audio_bytes = await audio.read()
        logger.info(f"🎤 Received audio: {len(audio_bytes)} bytes")
        clean_bytes = denoise_audio(audio_bytes)
        transcription = groq_client.audio.transcriptions.create(
            file=("audio_clean.wav", clean_bytes),
            model="whisper-large-v3-turbo",
            language="en",
            prompt=WHISPER_PROMPT,
            temperature=0.0,
        )
        text = transcription.text.strip()
        logger.info(f"📝 Transcription: {text}")
        return {"text": text}
    except Exception as e:
        logger.error(f"Transcription error: {e}")
        raise HTTPException(status_code=500, detail=str(e))




@app.post("/chat", response_model=ChatResponse)
def chat(req: ChatRequest):
    if agent is None:
        raise HTTPException(status_code=503, detail="Agent not ready")
    try:
        response = chat_with_agent(agent, req.message, req.session_id)
        return ChatResponse(response=response, session_id=req.session_id)
    except Exception as e:
        logger.error(f"Chat error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/menu")
def get_full_menu():
    from src.data.menu_data import MENU_ITEMS
    return {"items": [item.model_dump() for item in MENU_ITEMS]}
