import sqlite3
import datetime
import uuid
import os

DB_NAME = "chat_history.db"

def get_db_connection():
    conn = sqlite3.connect(DB_NAME)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_db_connection()
    c = conn.cursor()
    
    # Sessions Table
    c.execute('''
        CREATE TABLE IF NOT EXISTS sessions (
            id TEXT PRIMARY KEY,
            title TEXT,
            created_at TIMESTAMP
        )
    ''')
    
    # Messages Table
    c.execute('''
        CREATE TABLE IF NOT EXISTS messages (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            session_id TEXT,
            role TEXT,
            content TEXT,
            created_at TIMESTAMP,
            FOREIGN KEY (session_id) REFERENCES sessions (id)
        )
    ''')
    
    conn.commit()
    conn.close()
    print(f"Database {DB_NAME} initialized.")

def create_session(title="New Chat"):
    session_id = str(uuid.uuid4())
    conn = get_db_connection()
    c = conn.cursor()
    c.execute('INSERT INTO sessions (id, title, created_at) VALUES (?, ?, ?)', 
              (session_id, title, datetime.datetime.now()))
    conn.commit()
    conn.close()
    return session_id

def add_message(session_id, role, content):
    conn = get_db_connection()
    c = conn.cursor()
    c.execute('INSERT INTO messages (session_id, role, content, created_at) VALUES (?, ?, ?, ?)',
              (session_id, role, content, datetime.datetime.now()))
    
    # Auto-update title if it's the first user message (title is still default)
    if role == 'user':
        new_title = content[:50] + "..." if len(content) > 50 else content
        c.execute('UPDATE sessions SET title = ? WHERE id = ? AND title = ?', 
                  (new_title, session_id, 'New Chat'))
    
    conn.commit()
    conn.close()

def get_sessions():
    conn = get_db_connection()
    c = conn.cursor()
    c.execute('SELECT * FROM sessions ORDER BY created_at DESC')
    rows = c.fetchall()
    conn.close()
    return [dict(row) for row in rows]

def get_messages(session_id):
    conn = get_db_connection()
    c = conn.cursor()
    c.execute('SELECT role, content FROM messages WHERE session_id = ? ORDER BY id ASC', (session_id,))
    rows = c.fetchall()
    conn.close()
    return [dict(row) for row in rows]

def delete_session(session_id):
    conn = get_db_connection()
    c = conn.cursor()
    # Cascading delete: messages first, then session
    c.execute('DELETE FROM messages WHERE session_id = ?', (session_id,))
    c.execute('DELETE FROM sessions WHERE id = ?', (session_id,))
    conn.commit()
    conn.close()
