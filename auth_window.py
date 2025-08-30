import tkinter as tk
from tkinter import ttk, messagebox
import logging
import traceback

# Setup logging
logging.basicConfig(
    filename='auth_errors.log',
    level=logging.ERROR,
    format='%(asctime)s - %(levelname)s - %(username)s - %(message)s'
)

class AuthWindow:
    def __init__(self, app):
        self.app = app
        self.root = tk.Toplevel(self.app.root)
        self.root.title("Login - Personal Finance Dashboard")
        self.root.geometry("450x600")
        self.colors = self.app.colors
        self.root.configure(bg=self.colors["bg_main"])
        self.root.resizable(False, False)
        self.setup_ui()
        self.app.root.withdraw()
        self.root.protocol("WM_DELETE_WINDOW", self.on_close)

    def setup_ui(self):
        main_frame = tk.Frame(self.root, bg=self.colors["bg_main"])
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        self.card = tk.Frame(
            main_frame, 
            bg=self.colors["bg_panel"], 
            bd=0, 
            highlightthickness=1,
            highlightbackground=self.colors["border"]
        )
        self.card.place(relx=0.5, rely=0.5, anchor="center", width=400, height=520)
        
        title_frame = tk.Frame(self.card, bg=self.colors["bg_panel"])
        title_frame.pack(fill=tk.X, pady=(50, 5))
        
        title = tk.Label(
            title_frame, 
            text="Personal Finance", 
            font=("Roboto", 24, "bold"), 
            fg=self.colors["primary"], 
            bg=self.colors["bg_panel"]
        )
        title.pack()
        
        title2 = tk.Label(
            title_frame, 
            text="Dashboard", 
            font=("Roboto", 24, "bold"), 
            fg=self.colors["primary"], 
            bg=self.colors["bg_panel"]
        )
        title2.pack()
        
        subtitle = tk.Label(
            self.card, 
            text="Welcome back! Please log in.",
            font=("Roboto", 12), 
            fg=self.colors["text_secondary"], 
            bg=self.colors["bg_panel"]
        )
        subtitle.pack(pady=(5, 30))
        
        username_label = tk.Label(
            self.card, 
            text="Username", 
            font=("Roboto", 12), 
            fg=self.colors["text_primary"], 
            bg=self.colors["bg_panel"],
            anchor="w"
        )
        username_label.pack(fill=tk.X, padx=30, anchor="w")
        
        self.username_entry = tk.Entry(
            self.card, 
            font=("Roboto", 12),
            bd=1, 
            relief=tk.SOLID,
            highlightthickness=1,
            highlightbackground=self.colors["border"],
            highlightcolor=self.colors["primary"]
        )
        self.username_entry.pack(fill=tk.X, padx=30, pady=(5, 20), ipady=8)
        self.username_entry.focus()
        
        password_label = tk.Label(
            self.card, 
            text="Password", 
            font=("Roboto", 12), 
            fg=self.colors["text_primary"], 
            bg=self.colors["bg_panel"],
            anchor="w"
        )
        password_label.pack(fill=tk.X, padx=30, anchor="w")
        
        self.password_entry = tk.Entry(
            self.card, 
            font=("Roboto", 12),
            bd=1, 
            relief=tk.SOLID, 
            show="*",
            highlightthickness=1,
            highlightbackground=self.colors["border"],
            highlightcolor=self.colors["primary"]
        )
        self.password_entry.pack(fill=tk.X, padx=30, pady=(5, 10), ipady=8)
        
        self.show_password_var = tk.BooleanVar(value=False)
        show_pass_frame = tk.Frame(self.card, bg=self.colors["bg_panel"])
        show_pass_frame.pack(fill=tk.X, padx=30, anchor="w", pady=(0, 30))
        
        show_pass_cb = ttk.Checkbutton(
            show_pass_frame, 
            text="Show Password",
            variable=self.show_password_var,
            command=self.toggle_password,
            style='TCheckbutton'
        )
        show_pass_cb.pack(anchor="w")
        
        btn_frame = tk.Frame(self.card, bg=self.colors["bg_panel"])
        btn_frame.pack(fill=tk.X, padx=30, pady=(0, 40))
        
        login_btn = ttk.Button(
            btn_frame, 
            text="Login", 
            command=self.login, 
            style='TButton'
        )
        login_btn.pack(side=tk.LEFT, fill=tk.X, expand=True, ipady=10)
        
        tk.Frame(btn_frame, width=15, bg=self.colors["bg_panel"]).pack(side=tk.LEFT)
        
        register_btn = ttk.Button(
            btn_frame, 
            text="Register", 
            command=self.register,
            style='Accent.TButton'
        )
        register_btn.pack(side=tk.LEFT, fill=tk.X, expand=True, ipady=10)
    
    def toggle_password(self):
        if self.show_password_var.get():
            self.password_entry.config(show="")
        else:
            self.password_entry.config(show="*")
    
    def login(self):
        username = self.username_entry.get().strip()
        password = self.password_entry.get().strip()
        if not username or not password:
            messagebox.showerror("Error", "Please enter both username and password")
            return
        try:
            if self.app.db.login_user(username, password):
                messagebox.showinfo("Success", f"Welcome back, {username}!")
                self.app.set_user(username)
                self.root.destroy()
                self.app.root.deiconify()
            else:
                logging.error("Invalid username or password", extra={'username': username})
                messagebox.showerror("Error", "Invalid username or password")
        except Exception as e:
            logging.error(f"Login failed: {str(e)}\n{traceback.format_exc()}", extra={'username': username})
            messagebox.showerror("Error", f"Login failed: {str(e)}")

    def register(self):
        username = self.username_entry.get().strip()
        password = self.password_entry.get().strip()
        if not username or not password:
            messagebox.showerror("Error", "Please enter both username and password")
            return
        if len(password) < 6:
            messagebox.showerror("Error", "Password must be at least 6 characters")
            return
        try:
            if self.app.db.register_user(username, password):
                messagebox.showinfo("Success", "Registration successful! Please login.")
                self.username_entry.delete(0, tk.END)
                self.password_entry.delete(0, tk.END)
                self.show_password_var.set(False)
                self.toggle_password()
            else:
                logging.error("Username already exists", extra={'username': username})
                messagebox.showerror("Error", "Username already exists")
        except Exception as e:
            logging.error(f"Registration failed: {str(e)}\n{traceback.format_exc()}", extra={'username': username})
            messagebox.showerror("Error", f"Registration failed: {str(e)}")
    
    def on_close(self):
        try:
            self.app.db.close()
        except Exception as e:
            logging.error(f"Failed to close database: {str(e)}\n{traceback.format_exc()}", extra={'username': 'unknown'})
        self.root.destroy()
        self.app.root.destroy()