import customtkinter as ctk
from tkinter import messagebox
import sys
import traceback
import threading
from PIL import Image
import os
import time

# Add root to sys.path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app_controller import AppController
from ui.dashboard import BankingDashboard
from utils import COLORS, logger, APP_NAME, VERSION

# Configure CustomTkinter
ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

class NexusApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title(f"{APP_NAME} v{VERSION}")
        self.geometry("1400x800")
        self.configure(fg_color=COLORS['bg'])
        
        # Controller
        self.controller = AppController(self)
        
        # Global Error Handling
        self.report_callback_exception = self.handle_exception
        
        # UI State
        self.protocol("WM_DELETE_WINDOW", self.on_closing)
        
        self.show_splash()

    def handle_exception(self, exc, val, tb):
        err_msg = "".join(traceback.format_exception(exc, val, tb))
        logger.error(f"Unhandled UI Exception: {err_msg}")
        messagebox.showerror("Application Error", "An unexpected error occurred. Details have been logged.")

    def show_splash(self):
        self.splash_frame = ctk.CTkFrame(self, fg_color=COLORS['bg'])
        self.splash_frame.pack(expand=True, fill="both")
        
        # Logo Label (Using emoji as placeholder, could use Image later)
        self.logo_label = ctk.CTkLabel(self.splash_frame, text="🏦", font=("Segoe UI", 120))
        self.logo_label.pack(pady=(150, 20))
        
        self.title_label = ctk.CTkLabel(self.splash_frame, text=APP_NAME.upper(), 
                                      font=("Segoe UI", 40, "bold"), text_color=COLORS['accent'])
        self.title_label.pack()
        
        self.version_label = ctk.CTkLabel(self.splash_frame, text=f"PREMIUM ENTERPRISE EDITION | v{VERSION}", 
                                        font=("Segoe UI", 12), text_color=COLORS['text_muted'])
        self.version_label.pack(pady=10)
        
        self.progress_bar = ctk.CTkProgressBar(self.splash_frame, width=400, height=15, 
                                             progress_color=COLORS['accent'], fg_color=COLORS['sidebar'])
        self.progress_bar.set(0)
        self.progress_bar.pack(pady=50)
        
        self.init_progress = 0
        self.start_initialization()

    def start_initialization(self):
        def init_task():
            self.controller.initialize_system()
            self.init_complete = True

        self.init_complete = False
        threading.Thread(target=init_task, daemon=True).start()
        self.update_splash_progress()

    def update_splash_progress(self):
        if self.init_progress < 1.0:
            increment = 0.01 if not self.init_complete else 0.05
            self.init_progress += increment
            self.progress_bar.set(self.init_progress)
            self.after(20, self.update_splash_progress)
        elif self.init_complete:
            self.after(500, self.finish_splash)
        else:
            self.after(100, self.update_splash_progress)

    def finish_splash(self):
        if hasattr(self, 'splash_frame'):
            self.splash_frame.destroy()
        self.show_login()

    def show_login(self):
        self.auth_container = ctk.CTkFrame(self, fg_color=COLORS['bg'])
        self.auth_container.pack(expand=True, fill="both")
        
        # Center Card
        card = ctk.CTkFrame(self.auth_container, fg_color=COLORS['sidebar'], width=450, height=550, corner_radius=20, border_width=1, border_color=COLORS['border'])
        card.place(relx=0.5, rely=0.5, anchor="center")
        
        ctk.CTkLabel(card, text="SECURE ACCESS", font=("Segoe UI", 24, "bold"), text_color=COLORS['text']).pack(pady=(50, 40))
        
        # Inputs
        self.user_ent = self.create_input(card, "USERNAME", False)
        self.pass_ent = self.create_input(card, "PASSWORD", True)
        self.pass_ent.bind("<Return>", lambda e: self.process_login())
        
        ctk.CTkButton(card, text="SIGN IN", command=self.process_login, fg_color=COLORS['accent'], 
                     hover_color=COLORS['info'], font=("Segoe UI", 14, "bold"), height=50, corner_radius=10).pack(pady=(20, 0), padx=50, fill="x")
        
        ctk.CTkButton(card, text="Register New Analyst", command=self.show_signup, fg_color="transparent", 
                     text_color=COLORS['info'], font=("Segoe UI", 12), hover=False).pack(pady=(20, 0))

    def create_input(self, parent, label_text, is_pass):
        ctk.CTkLabel(parent, text=label_text, font=("Segoe UI", 11, "bold"), text_color=COLORS['text_muted']).pack(anchor="w", padx=50)
        ent = ctk.CTkEntry(parent, height=45, fg_color=COLORS['bg'], border_color=COLORS['border'], 
                          font=("Segoe UI", 13), show="*" if is_pass else "", corner_radius=10)
        ent.pack(pady=(5, 20), padx=50, fill="x")
        return ent

    def process_login(self):
        u, p = self.user_ent.get(), self.pass_ent.get()
        if not u or not p:
            messagebox.showwarning("Incomplete", "Please enter both credentials.")
            return
            
        def login_result(success, res):
            if success:
                self.auth_container.destroy()
                self.show_dashboard()
                self.controller.start_simulator()
            else:
                messagebox.showerror("Auth Error", res)

        self.controller.handle_login(u, p, login_result)

    def show_signup(self):
        self.auth_container.destroy()
        self.signup_container = ctk.CTkFrame(self, fg_color=COLORS['bg'])
        self.signup_container.pack(expand=True, fill="both")
        
        card = ctk.CTkFrame(self.signup_container, fg_color=COLORS['sidebar'], width=450, height=650, corner_radius=20, border_width=1, border_color=COLORS['border'])
        card.place(relx=0.5, rely=0.5, anchor="center")
        
        ctk.CTkLabel(card, text="SYSTEM REGISTRATION", font=("Segoe UI", 24, "bold"), text_color=COLORS['text']).pack(pady=(50, 30))
        
        self.name_ent = self.create_input(card, "FULL NAME", False)
        self.s_user_ent = self.create_input(card, "USERNAME", False)
        self.s_pass_ent = self.create_input(card, "ACCESS KEY (PASSWORD)", True)
        
        ctk.CTkButton(card, text="CREATE ACCOUNT", command=self.process_signup, fg_color=COLORS['success'], 
                     hover_color="#16a34a", font=("Segoe UI", 14, "bold"), height=50, corner_radius=10).pack(pady=(10, 0), padx=50, fill="x")
        
        ctk.CTkButton(card, text="Back to Login", command=self.back_to_login, fg_color="transparent", 
                     text_color=COLORS['text_muted'], font=("Segoe UI", 12), hover=False).pack(pady=10)

    def process_signup(self):
        n = self.name_ent.get()
        u = self.s_user_ent.get()
        p = self.s_pass_ent.get()
        
        if not n or not u or not p:
            messagebox.showwarning("Incomplete", "All fields are required.")
            return
            
        def signup_result(success, msg):
            if success:
                messagebox.showinfo("Registered", "Account created. You can now login.")
                self.back_to_login()
            else:
                messagebox.showerror("Error", msg)

        self.controller.handle_signup(u, p, n, signup_result)

    def back_to_login(self):
        self.signup_container.destroy()
        self.show_login()

    def show_dashboard(self):
        self.dashboard = BankingDashboard(self, user=self.controller.current_user, controller=self.controller)
        self.dashboard.pack(expand=True, fill="both")

    def on_closing(self):
        if messagebox.askokcancel("Quit", "Do you want to exit Nexus Bank Analytics?"):
            logger.info("Application shutdown initiated.")
            self.controller.stop_simulator()
            self.destroy()

if __name__ == "__main__":
    app = NexusApp()
    app.mainloop()
