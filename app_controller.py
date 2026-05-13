import sys
from tkinter import messagebox
from services.auth_service import login, signup, create_default_admin
from services.database import init_db
from services.simulator import seed_initial_data, TransactionSimulator
from utils import logger

class AppController:
    """Centralized controller for managing app state and background services."""
    def __init__(self, root):
        self.root = root
        self.current_user = None
        self.simulator = TransactionSimulator(interval=10)
        self.db_initialized = False

    def initialize_system(self):
        try:
            init_db()
            create_default_admin()
            seed_initial_data()
            self.db_initialized = True
            logger.info("System initialization complete.")
        except Exception as e:
            logger.critical(f"Initialization failure: {e}")
            messagebox.showerror("System Error", "Database initialization failed. Check logs.")
            sys.exit(1)

    def start_simulator(self):
        if self.db_initialized:
            self.simulator.start()
            logger.info("Background transaction simulator started.")

    def stop_simulator(self):
        self.simulator.stop()
        logger.info("Background transaction simulator stopped.")

    def handle_login(self, username, password, callback):
        import platform
        import socket
        
        device = f"{platform.system()} {platform.release()}"
        try:
            ip = socket.gethostbyname(socket.gethostname())
        except:
            ip = "127.0.0.1"

        success, res = login(username, password, device_info=device, ip_address=ip)
        if success:
            self.current_user = res
            logger.info(f"User logged in: {username}")
            callback(True, res)
        else:
            logger.warning(f"Login failed for: {username}")
            callback(False, res)

    def handle_signup(self, username, password, full_name, callback):
        success, msg = signup(username, password, full_name)
        if success:
            logger.info(f"New user registered: {username}")
            callback(True, msg)
        else:
            logger.warning(f"Signup failed: {msg}")
            callback(False, msg)
