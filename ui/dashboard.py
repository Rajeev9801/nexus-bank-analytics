import customtkinter as ctk
import pandas as pd
from tkinter import messagebox
from services.database import get_connection
from ui.sidebar import Sidebar
from ui.navbar import Navbar
from ui.cards import CardGrid
from ui.charts import AnalyticsCharts
from ui.transactions import TransactionTable
from ui.reports import ReportsTab
from ui.analytics import AnalyticsTab, SettingsTab
from ui.ai_insights import AIInsightsTab
from ui.admin_panel import UserManagementTab
from utils import COLORS, logger, VERSION

class BankingDashboard(ctk.CTkFrame):
    def __init__(self, parent, user, controller, *args, **kwargs):
        super().__init__(parent, fg_color=COLORS['bg'], *args, **kwargs)
        self.parent = parent
        self.user = user
        self.controller = controller
        
        self.setup_ui()
        logger.info(f"Premium Dashboard loaded for: {user['username']}")

    def setup_ui(self):
        # Layout: Sidebar (Left) + Content (Right)
        self.sidebar = Sidebar(self, self.controller, self.show_tab)
        self.sidebar.pack(side="left", fill="y")
        
        self.right_container = ctk.CTkFrame(self, fg_color="transparent")
        self.right_container.pack(side="right", expand=True, fill="both")
        
        # Navbar (Top of Right Container)
        self.navbar = Navbar(self.right_container, self.user, self.logout, self.refresh_data)
        self.navbar.pack(side="top", fill="x")
        
        # Main View (Below Navbar)
        self.main_view = ctk.CTkScrollableFrame(self.right_container, fg_color="transparent")
        self.main_view.pack(side="top", expand=True, fill="both", padx=20, pady=20)
        
        # Initialize Tabs
        self.tabs = {
            "Overview": self.render_overview,
            "Transactions": self.render_transactions,
            "AI Insights": self.render_ai_insights,
            "Reports": self.render_reports,
            "Analytics": self.render_analytics,
            "User Management": self.render_admin_panel,
            "Settings": self.render_settings
        }
        
        # Initial Data Load & First Tab
        self.refresh_data()
        self.sidebar.handle_click("Overview")

    def show_tab(self, tab_name):
        self.current_tab = tab_name
        for widget in self.main_view.winfo_children():
            widget.destroy()
            
        if tab_name in self.tabs:
            self.tabs[tab_name]()

    def refresh_data(self):
        try:
            conn = get_connection()
            full_df = pd.read_sql("SELECT * FROM transactions ORDER BY date DESC", conn)
            conn.close()
            
            # Global Search Filter
            search_term = self.navbar.search_var.get().lower()
            if search_term:
                self.df = full_df[
                    full_df['acc_no'].str.lower().str.contains(search_term, na=False) |
                    full_df['bank'].str.lower().str.contains(search_term, na=False) |
                    full_df['type'].str.lower().str.contains(search_term, na=False) |
                    full_df['description'].str.lower().str.contains(search_term, na=False)
                ]
            else:
                self.df = full_df

            # If a tab is already visible, re-render it
            if hasattr(self, 'current_tab'):
                self.show_tab(self.current_tab)
            else:
                self.show_tab("Overview")
        except Exception as e:
            logger.error(f"Dashboard Data Refresh Error: {e}")
            self.df = pd.DataFrame()

    def render_overview(self):
        # 1. Cards
        grid = CardGrid(self.main_view)
        grid.pack(fill="x", pady=(0, 20))
        
        balance = self.df.iloc[0]['balance'] if not self.df.empty else 0
        fraud_count = len(self.df[self.df['is_fraud'] == 1]) if not self.df.empty else 0
        status = "ACTIVE" if self.controller.simulator.running else "STANDBY"
        
        grid.update_metrics({
            "Total Balance": f"₹ {balance:,.2f}",
            "Transactions": str(len(self.df)),
            "Fraud Alerts": str(fraud_count),
            "System Health": status
        })

        # 2. Charts
        charts = AnalyticsCharts(self.main_view)
        charts.pack(fill="x", pady=20)
        charts.render_dashboard(self.df)
        
        # 3. Quick Table (Recent 10)
        table = TransactionTable(self.main_view)
        table.pack(fill="x", pady=20)
        table.update_data(self.df.head(10))

    def render_transactions(self):
        table = TransactionTable(self.main_view)
        table.pack(fill="both", expand=True)
        table.update_data(self.df)

    def render_ai_insights(self):
        tab = AIInsightsTab(self.main_view)
        tab.pack(fill="both", expand=True)
        tab.update_data(self.df)

    def render_reports(self):
        tab = ReportsTab(self.main_view)
        tab.pack(fill="both", expand=True)

    def render_analytics(self):
        tab = AnalyticsTab(self.main_view)
        tab.pack(fill="both", expand=True)
        tab.update_data(self.df)

    def render_admin_panel(self):
        # Additional role check for safety
        if self.user.get('role') != 'ADMIN':
            messagebox.showerror("Access Denied", "You do not have permission to access this panel.")
            self.show_tab("Overview")
            return
            
        tab = UserManagementTab(self.main_view)
        tab.pack(fill="both", expand=True)

    def render_settings(self):
        tab = SettingsTab(self.main_view)
        tab.pack(fill="both", expand=True)

    def logout(self):
        if messagebox.askyesno("Logout", "Are you sure you want to logout?"):
            self.controller.stop_simulator()
            self.destroy()
            self.parent.show_login()
