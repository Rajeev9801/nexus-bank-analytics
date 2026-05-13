import customtkinter as ctk
from utils import COLORS, logger
import time
from datetime import datetime

class Navbar(ctk.CTkFrame):
    def __init__(self, parent, user, logout_callback, refresh_callback):
        super().__init__(parent, fg_color=COLORS['sidebar'], height=70, corner_radius=0)
        self.user = user
        self.logout_callback = logout_callback
        self.refresh_callback = refresh_callback
        
        self.setup_ui()
        self.update_clock()

    def setup_ui(self):
        # Left Side: Welcome & Search
        self.welcome_label = ctk.CTkLabel(self, text=f"Welcome, {self.user['full_name']}", 
                                        font=("Segoe UI", 16, "bold"), text_color=COLORS['text'])
        self.welcome_label.pack(side="left", padx=30)
        
        # Search Bar
        self.search_var = ctk.StringVar()
        self.search_var.trace_add("write", lambda *args: self.refresh_callback())
        self.search_entry = ctk.CTkEntry(self, placeholder_text="Search transactions...", 
                                        textvariable=self.search_var,
                                        width=300, height=35, fg_color=COLORS['bg'], 
                                        border_color=COLORS['border'], corner_radius=10)
        self.search_entry.pack(side="left", padx=20)

        # Right Side: Clock, Refresh, User Profile, Logout
        self.logout_btn = ctk.CTkButton(self, text="Logout", fg_color=COLORS['danger'], 
                                       hover_color="#b91c1c", width=100, height=35, 
                                       corner_radius=10, command=self.logout_callback)
        self.logout_btn.pack(side="right", padx=30)
        
        self.refresh_btn = ctk.CTkButton(self, text="🔄", fg_color=COLORS['info'], 
                                        hover_color="#4f46e5", width=40, height=35, 
                                        corner_radius=10, command=self.refresh_callback)
        self.refresh_btn.pack(side="right", padx=10)

        self.clock_label = ctk.CTkLabel(self, text="", font=("Segoe UI", 12), text_color=COLORS['text_muted'])
        self.clock_label.pack(side="right", padx=20)

    def update_clock(self):
        now = datetime.now().strftime("%d %b %Y | %H:%M:%S")
        self.clock_label.configure(text=now)
        self.after(1000, self.update_clock)
