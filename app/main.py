from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import google.generativeai as genai
import os
import uuid
import traceback

app = FastAPI()

# -----------------------------
#  CORS agar frontend GitHub Pages bisa akses backend
# -----------------------------
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # kalau mau aman, ubah ke domain GitHub Pages kamu
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# -----------------------------
#  Simpan percakapan sementara di memori
# -----------------------------
conversations = {}

# -----------------------------
#  Model request dari frontend
# -----------------------------
class Message(BaseModel):
    conversation_id: str
    text: str

# -----------------------------
#  Root endpoint (cek koneksi)
# -----------------------------
@app.get("/")
def root():
    return {"status": "ok", "note": "ChatIruL backend aktif dengan Gemini v1!"}

# -----------------------------
#  Buat percakapan baru
# -----------------------------
@app.post("/conversations")
def new_conversation():
    cid = str(uuid.uuid4())
    conversations[cid] = []
    return {"id": cid}

# -----------------------------
#  Ambil semua percakapan aktif
# -----------------------------
@app.get("/conversations")
def list_conversations():
    return [{"id": cid, "messages": conversations[cid]} for cid in conversations]

# -----------------------------
#  Kirim pesan ke AI Gemini
# -----------------------------
@app.post("/chat")
def chat(msg: Message):
    # Pastikan conversation ID valid
    if msg.conversation_id not in conversations:
        raise HTTPException(status_code=404, detail="Conversation tidak ditemukan")

    # Ambil API key dari Render
    api_key = os.environ.get("GOOGLE_API_KEY")
    if not api_key:
        raise HTTPException(status_code=500, detail="GOOGLE_API_KEY tidak diset di Render")

    # Konfigurasi Gemini
    genai.configure(api_key=api_key)
    model_name = os.environ.get("DEFAULT_MODEL", "gemini-1.5-flash")

    try:
        # Kirim ke Gemini API
        model = genai.GenerativeModel(model_name)
        response = model.generate_content(msg.text)

        # Ambil hasil text
        answer = response.text

    except Exception as e:
        print("=== ERROR GEMINI ===")
        traceback.print_exc()
        answer = f"[Error dari Gemini] {e}"

    # Simpan riwayat
    conversations[msg.conversation_id].append({
        "user": msg.text,
        "bot": answer
    })

    return {"response": answer}

# -----------------------------
#  Jalankan secara lokal (opsional)
# -----------------------------
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
