# In budget_tab.py
import tkinter as tk
from tkinter import ttk, messagebox
import logging
import re
from datetime import datetime

class BudgetTab:
    def __init__(self, app):
        self.app = app
        self.frame = ttk.Frame(self.app.notebook)
        self.app.notebook.add(self.frame, text="Budget")
        logging.debug(f"Initializing BudgetTab with current date: {datetime.now()}")
        self.setup_ui()
        self.refresh()

    def setup_ui(self):
        self.card = ttk.Frame(self.frame, style='Card.TFrame')
        self.card.pack(fill=tk.BOTH, expand=True, padx=12, pady=12)

        # Input Frame with Grid Layout
        input_frame = ttk.LabelFrame(self.card, text="Set Budget", style='Card.TFrame')
        input_frame.pack(fill=tk.X, padx=12, pady=12)
        input_frame.columnconfigure(1, weight=1)

        # Month Field
        ttk.Label(input_frame, text="Select Month:*", font=('Roboto', 12), anchor='e').grid(row=0, column=0, padx=(10, 5), pady=5, sticky="e")
        current_year = datetime.now().year
        self.month_var = tk.StringVar(value=datetime.now().strftime('%Y-%m'))
        # Use a list of valid month-year combinations (first day of each month)
        self.month_combo = ttk.Combobox(
            input_frame, 
            textvariable=self.month_var, 
            values=[f"{current_year}-{m:02d}" for m in range(1, 13)],
            width=20, 
            font=('Roboto', 12)
        )
        self.month_combo.grid(row=0, column=1, padx=(5, 10), pady=5, sticky="ew")

        # Category Field
        ttk.Label(input_frame, text="Category:*", font=('Roboto', 12), anchor='e').grid(row=1, column=0, padx=(10, 5), pady=5, sticky="e")
        self.category_combo = ttk.Combobox(
            input_frame, 
            values=["Housing", "Food", "Transport", "Entertainment", "Utilities", "Healthcare"], 
            width=20, 
            font=('Roboto', 12)
        )
        self.category_combo.grid(row=1, column=1, padx=(5, 10), pady=5, sticky="ew")

        # Amount Field
        ttk.Label(input_frame, text="Amount:*", font=('Roboto', 12), anchor='e').grid(row=2, column=0, padx=(10, 5), pady=5, sticky="e")
        self.amount_entry = ttk.Entry(input_frame, width=20, font=('Roboto', 12))
        self.amount_entry.grid(row=2, column=1, padx=(5, 10), pady=5, sticky="ew")

        # Button Frame
        button_frame = ttk.Frame(input_frame)
        button_frame.grid(row=3, column=0, columnspan=2, padx=5, pady=5, sticky="ew")
        button_frame.columnconfigure(0, weight=1)
        button_frame.columnconfigure(1, weight=1)
        button_frame.columnconfigure(2, weight=1)

        ttk.Button(button_frame, text="Set Budget", style='TButton', command=self.set_budget).grid(row=0, column=0, padx=5, pady=5, sticky="ew")
        ttk.Button(button_frame, text="Clear Form", style='TButton', command=self.clear_form).grid(row=0, column=1, padx=5, pady=5, sticky="ew")
        ttk.Button(button_frame, text="Clear Budget", style='Accent.TButton', command=self.clear_budget).grid(row=0, column=2, padx=5, pady=5, sticky="ew")

        # Budget vs Actual Treeview
        self.budget_tree = ttk.Treeview(
            self.card, 
            columns=("Category", "Budget ($)", "Actual ($)", "Difference ($)", "Progress"), 
            show='headings'
        )
        self.budget_tree.heading("Category", text="Category")
        self.budget_tree.heading("Budget ($)", text="Budget ($)")
        self.budget_tree.heading("Actual ($)", text="Actual ($)")
        self.budget_tree.heading("Difference ($)", text="Difference ($)")
        self.budget_tree.heading("Progress", text="Progress")
        self.budget_tree.column("Category", width=120, anchor='center')
        self.budget_tree.column("Budget ($)", width=100, anchor='center')
        self.budget_tree.column("Actual ($)", width=100, anchor='center')
        self.budget_tree.column("Difference ($)", width=100, anchor='center')
        self.budget_tree.column("Progress", width=100, anchor='center')
        self.budget_tree.pack(fill=tk.BOTH, expand=True, padx=12, pady=12)

    def set_budget(self):
        month = self.month_var.get()
        category = self.category_combo.get().strip()
        amount = self.amount_entry.get().strip()
        try:
            if not month or not category or not amount:
                messagebox.showerror("Error", "Please fill in all required fields (*)")
                return
            if not re.match(r'^\d*\.?\d{0,2}$', amount):
                messagebox.showerror("Error", "Please enter a valid number for Amount (e.g., 50, 12.34)")
                return
            amount = float(amount)
            self.app.db.cursor.execute('''
                INSERT OR REPLACE INTO budgets (month, category, amount)
                VALUES (?, ?, ?)
            ''', (month, category, amount))
            self.app.db.conn.commit()
            self.refresh()
            self.clear_form()
            messagebox.showinfo("Success", "Budget set successfully")
        except Exception as e:
            logging.error(f"Failed to set budget: {str(e)}")
            messagebox.showerror("Error", f"Failed to set budget: {str(e)}")

    def clear_form(self):
        self.month_var.set(datetime.now().strftime('%Y-%m'))
        self.category_combo.set("")
        self.amount_entry.delete(0, tk.END)

    def clear_budget(self):
        month = self.month_var.get()
        try:
            self.app.db.cursor.execute('DELETE FROM budgets WHERE month = ?', (month,))
            self.app.db.conn.commit()
            self.refresh()
            messagebox.showinfo("Success", "Budget cleared successfully")
        except Exception as e:
            logging.error(f"Failed to clear budget: {str(e)}")
            messagebox.showerror("Error", f"Failed to clear budget: {str(e)}")

    def refresh(self):
        try:
            for item in self.budget_tree.get_children():
                self.budget_tree.delete(item)
            month = self.month_var.get() or datetime.now().strftime('%Y-%m')
            # Validate month format to avoid day out of range errors
            try:
                datetime.strptime(month + '-01', '%Y-%m-%d')  # Use a safe day (1st)
            except ValueError:
                logging.error(f"Invalid month format: {month}, defaulting to current month")
                month = datetime.now().strftime('%Y-%m')
            self.app.db.cursor.execute('''
                SELECT b.category, b.amount, COALESCE(t.total, 0) as actual
                FROM budgets b
                LEFT JOIN (
                    SELECT category, SUM(amount) as total
                    FROM transactions
                    WHERE strftime('%Y-%m', date) = ?
                    AND type = 'Expense'
                    GROUP BY category
                ) t ON b.category = t.category
                WHERE b.month = ?
            ''', (month, month))
            for row in self.app.db.cursor.fetchall():
                category, budget, actual = row
                difference = budget - actual
                progress = f"{(actual / budget * 100):.1f}%" if budget > 0 else "N/A"
                self.budget_tree.insert('', tk.END, values=(category, f"{budget:.2f}", f"{actual:.2f}", f"{difference:.2f}", progress))
        except Exception as e:
            logging.error(f"Failed to refresh Budget data: {str(e)}")
            messagebox.showerror("Error", f"Failed to refresh Budget data: {str(e)}")