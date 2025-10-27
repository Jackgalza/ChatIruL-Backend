from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import google.generativeai as genai
import os
import uuid

app = FastAPI()

# Middleware agar GitHub Pages bisa akses API backend Render
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # bisa diganti ke domain kamu nanti
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Simpan percakapan dalam memori sementara
conversations = {}

# Model pesan
class Message(BaseModel):
    conversation_id: str
    text: str

# Root API (cek koneksi)
@app.get("/")
def root():
    return {"status": "ok", "note": "ChatIruL backend aktif dengan Gemini v1!"}

# Buat conversation baru
@app.post("/conversations")
def new_conversation():
    cid = str(uuid.uuid4())
    conversations[cid] = []
    return {"id": cid}

# Ambil semua conversation
@app.get("/conversations")
def list_conversations():
    return [{"id": cid, "messages": conversations[cid]} for cid in conversations]

# Kirim pesan ke AI (Gemini)
@app.post("/chat")
def chat(msg: Message):
    if msg.conversation_id not in conversations:
        raise HTTPException(status_code=404, detail="Conversation tidak ditemukan")

    api_key = os.environ.get("GOOGLE_API_KEY")
    if not api_key:
        raise HTTPException(status_code=500, detail="GOOGLE_API_KEY tidak diset di Render")

    # Konfigurasi Gemini API
    genai.configure(api_key=api_key)

    # Pilih model yang benar (versi terbaru)
    model_name = os.environ.get("DEFAULT_MODEL", "gemini-1.5-flash-8b")

    try:
        model = genai.GenerativeModel(model_name)
        response = model.generate_content(msg.text)
        answer = response.text
    except Exception as e:
        answer = f"[Error dari Gemini] {e}"

    # Simpan riwayat percakapan
    conversations[msg.conversation_id].append({"user": msg.text, "bot": answer})
    return {"response": answer}
