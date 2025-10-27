from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import google.generativeai as genai
import os
import uuid
import traceback

app = FastAPI()

# Izinkan akses dari frontend (GitHub Pages)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # bisa diganti ke domain GitHub Pages kamu
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Simpan percakapan sementara (RAM)
conversations = {}

class Message(BaseModel):
    conversation_id: str
    text: str

@app.get("/")
def root():
    return {"status": "ok", "note": "ChatIruL backend aktif 🎯"}

# Tambahkan handler HEAD biar Render gak stuck di "In progress"
@app.head("/")
def head_root():
    return {"status": "ok"}

@app.post("/conversations")
def new_conversation():
    cid = str(uuid.uuid4())
    conversations[cid] = []
    return {"id": cid}

@app.post("/chat")
def chat(msg: Message):
    import traceback

    if msg.conversation_id not in conversations:
        raise HTTPException(status_code=404, detail="Conversation tidak ditemukan")

    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        raise HTTPException(status_code=500, detail="GEMINI_API_KEY tidak diset di Render")

    # Konfigurasi Gemini API
    genai.configure(api_key=api_key)

    try:
        model = genai.GenerativeModel("gemini-1.5-flash")
        response = model.generate_content(msg.text)
        answer = response.text
    except Exception as e:
        print("=== GEMINI ERROR ===")
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Gemini error: {e}")

    conversations[msg.conversation_id].append({"user": msg.text, "bot": answer})
    return {"response": answer}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
