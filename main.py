from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import google.generativeai as genai
import os
import uuid

# Inisialisasi FastAPI
app = FastAPI()

# Middleware agar bisa diakses dari frontend GitHub Pages
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # nanti bisa ubah ke domain kamu sendiri
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Simpan percakapan sementara di memori
conversations = {}

# Model data untuk pesan
class Message(BaseModel):
    conversation_id: str
    text: str

# Route utama (cek koneksi)
@app.get("/")
def root():
    return {"status": "ok", "note": "ChatIruL backend aktif dengan Gemini!"}

# Buat percakapan baru
@app.post("/conversations")
def new_conversation():
    cid = str(uuid.uuid4())
    conversations[cid] = []
    return {"id": cid}

# Ambil daftar percakapan
@app.get("/conversations")
def list_conversations():
    return [{"id": cid, "messages": conversations[cid]} for cid in conversations]

# Kirim pesan ke AI Gemini
@app.post("/chat")
def chat(msg: Message):
    if msg.conversation_id not in conversations:
        raise HTTPException(status_code=404, detail="Conversation tidak ditemukan")

    api_key = os.environ.get("GEMINI_API_KEY")
    if not api_key:
        raise HTTPException(status_code=500, detail="GEMINI_API_KEY belum diset di Render")

    try:
        # Konfigurasi Gemini API
        genai.configure(api_key=api_key)

        # Gunakan model stabil
        model = genai.GenerativeModel("gemini-1.5-flash")

        # Kirim pesan ke model
        response = model.generate_content(msg.text)
        answer = response.text

    except Exception as e:
        answer = f"[Error dari Gemini] {e}"

    # Simpan riwayat chat
    conversations[msg.conversation_id].append({"user": msg.text, "bot": answer})
    return {"response": answer}
