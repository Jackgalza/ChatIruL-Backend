from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from google import genai
import os
import uuid

app = FastAPI()

# Middleware untuk mengizinkan GitHub Pages mengakses backend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # kalau mau aman nanti ubah ke domain kamu aja
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Simpan percakapan dalam memori sementara
conversations = {}

# Model untuk pesan
class Message(BaseModel):
    conversation_id: str
    text: str

# API Root (cek koneksi)
@app.get("/")
def root():
    return {"status": "ok", "note": "ChatIruL backend aktif!"}

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

# Kirim pesan ke AI (Google Gemini)
@app.post("/chat")
def chat(msg: Message):
    if msg.conversation_id not in conversations:
        raise HTTPException(status_code=404, detail="Conversation tidak ditemukan")

    api_key = os.environ.get("GOOGLE_API_KEY")
    if not api_key:
        raise HTTPException(status_code=500, detail="GOOGLE_API_KEY tidak diset di Render")

    client = genai.Client(api_key=api_key)
    model_name = os.environ.get("DEFAULT_MODEL", "gemini-1.5-flash")

    try:
        chat = client.chats.create(model=model_name)
        response = chat.send_message(msg.text)
        answer = response.text
    except Exception as e:
        answer = f"[Error dari Gemini] {e}"

    # Simpan riwayat
    conversations[msg.conversation_id].append({"user": msg.text, "bot": answer})
    return {"response": answer}
