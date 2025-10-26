# app/ai_client.py
import os

def respond_to(prompt: str, model: str = None) -> str:
    api_key = os.environ.get("GOOGLE_API_KEY")
    model_name = model or os.environ.get("DEFAULT_MODEL", "gemini-1.5-flash")
    if not api_key:
        # fallback: mock reply for development if no API key
        return f"[mock reply] Kamu menulis: {prompt}"
    try:
        from google import genai
        client = genai.Client(api_key=api_key)
        chat = client.chats.create(model=model_name)
        res = chat.send_message(prompt)
        return res.text
    except Exception as e:
        return f"[error contacting GenAI] {e}"
