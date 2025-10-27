from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import google.generativeai as genai
import os, uuid
from dotenv import load_dotenv

# Load environment
load_dotenv()

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://jackgalza.github.io"],
    allow_credentials=True,
    allow_methods=["GET", "POST", "OPTIONS"],
    allow_headers=["Content-Type"],
)

conversations = {}

class Message(BaseModel):
    conversation_id: str
    text: str

@app.get("/")
def root():
    return {"status": "ok", "note": "ChatIruL backend aktif dengan Gemini!"}

@app.post("/conversations")
def new_conversation():
    cid = str(uuid.uuid4())
    conversations[cid] = []
    return {"id": cid}

@app.get("/conversations")
def list_conversations():
    return [{"id": cid, "messages": conversations[cid]} for cid in conversations]

@app.post("/chat")
def chat(msg: Message):
    if msg.conversation_id not in conversations:
        raise HTTPException(status_code=404, detail="Conversation tidak ditemukan")

    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        raise HTTPException(status_code=500, detail="GEMINI_API_KEY belum diset di environment")

    try:
        genai.configure(api_key=api_key)
        model = genai.GenerativeModel("gemini-1.5-flash")
        response = model.generate_content(msg.text)
        answer = response.text if hasattr(response, "text") else response.candidates[0].content.parts[0].text

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error dari Gemini: {e}")

    conversations[msg.conversation_id].append({"user": msg.text, "bot": answer})
    return {"response": answer}
