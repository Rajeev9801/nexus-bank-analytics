import customtkinter as ctk
from utils import COLORS
from services.ai_engine import analyze_fraud, predict_future_balance, get_spending_insights

class AIInsightsTab(ctk.CTkFrame):
    def __init__(self, parent):
        super().__init__(parent, fg_color="transparent")
        self.setup_ui()

    def setup_ui(self):
        ctk.CTkLabel(self, text="Account AI Analysis", font=("Segoe UI", 24, "bold"), text_color=COLORS['accent']).pack(pady=(20, 40))
        
        self.container = ctk.CTkFrame(self, fg_color=COLORS['card'], corner_radius=15, border_width=1, border_color=COLORS['border'])
        self.container.pack(fill="x", padx=40, pady=20)
        
        self.metrics = {}
        items = [
            ("Spending Pattern", "Loading...", "accent"),
            ("30-Day Forecast", "Loading...", "success"),
            ("Security Status", "Scanning...", "danger")
        ]
        
        for label, val, color in items:
            f = ctk.CTkFrame(self.container, fg_color="transparent")
            f.pack(fill="x", padx=40, pady=20)
            ctk.CTkLabel(f, text=label.upper(), font=("Segoe UI", 11, "bold"), text_color=COLORS['text_muted']).pack(anchor="w")
            v = ctk.CTkLabel(f, text=val, font=("Segoe UI", 18), text_color=COLORS[color])
            v.pack(anchor="w", pady=5)
            self.metrics[label] = v

    def update_data(self, df):
        insights = get_spending_insights(df)
        fraud_indices = analyze_fraud(df)
        prediction = predict_future_balance(df)
        
        self.metrics["Spending Pattern"].configure(text=insights)
        self.metrics["30-Day Forecast"].configure(text=f"Estimated Liquid Balance: ₹{prediction:,.2f}")
        
        fraud_msg = f"Detected {len(fraud_indices)} suspicious transactions." if fraud_indices else "No security threats detected."
        self.metrics["Security Status"].configure(text=fraud_msg, text_color=COLORS['danger'] if fraud_indices else COLORS['success'])
