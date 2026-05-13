import customtkinter as ctk
from utils import COLORS, logger
from services.exporter import generate_enterprise_report
from tkinter import messagebox
import threading

class ReportsTab(ctk.CTkFrame):
    def __init__(self, parent):
        super().__init__(parent, fg_color="transparent")
        self.setup_ui()

    def setup_ui(self):
        ctk.CTkLabel(self, text="Enterprise Report Center", font=("Segoe UI", 24, "bold"), text_color=COLORS['text']).pack(pady=(20, 40))
        
        container = ctk.CTkFrame(self, fg_color="transparent")
        container.pack(fill="x", padx=40)
        
        formats = [
            ("PDF Report", "Detailed analytics with charts", "PDF", COLORS['accent']),
            ("CSV Export", "Raw transaction data for Excel", "CSV", COLORS['info']),
            ("Excel Export", "Formatted spreadsheet ledger", "Excel", COLORS['success'])
        ]
        
        for title, desc, fmt, color in formats:
            card = ctk.CTkFrame(container, fg_color=COLORS['card'], corner_radius=15, border_width=1, border_color=COLORS['border'])
            card.pack(side="left", padx=10, expand=True, fill="both")
            
            ctk.CTkLabel(card, text=title, font=("Segoe UI", 16, "bold"), text_color=color).pack(pady=(25, 5))
            ctk.CTkLabel(card, text=desc, font=("Segoe UI", 12), text_color=COLORS['text_muted']).pack(pady=(0, 25))
            
            ctk.CTkButton(card, text=f"Generate {fmt}", fg_color=color, text_color=COLORS['bg'], 
                         font=("Segoe UI", 13, "bold"), height=40, corner_radius=10,
                         command=lambda f=fmt: self.generate_report(f)).pack(pady=(0, 25), padx=30, fill="x")

    def generate_report(self, fmt):
        def task():
            success, path = generate_enterprise_report(fmt)
            if success:
                messagebox.showinfo("Success", f"Report generated successfully:\n{path}")
            else:
                messagebox.showerror("Error", f"Failed to generate report: {path}")
        
        threading.Thread(target=task, daemon=True).start()
