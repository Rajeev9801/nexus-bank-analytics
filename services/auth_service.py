import hashlib
import sqlite3
import time
from services.database import get_connection
from utils import logger
from datetime import datetime

# --- Configuration ---
MAX_LOGIN_ATTEMPTS = 5
LOCKOUT_DURATION = 300 # 5 minutes in seconds

# Simple in-memory lockout tracker
lockouts = {}

def hash_password(password):
    """Secure SHA-256 hashing for passwords."""
    return hashlib.sha256(password.encode()).hexdigest()

def signup(username, password, full_name, role='ANALYST', email=None, status='Active'):
    """Creates a new user with hashed password."""
    try:
        username = username.lower().strip()
        if len(password) < 6:
            return False, "Password must be at least 6 characters."
            
        conn = get_connection()
        cursor = conn.cursor()
        
        # Check if user exists first to be clean
        cursor.execute("SELECT id FROM users WHERE username = ?", (username,))
        if cursor.fetchone():
            conn.close()
            return False, "Username already exists."
            
        hashed = hash_password(password)
        cursor.execute(
            "INSERT INTO users (username, password, full_name, role, email, status) VALUES (?, ?, ?, ?, ?, ?)",
            (username, hashed, full_name.strip(), role, email, status)
        )
        conn.commit()
        conn.close()
        logger.info(f"User registration successful: {username}")
        return True, "Account created successfully."
    except Exception as e:
        logger.error(f"Signup error: {e}")
        return False, f"Registration failed: {str(e)}"

def login(username, password, device_info=None, ip_address=None):
    """Validates user credentials against stored hashes."""
    username = username.lower().strip()
    
    # Check lockout
    if username in lockouts:
        attempts, last_time = lockouts[username]
        if attempts >= MAX_LOGIN_ATTEMPTS:
            if time.time() - last_time < LOCKOUT_DURATION:
                remaining = int(LOCKOUT_DURATION - (time.time() - last_time))
                return False, f"Security Lockout: Try again in {remaining}s."
            else:
                lockouts[username] = [0, 0]

    try:
        conn = get_connection()
        cursor = conn.cursor()
        hashed = hash_password(password)
        
        cursor.execute(
            "SELECT id, username, role, full_name, status FROM users WHERE username = ? AND password = ?",
            (username, hashed)
        )
        user = cursor.fetchone()
        
        if user:
            if user[4] != 'Active':
                conn.close()
                return False, "Account is deactivated. Contact administrator."
                
            cursor.execute("UPDATE users SET last_login = CURRENT_TIMESTAMP WHERE id = ?", (user[0],))
            
            # Record success activity
            cursor.execute(
                "INSERT INTO login_activity (user_id, username, status, device_info, ip_address) VALUES (?, ?, ?, ?, ?)",
                (user[0], username, 'SUCCESS', device_info, ip_address)
            )
            
            conn.commit()
            conn.close()
            lockouts[username] = [0, 0] # Reset attempts
            logger.info(f"Authentication successful for user: {username}")
            return True, {
                "id": user[0],
                "username": user[1],
                "role": user[2],
                "full_name": user[3]
            }
        
        # Record failed attempt
        cursor.execute(
            "INSERT INTO login_activity (username, status, device_info, ip_address) VALUES (?, ?, ?, ?)",
            (username, 'FAILED', device_info, ip_address)
        )
        conn.commit()
        conn.close()
        
        # Track failed attempts for lockout
        if username not in lockouts:
            lockouts[username] = [1, time.time()]
        else:
            lockouts[username][0] += 1
            lockouts[username][1] = time.time()
            
        logger.warning(f"Failed login attempt for: {username}")
        return False, "Invalid username or password. Please try again."
        
    except Exception as e:
        logger.error(f"Authentication engine failure: {e}")
        return False, "System temporarily unavailable. Please contact support."

def create_default_admin():
    """Automatically ensures a default admin exists and logs credentials on first run."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM users WHERE role = 'ADMIN'")
    if cursor.fetchone()[0] == 0:
        logger.info("First startup detected: Configuring default administrator...")
        success, msg = signup("admin", "admin123", "System Administrator", "ADMIN")
        if success:
            # Clear output for user visibility
            print("\n" + "="*50)
            print("NEXUS BANK ENTERPRISE - INITIAL SETUP COMPLETE")
            print("Default Credentials:")
            print("  Username: admin")
            print("  Password: admin123")
            print("="*50 + "\n")
            logger.info("Default administrator account generated successfully.")
    conn.close()

# --- Admin Management Functions ---

def get_all_users():
    try:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT id, username, full_name, email, role, status, created_at, last_login FROM users")
        users = cursor.fetchall()
        conn.close()
        return users
    except Exception as e:
        logger.error(f"Failed to fetch users: {e}")
        return []

def update_user(user_id, full_name, email, role, status):
    try:
        conn = get_connection()
        cursor = conn.cursor()
        
        # Prevent deactivating or changing role of the last admin if it's the current user? 
        # For now just a simple check.
        if status != 'Active' or role != 'ADMIN':
            cursor.execute("SELECT COUNT(*) FROM users WHERE role = 'ADMIN' AND status = 'Active'")
            if cursor.fetchone()[0] <= 1:
                cursor.execute("SELECT role, status FROM users WHERE id = ?", (user_id,))
                curr = cursor.fetchone()
                if curr and curr[0] == 'ADMIN' and curr[1] == 'Active':
                    conn.close()
                    return False, "Cannot deactivate or change role of the only active administrator."

        cursor.execute(
            "UPDATE users SET full_name = ?, email = ?, role = ?, status = ? WHERE id = ?",
            (full_name, email, role, status, user_id)
        )
        conn.commit()
        conn.close()
        return True, "User updated successfully."
    except Exception as e:
        logger.error(f"Failed to update user: {e}")
        return False, str(e)

def delete_user(user_id):
    try:
        conn = get_connection()
        cursor = conn.cursor()
        
        # Check if it's the last admin
        cursor.execute("SELECT role FROM users WHERE id = ?", (user_id,))
        role = cursor.fetchone()
        if role and role[0] == 'ADMIN':
            cursor.execute("SELECT COUNT(*) FROM users WHERE role = 'ADMIN'")
            if cursor.fetchone()[0] <= 1:
                conn.close()
                return False, "Cannot delete the only administrator account."
        
        cursor.execute("DELETE FROM users WHERE id = ?", (user_id,))
        conn.commit()
        conn.close()
        return True, "User deleted successfully."
    except Exception as e:
        logger.error(f"Failed to delete user: {e}")
        return False, str(e)

def reset_password(user_id, new_password):
    try:
        if len(new_password) < 6:
            return False, "Password must be at least 6 characters."
            
        conn = get_connection()
        cursor = conn.cursor()
        hashed = hash_password(new_password)
        cursor.execute("UPDATE users SET password = ? WHERE id = ?", (hashed, user_id))
        conn.commit()
        conn.close()
        return True, "Password reset successfully."
    except Exception as e:
        logger.error(f"Failed to reset password: {e}")
        return False, str(e)

def get_login_activity(limit=100):
    try:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute(
            "SELECT id, username, login_time, status, ip_address, device_info FROM login_activity ORDER BY login_time DESC LIMIT ?",
            (limit,)
        )
        activity = cursor.fetchall()
        conn.close()
        return activity
    except Exception as e:
        logger.error(f"Failed to fetch login activity: {e}")
        return []
