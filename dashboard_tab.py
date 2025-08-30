import tkinter as tk
from tkinter import ttk
from datetime import datetime
from utils import get_motivational_quote, success_message, error_message
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

class DashboardTab:
    def __init__(self, app, username):
        self.app = app
        self.username = username
        self.tab = ttk.Frame(self.app.notebook)
        self.app.notebook.add(self.tab, text="Dashboard")
        self.create_widgets()

    def create_widgets(self):
        main_frame = ttk.Frame(self.tab)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=12, pady=12)
        main_frame.columnconfigure(0, weight=1)
        main_frame.rowconfigure(2, weight=1)

        welcome_frame = ttk.Frame(main_frame)
        welcome_frame.grid(row=0, column=0, sticky='ew', padx=12, pady=5)
        ttk.Label(welcome_frame, text=f"Hi, {self.username}!", font=('Roboto', 18, 'bold'), foreground=self.app.colors["primary"]).pack(anchor='w')

        quote_frame = ttk.LabelFrame(main_frame, text="Inspiration 💡", style='Card.TFrame')
        quote_frame.grid(row=1, column=0, sticky='ew', padx=12, pady=5)
        self.quote_label = ttk.Label(
            quote_frame, 
            text="", 
            font=('Roboto', 14, 'italic'), 
            wraplength=800, 
            anchor='center',
            style='Quote.TLabel'
        )
        self.quote_label.pack(pady=8, fill=tk.X)
        self.tab.after(0, self.fade_in_quote)
        self.update_quote()

        charts_frame = ttk.Frame(main_frame)
        charts_frame.grid(row=2, column=0, sticky='nsew', padx=12, pady=5)
        charts_frame.columnconfigure(0, weight=1)
        charts_frame.columnconfigure(1, weight=1)

        self.pie_frame = ttk.LabelFrame(charts_frame, text="Expense Breakdown 📈", style='Card.TFrame')
        self.pie_frame.grid(row=0, column=0, sticky='nsew', padx=5, pady=5)

        self.line_frame = ttk.LabelFrame(charts_frame, text="Monthly Trends 📅", style='Card.TFrame')
        self.line_frame.grid(row=0, column=1, sticky='nsew', padx=5, pady=5)

        recent_frame = ttk.LabelFrame(main_frame, text="Recent Transactions 📋", style='Card.TFrame')
        recent_frame.grid(row=3, column=0, sticky='ew', padx=12, pady=5)
        columns = ("date", "amount", "category", "type", "description")
        self.recent_transactions_tree = ttk.Treeview(
            recent_frame, columns=columns, show="headings", height=5
        )
        for col in columns:
            self.recent_transactions_tree.heading(col, text=col.capitalize())
            self.recent_transactions_tree.column(col, width=120, anchor='center', stretch=True)
        self.recent_transactions_tree.pack(fill=tk.X, expand=True, padx=5, pady=5)

        reminders_frame = ttk.LabelFrame(main_frame, text="Upcoming Reminders ⏰", style='Card.TFrame')
        reminders_frame.grid(row=4, column=0, sticky='ew', padx=12, pady=5)
        rem_columns = ("name", "due_date", "amount", "status")
        self.reminders_tree = ttk.Treeview(
            reminders_frame, columns=rem_columns, show="headings", height=5
        )
        self.reminders_tree.heading("name", text="Name")
        self.reminders_tree.heading("due_date", text="Due Date")
        self.reminders_tree.heading("amount", text="Amount")
        self.reminders_tree.heading("status", text="Status")
        self.reminders_tree.column("name", width=150, anchor='center', stretch=True)
        self.reminders_tree.column("due_date", width=120, anchor='center', stretch=True)
        self.reminders_tree.column("amount", width=120, anchor='center', stretch=True)
        self.reminders_tree.column("status", width=120, anchor='center', stretch=True)
        self.reminders_tree.pack(fill=tk.X, expand=True, padx=5, pady=5)
        self.reminders_tree.tag_configure('overdue', background=self.app.colors["danger"], foreground='#FFFFFF')

    def fade_in_quote(self):
        self.quote_label.configure(foreground=self.app.colors["accent"])

    def update_quote(self):
        quote = get_motivational_quote()
        self.quote_label.config(text=quote)
        self.tab.after(10000, self.update_quote)

    def refresh(self):
        for widget in self.pie_frame.winfo_children():
            if isinstance(widget, ttk.Label) or isinstance(widget, tk.Canvas):
                widget.destroy()
        for widget in self.line_frame.winfo_children():
            if isinstance(widget, ttk.Label) or isinstance(widget, tk.Canvas):
                widget.destroy()

        for item in self.recent_transactions_tree.get_children():
            self.recent_transactions_tree.delete(item)
        self.app.db.cursor.execute('''
            SELECT date, amount, category, type, description 
            FROM transactions 
            ORDER BY date DESC 
            LIMIT 5
        ''')
        for trans in self.app.db.cursor.fetchall():
            self.recent_transactions_tree.insert("", tk.END, values=trans)

        for item in self.reminders_tree.get_children():
            self.reminders_tree.delete(item)
        today = datetime.now().date().strftime("%Y-%m-%d")
        self.app.db.cursor.execute('''
            SELECT name, due_date, amount, 
                   CASE WHEN paid=1 THEN 'Paid' ELSE 'Pending' END as status
            FROM reminders
            WHERE due_date >= ? OR paid=0
            ORDER BY due_date
            LIMIT 5
        ''', (today,))
        for rem in self.app.db.cursor.fetchall():
            name, due_date, amount, status = rem
            due_date_obj = datetime.strptime(due_date, "%Y-%m-%d").date()
            tag = 'overdue' if status == 'Pending' and due_date_obj <= datetime.now().date() else ''
            self.reminders_tree.insert("", tk.END, values=(name, due_date, f"${amount:,.2f}", status), tags=(tag,))

        self.update_expense_chart()
        self.update_trend_chart()

    def update_expense_chart(self):
        self.app.db.cursor.execute('''
            SELECT category, SUM(amount) 
            FROM transactions 
            WHERE type='Expense' 
            GROUP BY category
            HAVING SUM(amount) > 0
        ''')
        expense_data = self.app.db.cursor.fetchall()
        if not expense_data:
            ttk.Label(self.pie_frame, text="No expense data available", font=('Roboto', 12), foreground=self.app.colors["text_secondary"]).pack(pady=8)
            return
        categories = [row[0] for row in expense_data]
        amounts = [row[1] for row in expense_data]

        fig, ax = plt.subplots(figsize=(4, 3))
        ax.pie(
            amounts, 
            labels=categories, 
            colors=[self.app.colors["primary"], self.app.colors["accent"], self.app.colors["secondary"], self.app.colors["success"]],
            textprops={'fontfamily': 'Roboto', 'fontsize': 10, 'color': self.app.colors["text_primary"]}
        )
        ax.set_title("Expense Distribution", fontfamily='Roboto', fontsize=12, fontweight='bold', color=self.app.colors["text_primary"])
        fig.patch.set_facecolor(self.app.colors["bg_panel"])
        canvas = FigureCanvasTkAgg(fig, master=self.pie_frame)
        canvas.draw()
        canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        plt.close(fig)

    def update_trend_chart(self):
        self.app.db.cursor.execute('''
            SELECT strftime('%Y-%m', date) as month, 
                   SUM(CASE WHEN type='Income' THEN amount ELSE 0 END) as income,
                   SUM(CASE WHEN type='Expense' THEN amount ELSE 0 END) as expense
            FROM transactions
            GROUP BY month
            ORDER BY month
        ''')
        trend_data = self.app.db.cursor.fetchall()
        if len(trend_data) < 2:
            ttk.Label(self.line_frame, text="Not enough data for trends", font=('Roboto', 12), foreground=self.app.colors["text_secondary"]).pack(pady=8)
            return
        months = [row[0] for row in trend_data]
        income = [row[1] for row in trend_data]
        expense = [row[2] for row in trend_data]

        fig, ax = plt.subplots(figsize=(4, 3))
        ax.plot(months, income, label="Income", color=self.app.colors["success"], linewidth=2)
        ax.plot(months, expense, label="Expense", color=self.app.colors["danger"], linewidth=2)
        ax.set_xlabel("Month", fontfamily='Roboto', fontsize=10, color=self.app.colors["text_primary"])
        ax.set_ylabel("Amount ($)", fontfamily='Roboto', fontsize=10, color=self.app.colors["text_primary"])
        ax.set_title("Monthly Trends", fontfamily='Roboto', fontsize=12, fontweight='bold', color=self.app.colors["text_primary"])
        ax.legend(prop={'family': 'Roboto', 'size': 10})
        ax.grid(True, color=self.app.colors["border"])
        ax.set_facecolor(self.app.colors["bg_panel"])
        fig.patch.set_facecolor(self.app.colors["bg_panel"])
        for label in ax.get_xticklabels() + ax.get_yticklabels():
            label.set_fontfamily('Roboto')
            label.set_fontsize(10)
            label.set_color(self.app.colors["text_primary"])
        canvas = FigureCanvasTkAgg(fig, master=self.line_frame)
        canvas.draw()
        canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        plt.close(fig)