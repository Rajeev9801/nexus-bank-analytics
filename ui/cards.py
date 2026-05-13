import customtkinter as ctk
from utils import COLORS

class StatCard(ctk.CTkFrame):
    def __init__(self, parent, title, value, color_key, icon="💰"):
        super().__init__(parent, fg_color=COLORS['card'], corner_radius=15, border_width=1, border_color=COLORS['border'])
        
        self.title_label = ctk.CTkLabel(self, text=f"{icon} {title.upper()}", 
                                      font=("Segoe UI", 11, "bold"), text_color=COLORS['text_muted'])
        self.title_label.pack(anchor="w", padx=20, pady=(20, 5))
        
        self.value_label = ctk.CTkLabel(self, text=value, 
                                      font=("Segoe UI", 24, "bold"), text_color=COLORS[color_key])
        self.value_label.pack(anchor="w", padx=20, pady=(0, 20))

    def update_value(self, new_value):
        self.value_label.configure(text=new_value)

class CardGrid(ctk.CTkFrame):
    def __init__(self, parent):
        super().__init__(parent, fg_color="transparent")
        self.cards = {}
        self.setup_ui()

    def setup_ui(self):
        metrics = [
            ("Total Balance", "₹ 0.00", "success", "🏦"),
            ("Transactions", "0", "info", "📝"),
            ("Fraud Alerts", "0", "danger", "🚨"),
            ("System Health", "STABLE", "accent", "⚡")
        ]
        
        for i, (title, value, color, icon) in enumerate(metrics):
            card = StatCard(self, title, value, color, icon)
            card.pack(side="left", padx=10, expand=True, fill="both")
            self.cards[title] = card

    def update_metrics(self, data):
        for title, value in data.items():
            if title in self.cards:
                self.cards[title].update_value(value)
