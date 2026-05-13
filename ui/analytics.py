import customtkinter as ctk
from utils import COLORS
from ui.charts import AnalyticsCharts
import pandas as pd
from services.database import get_connection
from services.ai_engine import get_spending_insights, analyze_fraud

class AnalyticsTab(ctk.CTkFrame):
    def __init__(self, parent):
        super().__init__(parent, fg_color="transparent")
        self.setup_ui()

    def setup_ui(self):
        self.charts = AnalyticsCharts(self)
        self.charts.pack(fill="both", expand=True, padx=20, pady=20)
        
        self.insights_box = ctk.CTkFrame(self, fg_color=COLORS['card'], corner_radius=15, border_width=1, border_color=COLORS['border'])
        self.insights_box.pack(fill="x", padx=20, pady=(0, 20))
        
        ctk.CTkLabel(self.insights_box, text="SMART INSIGHTS", font=("Segoe UI", 12, "bold"), text_color=COLORS['accent']).pack(anchor="w", padx=20, pady=(15, 5))
        self.insights_text = ctk.CTkLabel(self.insights_box, text="Loading insights...", font=("Segoe UI", 14), text_color=COLORS['text'])
        self.insights_text.pack(anchor="w", padx=20, pady=(0, 15))

    def update_data(self, df):
        self.charts.render_analytics(df)
        insights = get_spending_insights(df)
        fraud_count = len(analyze_fraud(df))
        full_insights = f"{insights}\nSecurity Status: {fraud_count} suspicious activities flagged."
        self.insights_text.configure(text=full_insights)

class SettingsTab(ctk.CTkFrame):
    def __init__(self, parent):
        super().__init__(parent, fg_color="transparent")
        self.setup_ui()

    def setup_ui(self):
        ctk.CTkLabel(self, text="Application Settings", font=("Segoe UI", 24, "bold"), text_color=COLORS['text']).pack(pady=(20, 40))
        
        container = ctk.CTkFrame(self, fg_color=COLORS['sidebar'], corner_radius=15, border_width=1, border_color=COLORS['border'])
        container.pack(fill="both", expand=True, padx=100, pady=(0, 100))
        
        # Appearance Mode
        ctk.CTkLabel(container, text="Appearance Mode", font=("Segoe UI", 14, "bold"), text_color=COLORS['text']).pack(anchor="w", padx=40, pady=(40, 10))
        self.appearance_mode = ctk.CTkOptionMenu(container, values=["Dark", "Light", "System"], 
                                               command=self.change_appearance_mode,
                                               fg_color=COLORS['card'], button_color=COLORS['accent'], 
                                               button_hover_color=COLORS['info'])
        self.appearance_mode.pack(anchor="w", padx=40)
        
        # Simulator Interval
        ctk.CTkLabel(container, text="Refresh Interval (Seconds)", font=("Segoe UI", 14, "bold"), text_color=COLORS['text']).pack(anchor="w", padx=40, pady=(30, 10))
        self.interval_slider = ctk.CTkSlider(container, from_=1, to=60, number_of_steps=59, button_color=COLORS['accent'])
        self.interval_slider.pack(anchor="w", padx=40, fill="x")
        self.interval_slider.set(10)

    def change_appearance_mode(self, new_mode):
        ctk.set_appearance_mode(new_mode)
