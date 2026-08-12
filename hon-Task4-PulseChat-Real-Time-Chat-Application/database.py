import sqlite3
import os
from werkzeug.security import generate_password_hash, check_password_hash
from typing import List, Dict, Optional

DB_PATH = os.path.join(os.path.dirname(__file__), "chat.db")


def get_db():
    conn = sqlite3.connect(DB_PATH, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    """Initialize database tables for users, rooms, and messages."""
    with get_db() as conn:
        cursor = conn.cursor()

        # Users table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT UNIQUE NOT NULL,
                password_hash TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)

        # Rooms table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS rooms (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT UNIQUE NOT NULL,
                description TEXT,
                created_by TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)

        # Messages table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS messages (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                room_name TEXT NOT NULL,
                username TEXT NOT NULL,
                content TEXT NOT NULL,
                timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)

        # Seed default rooms if empty
        cursor.execute("SELECT COUNT(*) FROM rooms")
        if cursor.fetchone()[0] == 0:
            default_rooms = [
                ("General", "General discussion room for everyone", "system"),
                ("Tech & Code", "Discussions about Python, WebDev, and Tech", "system"),
                ("Random", "Casual talk, memes, and fun topics", "system")
            ]
            cursor.executemany(
                "INSERT INTO rooms (name, description, created_by) VALUES (?, ?, ?)",
                default_rooms
            )

        conn.commit()


def register_user(username: str, password: str) -> tuple[bool, str]:
    """Register a new user with hashed password."""
    username = username.strip()
    if not username or not password:
        return False, "Username and password are required."
    if len(username) < 3:
        return False, "Username must be at least 3 characters long."
    if len(password) < 4:
        return False, "Password must be at least 4 characters long."

    hashed_pw = generate_password_hash(password)
    try:
        with get_db() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "INSERT INTO users (username, password_hash) VALUES (?, ?)",
                (username, hashed_pw)
            )
            conn.commit()
            return True, "Registration successful."
    except sqlite3.IntegrityError:
        return False, "Username already exists. Please choose another."


def authenticate_user(username: str, password: str) -> bool:
    """Verify user credentials."""
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT password_hash FROM users WHERE username = ?", (username.strip(),))
        row = cursor.fetchone()
        if row and check_password_hash(row["password_hash"], password):
            return True
        return False


def get_all_rooms() -> List[Dict]:
    """Fetch all available rooms."""
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT id, name, description, created_by, created_at FROM rooms ORDER BY name ASC")
        rows = cursor.fetchall()
        return [dict(r) for r in rows]


def create_room(name: str, description: str, created_by: str) -> tuple[bool, str]:
    """Create a new chat room."""
    name = name.strip()
    description = description.strip()
    if not name:
        return False, "Room name cannot be empty."
    if len(name) < 2:
        return False, "Room name must be at least 2 characters."

    try:
        with get_db() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "INSERT INTO rooms (name, description, created_by) VALUES (?, ?, ?)",
                (name, description, created_by)
            )
            conn.commit()
            return True, "Room created successfully."
    except sqlite3.IntegrityError:
        return False, "A room with that name already exists."


def save_message(room_name: str, username: str, content: str) -> Dict:
    """Save a chat message to the database."""
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO messages (room_name, username, content) VALUES (?, ?, ?)",
            (room_name, username, content)
        )
        conn.commit()
        msg_id = cursor.lastrowid
        cursor.execute("SELECT id, room_name, username, content, timestamp FROM messages WHERE id = ?", (msg_id,))
        return dict(cursor.fetchone())


def get_room_history(room_name: str, limit: int = 100) -> List[Dict]:
    """Fetch past messages for a given room."""
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute(
            "SELECT id, room_name, username, content, timestamp FROM messages WHERE room_name = ? ORDER BY timestamp ASC LIMIT ?",
            (room_name, limit)
        )
        rows = cursor.fetchall()
        return [dict(r) for r in rows]
