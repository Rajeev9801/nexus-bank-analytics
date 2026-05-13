import tkinter as tk
from tkinter import ttk
import customtkinter as ctk
from utils import COLORS

class TransactionTable(ctk.CTkFrame):
    def __init__(self, parent):
        super().__init__(parent, fg_color=COLORS['card'], corner_radius=15, border_width=1, border_color=COLORS['border'])
        self.setup_ui()

    def setup_ui(self):
        # Header
        header_frame = ctk.CTkFrame(self, fg_color="transparent")
        header_frame.pack(fill="x", padx=20, pady=15)
        
        ctk.CTkLabel(header_frame, text="Transaction Ledger", 
                     font=("Segoe UI", 16, "bold"), text_color=COLORS['text']).pack(side="left")
        
        # Table Styling
        style = ttk.Style()
        style.theme_use("default")
        
        style.configure("Treeview",
                        background=COLORS['card'],
                        foreground=COLORS['text'],
                        rowheight=35,
                        fieldbackground=COLORS['card'],
                        bordercolor=COLORS['border'],
                        borderwidth=0)
        
        style.map("Treeview", background=[('selected', COLORS['accent'])])
        
        style.configure("Treeview.Heading",
                        background=COLORS['sidebar'],
                        foreground=COLORS['text_muted'],
                        relief="flat",
                        font=("Segoe UI", 10, "bold"))
        
        # Scrollbar
        tree_frame = tk.Frame(self, bg=COLORS['card'])
        tree_frame.pack(fill="both", expand=True, padx=20, pady=(0, 20))
        
        self.cols = ("Date", "Account", "Type", "Bank", "Amount", "Status")
        self.tree = ttk.Treeview(tree_frame, columns=self.cols, show="headings", height=15, style="Treeview")
        
        for col in self.cols:
            self.tree.heading(col, text=col)
            self.tree.column(col, width=120, anchor="center")
            
        self.tree.pack(side="left", fill="both", expand=True)
        
        sb = ttk.Scrollbar(tree_frame, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=sb.set)
        sb.pack(side="right", fill="y")
        
        # Tag configuration for fraud
        self.tree.tag_configure('fraud', foreground=COLORS['danger'])

    def update_data(self, df):
        # Clear existing
        for item in self.tree.get_children():
            self.tree.delete(item)
            
        # Insert new
        for _, row in df.head(100).iterrows():
            tag = 'fraud' if row.get('is_fraud', 0) == 1 else 'normal'
            self.tree.insert("", "end", values=(
                row['date'], 
                row['acc_no'], 
                row['type'], 
                row['bank'], 
                f"₹{row['amount']:,.2f}", 
                row['status']
            ), tags=(tag,))
