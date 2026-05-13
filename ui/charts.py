import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import customtkinter as ctk
from utils import COLORS, logger

class AnalyticsCharts(ctk.CTkFrame):
    def __init__(self, parent):
        super().__init__(parent, fg_color=COLORS['card'], corner_radius=15, border_width=1, border_color=COLORS['border'])
        self.setup_dark_theme()
        
    def setup_dark_theme(self):
        plt.rcParams.update({
            'figure.facecolor': COLORS['card'],
            'axes.facecolor': COLORS['card'],
            'axes.edgecolor': COLORS['border'],
            'axes.labelcolor': COLORS['text'],
            'xtick.color': COLORS['text_muted'],
            'ytick.color': COLORS['text_muted'],
            'text.color': COLORS['text'],
            'grid.color': COLORS['border'],
            'font.size': 8
        })

    def render_dashboard(self, df):
        # Clear existing
        for widget in self.winfo_children():
            widget.destroy()

        if df.empty:
            ctk.CTkLabel(self, text="Waiting for Data...", text_color=COLORS['text_muted']).pack(expand=True)
            return

        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(10, 4))
        fig.subplots_adjust(bottom=0.2)

        try:
            # 1. Bar Chart -> Expenses vs Income
            type_sums = df.groupby('type')['amount'].sum()
            colors = [COLORS['success'] if t == 'Deposit' else COLORS['danger'] for t in type_sums.index]
            type_sums.plot(kind='bar', ax=ax1, color=colors)
            ax1.set_title("Inflow vs Outflow", pad=20)
            ax1.set_xlabel("")

            # 2. Donut Chart -> Activity by Bank
            bank_counts = df['bank'].value_counts()
            bank_counts.plot(kind='pie', ax=ax2, autopct='%1.0f%%', 
                             colors=[COLORS['accent'], COLORS['info'], COLORS['warning'], COLORS['success']],
                             wedgeprops={'width': 0.4})
            ax2.set_title("Distribution by Bank", pad=20)
            ax2.set_ylabel("")
            
            fig.tight_layout()
            
            canvas = FigureCanvasTkAgg(fig, master=self)
            canvas.draw()
            canvas.get_tk_widget().pack(fill="both", expand=True, padx=10, pady=10)
        except Exception as e:
            logger.error(f"Chart Render Error: {e}")
            ctk.CTkLabel(self, text="Visualizer Error", text_color=COLORS['danger']).pack(expand=True)

    def render_analytics(self, df):
        # Additional charts for Analytics page
        for widget in self.winfo_children():
            widget.destroy()

        if df.empty:
            ctk.CTkLabel(self, text="Waiting for Data...", text_color=COLORS['text_muted']).pack(expand=True)
            return

        fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(10, 8))

        try:
            # 1. Line Chart -> Balance Trend
            df_sorted = df.sort_values('date')
            ax1.plot(df_sorted['date'], df_sorted['balance'], color=COLORS['accent'], linewidth=2)
            ax1.fill_between(df_sorted['date'], df_sorted['balance'], color=COLORS['accent'], alpha=0.1)
            ax1.set_title("Balance Trend Over Time")
            ax1.set_xticks([]) # Hide x labels to avoid clutter

            # 2. Fraud Trend (Heatmap-like Bar)
            fraud_daily = df[df['is_fraud'] == 1].groupby(df['date'].str[:10]).size()
            fraud_daily.plot(kind='bar', ax=ax2, color=COLORS['danger'])
            ax2.set_title("Fraud Alerts Trend")
            
            fig.tight_layout()
            
            canvas = FigureCanvasTkAgg(fig, master=self)
            canvas.draw()
            canvas.get_tk_widget().pack(fill="both", expand=True, padx=10, pady=10)
        except Exception as e:
            logger.error(f"Analytics Chart Error: {e}")
            ctk.CTkLabel(self, text="Analytics Visualizer Error", text_color=COLORS['danger']).pack(expand=True)
