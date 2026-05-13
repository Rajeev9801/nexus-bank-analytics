import customtkinter as ctk
import tkinter as tk
from tkinter import ttk, messagebox
from utils import COLORS, logger
from services.auth_service import get_all_users, signup, update_user, delete_user, reset_password, get_login_activity

class UserManagementTab(ctk.CTkFrame):
    def __init__(self, parent):
        super().__init__(parent, fg_color="transparent")
        self.setup_ui()

    def setup_ui(self):
        # Header
        header = ctk.CTkFrame(self, fg_color="transparent")
        header.pack(fill="x", pady=(0, 20))
        
        ctk.CTkLabel(header, text="User Management", font=("Segoe UI", 24, "bold"), text_color=COLORS['text']).pack(side="left")
        
        ctk.CTkButton(header, text="+ Add New User", fg_color=COLORS['success'], hover_color="#16a34a", 
                     font=("Segoe UI", 13, "bold"), height=40, corner_radius=10,
                     command=self.show_add_user_modal).pack(side="right")

        # Stats/Activity Link
        ctk.CTkButton(header, text="View Login Activity", fg_color=COLORS['info'], hover_color="#4f46e5",
                     font=("Segoe UI", 12), height=40, corner_radius=10,
                     command=self.show_activity_modal).pack(side="right", padx=10)

        # Filters & Search
        filter_frame = ctk.CTkFrame(self, fg_color=COLORS['card'], corner_radius=15, border_width=1, border_color=COLORS['border'])
        filter_frame.pack(fill="x", pady=(0, 20))
        
        self.search_var = ctk.StringVar()
        self.search_var.trace_add("write", lambda *args: self.refresh_table())
        ctk.CTkEntry(filter_frame, placeholder_text="Search by username or name...", 
                    textvariable=self.search_var, width=400, height=40, 
                    fg_color=COLORS['bg'], border_color=COLORS['border']).pack(side="left", padx=20, pady=15)
        
        self.role_filter = ctk.CTkOptionMenu(filter_frame, values=["All Roles", "ADMIN", "ANALYST", "VIEWER"],
                                            command=lambda _: self.refresh_table(),
                                            fg_color=COLORS['bg'], button_color=COLORS['accent'])
        self.role_filter.pack(side="left", padx=10)
        
        self.status_filter = ctk.CTkOptionMenu(filter_frame, values=["All Status", "Active", "Deactivated"],
                                              command=lambda _: self.refresh_table(),
                                              fg_color=COLORS['bg'], button_color=COLORS['accent'])
        self.status_filter.pack(side="left", padx=10)

        # Table
        self.table_container = ctk.CTkFrame(self, fg_color=COLORS['card'], corner_radius=15, border_width=1, border_color=COLORS['border'])
        self.table_container.pack(fill="both", expand=True)
        
        self.setup_table()
        self.refresh_table()

    def setup_table(self):
        style = ttk.Style()
        style.configure("Admin.Treeview", background=COLORS['card'], foreground=COLORS['text'], 
                        rowheight=40, fieldbackground=COLORS['card'], borderwidth=0)
        style.map("Admin.Treeview", background=[('selected', COLORS['accent'])])
        style.configure("Admin.Treeview.Heading", background=COLORS['sidebar'], foreground=COLORS['text_muted'], 
                        relief="flat", font=("Segoe UI", 10, "bold"))

        tree_frame = tk.Frame(self.table_container, bg=COLORS['card'])
        tree_frame.pack(fill="both", expand=True, padx=20, pady=20)
        
        self.cols = ("ID", "Username", "Full Name", "Email", "Role", "Status", "Created", "Last Login")
        self.tree = ttk.Treeview(tree_frame, columns=self.cols, show="headings", style="Admin.Treeview")
        
        for col in self.cols:
            self.tree.heading(col, text=col)
            width = 100 if col in ["ID", "Role", "Status"] else 150
            self.tree.column(col, width=width, anchor="center")
            
        self.tree.pack(side="left", fill="both", expand=True)
        
        sb = ttk.Scrollbar(tree_frame, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=sb.set)
        sb.pack(side="right", fill="y")
        
        # Action Buttons below table
        actions = ctk.CTkFrame(self.table_container, fg_color="transparent")
        actions.pack(fill="x", padx=20, pady=(0, 20))
        
        ctk.CTkButton(actions, text="Edit User", fg_color=COLORS['accent'], width=120, command=self.handle_edit).pack(side="left", padx=5)
        ctk.CTkButton(actions, text="Delete User", fg_color=COLORS['danger'], width=120, command=self.handle_delete).pack(side="left", padx=5)
        ctk.CTkButton(actions, text="Reset Password", fg_color=COLORS['warning'], text_color=COLORS['bg'], width=150, command=self.handle_reset_pass).pack(side="left", padx=5)

    def refresh_table(self):
        users = get_all_users()
        search = self.search_var.get().lower()
        role_f = self.role_filter.get()
        status_f = self.status_filter.get()
        
        # Clear
        for item in self.tree.get_children():
            self.tree.delete(item)
            
        for u in users:
            # Filters
            if search and search not in u[1].lower() and search not in u[2].lower(): continue
            if role_f != "All Roles" and u[4] != role_f: continue
            if status_f != "All Status" and u[5] != status_f: continue
            
            self.tree.insert("", "end", values=u)

    def show_add_user_modal(self):
        modal = UserModal(self, "Add New User", self.refresh_table)

    def handle_edit(self):
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning("Selection", "Please select a user to edit.")
            return
        
        values = self.tree.item(selected[0])['values']
        modal = UserModal(self, "Edit User", self.refresh_table, user_data=values)

    def handle_delete(self):
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning("Selection", "Please select a user to delete.")
            return
        
        u_id = self.tree.item(selected[0])['values'][0]
        u_name = self.tree.item(selected[0])['values'][1]
        
        if messagebox.askyesno("Confirm Delete", f"Are you sure you want to delete user '{u_name}'?"):
            success, msg = delete_user(u_id)
            if success:
                messagebox.showinfo("Success", msg)
                self.refresh_table()
            else:
                messagebox.showerror("Error", msg)

    def handle_reset_pass(self):
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning("Selection", "Please select a user.")
            return
        
        u_id = self.tree.item(selected[0])['values'][0]
        u_name = self.tree.item(selected[0])['values'][1]
        modal = PasswordResetModal(self, u_id, u_name)

    def show_activity_modal(self):
        ActivityModal(self)

class UserModal(ctk.CTkToplevel):
    def __init__(self, parent, title, on_success, user_data=None):
        super().__init__(parent)
        self.title(title)
        self.geometry("500x700")
        self.on_success = on_success
        self.user_data = user_data # If editing
        self.configure(fg_color=COLORS['bg'])
        
        # Make modal-like
        self.grab_set()
        self.setup_ui()

    def setup_ui(self):
        container = ctk.CTkFrame(self, fg_color=COLORS['sidebar'], corner_radius=20, border_width=1, border_color=COLORS['border'])
        container.pack(fill="both", expand=True, padx=20, pady=20)
        
        ctk.CTkLabel(container, text=self.title(), font=("Segoe UI", 20, "bold")).pack(pady=20)
        
        fields = [
            ("Username", "username", False),
            ("Full Name", "full_name", False),
            ("Email", "email", False)
        ]
        
        self.entries = {}
        for label, key, is_pass in fields:
            ctk.CTkLabel(container, text=label, font=("Segoe UI", 12)).pack(anchor="w", padx=40, pady=(10, 0))
            ent = ctk.CTkEntry(container, width=350, height=35)
            ent.pack(padx=40, pady=5)
            self.entries[key] = ent
            if self.user_data:
                # Map user_data index to key
                idx = {"username": 1, "full_name": 2, "email": 3}[key]
                ent.insert(0, self.user_data[idx])
                if key == "username": ent.configure(state="disabled") # Don't allow changing username

        if not self.user_data:
            # Passwords only for NEW users
            ctk.CTkLabel(container, text="Password", font=("Segoe UI", 12)).pack(anchor="w", padx=40, pady=(10, 0))
            self.pass_ent = ctk.CTkEntry(container, width=350, height=35, show="*")
            self.pass_ent.pack(padx=40, pady=5)
            
            ctk.CTkLabel(container, text="Confirm Password", font=("Segoe UI", 12)).pack(anchor="w", padx=40, pady=(10, 0))
            self.conf_pass_ent = ctk.CTkEntry(container, width=350, height=35, show="*")
            self.conf_pass_ent.pack(padx=40, pady=5)

        ctk.CTkLabel(container, text="Role", font=("Segoe UI", 12)).pack(anchor="w", padx=40, pady=(10, 0))
        self.role_opt = ctk.CTkOptionMenu(container, values=["ADMIN", "ANALYST", "VIEWER"], width=350)
        self.role_opt.pack(padx=40, pady=5)
        if self.user_data: self.role_opt.set(self.user_data[4])

        ctk.CTkLabel(container, text="Status", font=("Segoe UI", 12)).pack(anchor="w", padx=40, pady=(10, 0))
        self.status_opt = ctk.CTkOptionMenu(container, values=["Active", "Deactivated"], width=350)
        self.status_opt.pack(padx=40, pady=5)
        if self.user_data: self.status_opt.set(self.user_data[5])

        ctk.CTkButton(container, text="Save User", fg_color=COLORS['success'], height=45, command=self.save).pack(pady=30, padx=40, fill="x")

    def save(self):
        u = self.entries['username'].get()
        n = self.entries['full_name'].get()
        e = self.entries['email'].get()
        r = self.role_opt.get()
        s = self.status_opt.get()
        
        if not u or not n:
            messagebox.showwarning("Missing Info", "Username and Full Name are required.")
            return

        if self.user_data:
            # Edit
            success, msg = update_user(self.user_data[0], n, e, r, s)
        else:
            # Add
            p = self.pass_ent.get()
            cp = self.conf_pass_ent.get()
            if p != cp:
                messagebox.showerror("Password", "Passwords do not match.")
                return
            if len(p) < 6:
                messagebox.showerror("Password", "Password too short.")
                return
            success, msg = signup(u, p, n, role=r, email=e, status=s)

        if success:
            messagebox.showinfo("Success", msg)
            self.on_success()
            self.destroy()
        else:
            messagebox.showerror("Error", msg)

class PasswordResetModal(ctk.CTkToplevel):
    def __init__(self, parent, user_id, username):
        super().__init__(parent)
        self.title("Reset Password")
        self.geometry("400x350")
        self.user_id = user_id
        self.configure(fg_color=COLORS['bg'])
        self.grab_set()
        
        container = ctk.CTkFrame(self, fg_color=COLORS['sidebar'], corner_radius=20, border_width=1, border_color=COLORS['border'])
        container.pack(fill="both", expand=True, padx=20, pady=20)
        
        ctk.CTkLabel(container, text=f"Reset Password for {username}", font=("Segoe UI", 16, "bold")).pack(pady=20)
        
        ctk.CTkLabel(container, text="New Password").pack(anchor="w", padx=40)
        self.p1 = ctk.CTkEntry(container, width=300, show="*")
        self.p1.pack(padx=40, pady=5)
        
        ctk.CTkLabel(container, text="Confirm New Password").pack(anchor="w", padx=40)
        self.p2 = ctk.CTkEntry(container, width=300, show="*")
        self.p2.pack(padx=40, pady=5)
        
        ctk.CTkButton(container, text="Update Password", fg_color=COLORS['warning'], text_color=COLORS['bg'],
                     height=40, command=self.reset).pack(pady=30, padx=40, fill="x")

    def reset(self):
        p1, p2 = self.p1.get(), self.p2.get()
        if p1 != p2:
            messagebox.showerror("Error", "Passwords do not match.")
            return
        
        success, msg = reset_password(self.user_id, p1)
        if success:
            messagebox.showinfo("Success", msg)
            self.destroy()
        else:
            messagebox.showerror("Error", msg)

class ActivityModal(ctk.CTkToplevel):
    def __init__(self, parent):
        super().__init__(parent)
        self.title("Login Activity")
        self.geometry("800x600")
        self.configure(fg_color=COLORS['bg'])
        self.grab_set()
        
        ctk.CTkLabel(self, text="Recent Login Activity", font=("Segoe UI", 18, "bold")).pack(pady=20)
        
        table_frame = ctk.CTkFrame(self, fg_color=COLORS['card'], corner_radius=15)
        table_frame.pack(fill="both", expand=True, padx=20, pady=(0, 20))
        
        cols = ("ID", "Username", "Time", "Status", "IP Address", "Device")
        tree = ttk.Treeview(table_frame, columns=cols, show="headings")
        for col in cols:
            tree.heading(col, text=col)
            tree.column(col, width=120, anchor="center")
        
        tree.pack(side="left", fill="both", expand=True, padx=10, pady=10)
        sb = ttk.Scrollbar(table_frame, orient="vertical", command=tree.yview)
        tree.configure(yscrollcommand=sb.set)
        sb.pack(side="right", fill="y")
        
        # Load data
        activity = get_login_activity()
        for a in activity:
            tree.insert("", "end", values=a)
