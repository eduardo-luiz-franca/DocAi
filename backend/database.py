import sqlite3
import uuid
from datetime import datetime
from contextlib import contextmanager

DB_PATH = "docai.db"

@contextmanager
def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    try:
        yield conn
    finally:
        conn.close()

def init_db():
    """Cria as tabelas"""
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS conversations (
                id TEXT PRIMARY KEY,
                created_at TEXT
            )
        """)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS messages (
                id TEXT PRIMARY KEY,
                conversation_id TEXT,
                role TEXT,
                content TEXT,
                created_at TEXT,
                FOREIGN KEY (conversation_id) REFERENCES conversations(id)
            )
        """)
        conn.commit()

def create_conversation(conversation_id: str):
    """Cria conversa."""
    with get_db() as conn:
        cursor = conn.cursor()
        created_at = datetime.utcnow().isoformat()
        cursor.execute(
            "INSERT INTO conversations (id, created_at) VALUES (?, ?)",
            (conversation_id, created_at)
        )
        conn.commit()

def save_message(conversation_id: str, role: str, content: str):
    """Salva mensagem (user ou assistant)."""
    with get_db() as conn:
        cursor = conn.cursor()
        message_id = str(uuid.uuid4())
        created_at = datetime.utcnow().isoformat()
        cursor.execute(
            "INSERT INTO messages (id, conversation_id, role, content, created_at) VALUES (?, ?, ?, ?, ?)",
            (message_id, conversation_id, role, content, created_at)
        )
        conn.commit()
        return message_id

def get_conversation_messages(conversation_id: str):
    """Carrega mensagens de uma conversa."""
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute(
            "SELECT role, content FROM messages WHERE conversation_id = ? ORDER BY created_at ASC",
            (conversation_id,)
        )
        return [dict(row) for row in cursor.fetchall()]

def get_all_conversations():
    """Lista todas as conversas."""
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT id, created_at FROM conversations ORDER BY created_at DESC")
        return [dict(row) for row in cursor.fetchall()]

def delete_conversation(conversation_id: str):
    """Deleta uma conversa e suas mensagens."""
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute("DELETE FROM messages WHERE conversation_id = ?", (conversation_id,))
        cursor.execute("DELETE FROM conversations WHERE id = ?", (conversation_id,))
        conn.commit()
