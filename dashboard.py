import tkinter as tk
from tkinter import ttk, messagebox
from database import Database
from dashboard_tab import DashboardTab
from transactions_tab import TransactionsTab
from budget_tab import BudgetTab
from reports_tab import ReportsTab
from reminders_tab import RemindersTab
from goals_tab import GoalsTab
import logging

class PersonalFinanceDashboard:
    def __init__(self, root):
        self.root = root
        self.root.title("Personal Finance Dashboard")
        try:
            self.db = Database('finance.db')
            logging.debug("Database initialized successfully in PersonalFinanceDashboard")
        except Exception as e:
            logging.error(f"Database connection failed: {str(e)}")
            messagebox.showerror("Error", f"Failed to connect to database: {str(e)}")
            self.root.destroy()
            return
        self.current_user = None
        self.tabs_initialized = False
        self.setup_styles()
        self.root.withdraw()
        self.root.minsize(600, 400)
        self.root.bind('<Configure>', self.on_resize)  # Bind the resize event
        self.root.configure(bg='#F5F7FA')

    def setup_styles(self):
        self.style = ttk.Style()
        self.colors = {
            "primary": "#00796B",
            "secondary": "#004D40",
            "accent": "#26A69A",
            "bg_main": "#F5F7FA",
            "bg_panel": "#FFFFFF",
            "border": "#E0E0E0",
            "success": "#4CAF50",
            "warning": "#FFC107",
            "danger": "#F44336",
            "text_primary": "#212121",
            "text_secondary": "#757575",
            "hover": "#B2DFDB",
            "icon_bg": "#E0F7FA"
        }

        # Force style refresh
        self.style.theme_use('default')

        # General frame and background
        self.style.configure('TFrame', background=self.colors["bg_main"])
        self.style.configure('TLabel', background=self.colors["bg_main"], font=('Roboto', 12), foreground=self.colors["text_primary"])

        # Primary button style (blue-green)
        self.style.configure('TButton', 
            font=('Roboto', 12, 'bold'), 
            padding=12, 
            background=self.colors["primary"], 
            foreground='#FFFFFF', 
            borderwidth=0, 
            relief='flat',
            highlightthickness=2,
            highlightbackground=self.colors["border"],
            highlightcolor=self.colors["hover"]
        )
        self.style.map('TButton', 
            background=[('active', self.colors["secondary"]), ('disabled', '#B0BEC5'), ('!disabled', self.colors["primary"]), ('hover', self.colors["hover"])],
            foreground=[('active', '#FFFFFF'), ('disabled', '#78909C')],
            highlightcolor=[('hover', self.colors["hover"])]
        )

        # Accent button style (lighter teal)
        self.style.configure('Accent.TButton', 
            font=('Roboto', 12, 'bold'), 
            padding=12, 
            background=self.colors["accent"], 
            foreground='#FFFFFF', 
            borderwidth=0, 
            relief='flat',
            highlightthickness=2,
            highlightbackground=self.colors["border"],
            highlightcolor=self.colors["hover"]
        )
        self.style.map('Accent.TButton', 
            background=[('active', self.colors["secondary"]), ('disabled', '#B0BEC5'), ('!disabled', self.colors["accent"]), ('hover', self.colors["hover"])],
            foreground=[('active', '#FFFFFF'), ('disabled', '#78909C')],
            highlightcolor=[('hover', self.colors["hover"])]
        )

        # Notebook and tab styles
        self.style.configure('TNotebook', background=self.colors["bg_main"], padding=12)
        self.style.configure('TNotebook.Tab', 
            font=('Roboto', 12, 'bold'), 
            padding=[12, 6], 
            background=self.colors["bg_panel"], 
            foreground=self.colors["text_primary"]
        )
        self.style.map('TNotebook.Tab', 
            background=[('selected', self.colors["primary"]), ('active', self.colors["secondary"])],
            foreground=[('selected', '#FFFFFF'), ('active', '#FFFFFF')]
        )

        # Card frame for panels
        self.style.configure('Card.TFrame', 
            background=self.colors["bg_panel"], 
            relief='flat', 
            borderwidth=1, 
            highlightbackground=self.colors["border"], 
            highlightthickness=1
        )

        # Quote label
        self.style.configure('Quote.TLabel', 
            background=self.colors["bg_panel"], 
            padding=10, 
            font=('Roboto', 14, 'italic'), 
            foreground=self.colors["accent"]
        )

        # Treeview for tables
        self.style.configure('Treeview', 
            font=('Roboto', 11), 
            rowheight=25, 
            background=self.colors["bg_panel"], 
            foreground=self.colors["text_primary"]
        )
        self.style.configure('Treeview.Heading', 
            font=('Roboto', 12, 'bold'), 
            background=self.colors["primary"], 
            foreground='#FFFFFF'
        )
        self.style.map('Treeview', 
            background=[('selected', self.colors["hover"])]
        )
        self.style.map('Treeview.Heading', 
            background=[('active', self.colors["secondary"])]
        )

        # Entry and Combobox
        self.style.configure('TEntry', 
            font=('Roboto', 12), 
            padding=6,
            relief='flat',
            highlightthickness=1,
            highlightbackground=self.colors["border"],
            highlightcolor=self.colors["primary"]
        )
        self.style.configure('TCombobox', 
            font=('Roboto', 12), 
            padding=6
        )
        self.style.map('TCombobox', 
            fieldbackground=[('readonly', self.colors["bg_panel"])],
            selectbackground=[('readonly', self.colors["bg_panel"])]
        )

        # Checkbutton
        self.style.configure('TCheckbutton', 
            font=('Roboto', 12), 
            background=self.colors["bg_main"], 
            foreground=self.colors["text_primary"]
        )

        # Progress bar
        self.style.configure('Progress.TFrame', 
            background=self.colors["primary"]
        )

        # Ensure styles are applied to all existing widgets
        self.root.update()

    def initialize_tabs(self):
        if self.tabs_initialized:
            logging.debug("Tabs already initialized, skipping")
            return
        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(fill=tk.BOTH, expand=True, padx=12, pady=12)
        try:
            logging.debug("Starting tab initialization")
            self.dashboard_tab = DashboardTab(self, self.current_user)
            logging.debug("DashboardTab instantiated")
            self.transactions_tab = TransactionsTab(self)
            logging.debug("TransactionsTab instantiated")
            self.budget_tab = BudgetTab(self)
            logging.debug("BudgetTab instantiated")
            self.reports_tab = ReportsTab(self)
            logging.debug("ReportsTab instantiated")
            self.reminders_tab = RemindersTab(self)
            logging.debug("RemindersTab instantiated")
            self.goals_tab = GoalsTab(self)
            logging.debug("GoalsTab instantiated")
            self.tabs_initialized = True
            self.refresh_data()
            if hasattr(self.reminders_tab, 'check_reminders'):
                logging.debug("Calling check_reminders")
                self.reminders_tab.check_reminders()
            else:
                logging.warning("check_reminders method not found in RemindersTab")
        except Exception as e:
            logging.error(f"Failed to initialize tabs: {str(e)}", exc_info=True)
            messagebox.showerror("Error", f"Failed to initialize tabs: {str(e)}. Please check logs and restart the application if needed.")
            return

    def set_user(self, username):
        self.current_user = username
        logging.debug(f"Setting user: {username}")
        self.initialize_tabs()
        if self.root.winfo_exists():
            self.root.deiconify()
        else:
            logging.error("Root window already destroyed in set_user")

    def refresh_data(self):
        if not self.tabs_initialized:
            logging.debug("Tabs not initialized, skipping refresh_data")
            return
        try:
            for tab_name, tab in [
                ("Dashboard", self.dashboard_tab),
                ("Transactions", self.transactions_tab),
                ("Budget", self.budget_tab),
                ("Reports", self.reports_tab),
                ("Reminders", self.reminders_tab),
                ("Goals", self.goals_tab)
            ]:
                try:
                    tab.refresh()
                except Exception as e:
                    logging.error(f"Failed to refresh {tab_name} tab: {str(e)}")
                    messagebox.showwarning("Warning", f"Failed to refresh {tab_name} data: {str(e)}")
        except Exception as e:
            logging.error(f"Unexpected error in refresh_data: {str(e)}")
            messagebox.showerror("Error", f"Failed to refresh data: {str(e)}")

    def on_resize(self, event):
        """Handle window resize to adjust font sizes and padding dynamically."""
        try:
            width = self.root.winfo_width()
            font_size = 12 if width >= 800 else 10
            button_padding = 12 if width >= 800 else 10
            self.style.configure('TLabel', font=('Roboto', font_size))
            self.style.configure('TButton', 
                font=('Roboto', font_size, 'bold'), 
                padding=button_padding
            )
            self.style.configure('Accent.TButton', 
                font=('Roboto', font_size, 'bold'), 
                padding=button_padding
            )
            self.style.configure('Treeview', font=('Roboto', font_size - 1))
            self.style.configure('Treeview.Heading', font=('Roboto', font_size, 'bold'))
            self.style.configure('TEntry', font=('Roboto', font_size))
            self.style.configure('TCombobox', font=('Roboto', font_size))
            logging.debug(f"Resized window to width: {width}, font_size: {font_size}")
        except Exception as e:
            logging.error(f"Error in on_resize: {str(e)}")

    def on_close(self):
        try:
            self.db.close()
            logging.debug("Database closed successfully")
        except Exception as e:
            logging.error(f"Failed to close database: {str(e)}")
        if self.root.winfo_exists():
            self.root.destroy()
            logging.debug("Root window destroyed in on_close")