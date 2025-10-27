from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import google.generativeai as genai
import os
import uuid
import traceback

app = FastAPI()

# CORS agar bisa diakses dari GitHub Pages
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Simpan percakapan sementara
conversations = {}

class Message(BaseModel):
    conversation_id: str
    text: str

@app.get("/")
def root():
    return {"status": "ok", "note": "ChatIruL backend aktif 🎯"}

@app.post("/conversations")
def new_conversation():
    cid = str(uuid.uuid4())
    conversations[cid] = []
    return {"id": cid}

@app.post("/chat")
def chat(msg: Message):
    if msg.conversation_id not in conversations:
        raise HTTPException(status_code=404, detail="Conversation tidak ditemukan")

    api_key = os.getenv("GOOGLE_API_KEY")
    if not api_key:
        raise HTTPException(status_code=500, detail="GOOGLE_API_KEY tidak diset di Render")

    genai.configure(api_key=api_key)
    model_name = "gemini-1.5-flash"

    try:
        model = genai.GenerativeModel(model_name)
        response = model.generate_content(msg.text)
        answer = response.text
    except Exception as e:
        print("=== ERROR GEMINI ===")
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))

    conversations[msg.conversation_id].append({"user": msg.text, "bot": answer})
    return {"response": answer}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
