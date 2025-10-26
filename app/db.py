# app/db.py
import sqlite3
import threading
import time
import os

DB_PATH = os.environ.get("CHAT_DB_PATH", "data/chat.db")
_lock = threading.Lock()

def init_db():
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    with _lock:
        conn = sqlite3.connect(DB_PATH)
        cur = conn.cursor()
        cur.execute("""
        CREATE TABLE IF NOT EXISTS sessions (
            session_id TEXT PRIMARY KEY,
            created_at INTEGER
        )""")
        cur.execute("""
        CREATE TABLE IF NOT EXISTS conversations (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            session_id TEXT,
            title TEXT,
            created_at INTEGER
        )""")
        cur.execute("""
        CREATE TABLE IF NOT EXISTS messages (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            conversation_id INTEGER,
            role TEXT,
            content TEXT,
            created_at INTEGER
        )""")
        conn.commit()
        conn.close()

def create_session(session_id: str):
    with _lock:
        conn = sqlite3.connect(DB_PATH)
        cur = conn.cursor()
        cur.execute("INSERT OR IGNORE INTO sessions(session_id, created_at) VALUES (?,?)",
                    (session_id, int(time.time())))
        conn.commit()
        conn.close()

def create_conversation(session_id: str, title: str = "New conversation") -> int:
    ts = int(time.time())
    with _lock:
        conn = sqlite3.connect(DB_PATH)
        cur = conn.cursor()
        cur.execute("INSERT INTO conversations(session_id, title, created_at) VALUES (?,?,?)",
                    (session_id, title, ts))
        conv_id = cur.lastrowid
        conn.commit()
        conn.close()
    return conv_id

def list_conversations(session_id: str):
    with _lock:
        conn = sqlite3.connect(DB_PATH)
        cur = conn.cursor()
        cur.execute("SELECT id, title, created_at FROM conversations WHERE session_id=? ORDER BY created_at DESC",
                    (session_id,))
        rows = cur.fetchall()
        conn.close()
    return [{"id": r[0], "title": r[1], "created_at": r[2]} for r in rows]

def add_message(conversation_id: int, role: str, content: str):
    ts = int(time.time())
    with _lock:
        conn = sqlite3.connect(DB_PATH)
        cur = conn.cursor()
        cur.execute("INSERT INTO messages(conversation_id, role, content, created_at) VALUES (?,?,?,?)",
                    (conversation_id, role, content, ts))
        conn.commit()
        conn.close()

def get_messages(conversation_id: int):
    with _lock:
        conn = sqlite3.connect(DB_PATH)
        cur = conn.cursor()
        cur.execute("SELECT id, role, content, created_at FROM messages WHERE conversation_id=? ORDER BY id ASC",
                    (conversation_id,))
        rows = cur.fetchall()
        conn.close()
    return [{"id": r[0], "role": r[1], "content": r[2], "created_at": r[3]} for r in rows]
