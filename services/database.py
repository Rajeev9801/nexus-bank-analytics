import sqlite3
import os
from pathlib import Path
from datetime import datetime
from utils import logger, BASE_DIR

# --- Absolute Path Resolution ---
DB_DIR = BASE_DIR / "database_files"
DB_PATH = DB_DIR / "nexus_bank.db"

def get_connection():
    """Returns a thread-safe connection to the absolute database path."""
    try:
        # Ensure directory exists
        if not DB_DIR.exists():
            DB_DIR.mkdir(parents=True, exist_ok=True)
            
        # Verify write permissions to the directory
        if os.access(DB_DIR, os.W_OK):
            conn = sqlite3.connect(str(DB_PATH), check_same_thread=False)
            return conn
        else:
            raise PermissionError(f"No write access to database directory: {DB_DIR}")
    except Exception as e:
        logger.critical(f"Failed to connect to database at {DB_PATH}")
        logger.error(f"Error: {e}")
        raise

def init_db():
    """Initializes the database schema with absolute path resolution."""
    logger.info(f"Resolving Database Path -> {DB_PATH}")
    
    conn = get_connection()
    cursor = conn.cursor()
    
    # Users Table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL,
            role TEXT DEFAULT 'Analyst',
            full_name TEXT,
            email TEXT,
            status TEXT DEFAULT 'Active',
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            last_login DATETIME
        )
    ''')
    
    # Migration: Add missing columns if they don't exist
    cursor.execute("PRAGMA table_info(users)")
    columns = [row[1] for row in cursor.fetchall()]
    
    if 'email' not in columns:
        cursor.execute("ALTER TABLE users ADD COLUMN email TEXT")
    if 'status' not in columns:
        cursor.execute("ALTER TABLE users ADD COLUMN status TEXT DEFAULT 'Active'")
    if 'created_at' not in columns:
        cursor.execute("ALTER TABLE users ADD COLUMN created_at DATETIME")
    
    # Login Activity Table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS login_activity (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            username TEXT,
            login_time DATETIME DEFAULT CURRENT_TIMESTAMP,
            logout_time DATETIME,
            status TEXT,
            ip_address TEXT,
            device_info TEXT,
            FOREIGN KEY(user_id) REFERENCES users(id)
        )
    ''')
    
    # Transactions Table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS transactions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            date DATETIME NOT NULL,
            acc_no TEXT NOT NULL,
            type TEXT NOT NULL,
            bank TEXT NOT NULL,
            amount REAL NOT NULL,
            balance REAL NOT NULL,
            status TEXT NOT NULL,
            is_fraud INTEGER DEFAULT 0,
            description TEXT
        )
    ''')
    
    # Alerts Table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS alerts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
            severity TEXT,
            message TEXT,
            is_read INTEGER DEFAULT 0
        )
    ''')
    
    # Reports Table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS reports (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            file_path TEXT,
            type TEXT
        )
    ''')
    
    conn.commit()
    conn.close()
    logger.info("Database system initialized successfully.")

if __name__ == "__main__":
    init_db()
