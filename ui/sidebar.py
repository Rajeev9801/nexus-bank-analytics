import customtkinter as ctk
from utils import COLORS

class Sidebar(ctk.CTkFrame):
    def __init__(self, parent, controller, switch_tab_callback):
        super().__init__(parent, fg_color=COLORS['sidebar'], width=220, corner_radius=0)
        self.controller = controller
        self.switch_tab_callback = switch_tab_callback
        
        self.setup_ui()

    def setup_ui(self):
        # Logo
        self.logo_label = ctk.CTkLabel(self, text="🏦 NEXUS", font=("Segoe UI", 24, "bold"), text_color=COLORS['accent'])
        self.logo_label.pack(pady=40)
        
        self.nav_btns = {}
        nav_items = [
            ("Overview", "🏠"),
            ("Transactions", "📝"),
            ("AI Insights", "🧠"),
            ("Reports", "📊"),
            ("Analytics", "📈")
        ]
        
        # Admin Only
        if self.controller.current_user and self.controller.current_user.get('role') == 'ADMIN':
            nav_items.append(("User Management", "👥"))
            
        nav_items.append(("Settings", "⚙️"))
        
        for name, icon in nav_items:
            btn = ctk.CTkButton(self, text=f"  {icon}  {name}", 
                               font=("Segoe UI", 14),
                               fg_color="transparent",
                               text_color=COLORS['text'],
                               hover_color=COLORS['card'],
                               anchor="w",
                               height=50,
                               corner_radius=10,
                               command=lambda n=name: self.handle_click(n))
            btn.pack(fill="x", padx=10, pady=2)
            self.nav_btns[name] = btn

        # Active state will be set by Dashboard after initialization

    def handle_click(self, name):
        for btn_name, btn in self.nav_btns.items():
            if btn_name == name:
                btn.configure(fg_color=COLORS['card'], text_color=COLORS['accent'])
            else:
                btn.configure(fg_color="transparent", text_color=COLORS['text'])
        
        self.switch_tab_callback(name)
