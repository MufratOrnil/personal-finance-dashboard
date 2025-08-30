import tkinter as tk
from tkinter import ttk, messagebox
from tkcalendar import DateEntry
import logging
import re
from datetime import datetime

class TransactionsTab:
    def __init__(self, app):
        self.app = app
        self.frame = ttk.Frame(self.app.notebook)
        self.app.notebook.add(self.frame, text="Transactions")
        self.setup_ui()
        self.refresh()

    def setup_ui(self):
        self.card = ttk.Frame(self.frame, style='Card.TFrame')
        self.card.pack(fill=tk.BOTH, expand=True, padx=12, pady=12)

        # Input Frame with Grid Layout
        input_frame = ttk.LabelFrame(self.card, text="Add Transaction", style='Card.TFrame')
        input_frame.pack(fill=tk.X, padx=12, pady=12)
        input_frame.columnconfigure(1, weight=1)  # Allow entry fields to expand
        input_frame.columnconfigure(3, weight=1)

        # Date Field
        ttk.Label(input_frame, text="Date:*", font=('Roboto', 12), anchor='e').grid(row=0, column=0, padx=(10, 5), pady=5, sticky="e")
        self.date_entry = DateEntry(
            input_frame, 
            date_pattern='yyyy-mm-dd', 
            width=20, 
            font=('Roboto', 12), 
            selectbackground=self.app.colors["secondary"],
            state='normal'  # Ensure the widget is editable
        )
        self.date_entry.set_date(datetime.now())  # Set default to today's date
        self.date_entry.grid(row=0, column=1, padx=(5, 10), pady=5, sticky="ew")

        # Amount Field
        ttk.Label(input_frame, text="Amount:*", font=('Roboto', 12), anchor='e').grid(row=0, column=2, padx=(10, 5), pady=5, sticky="e")
        self.amount_entry = ttk.Entry(input_frame, width=20, font=('Roboto', 12))
        self.amount_entry.grid(row=0, column=3, padx=(5, 10), pady=5, sticky="ew")

        # Category Field
        ttk.Label(input_frame, text="Category:*", font=('Roboto', 12), anchor='e').grid(row=1, column=0, padx=(10, 5), pady=5, sticky="e")
        self.category_combo = ttk.Combobox(
            input_frame, 
            values=["Housing", "Food", "Transport", "Entertainment", "Utilities", "Healthcare"], 
            width=20, 
            font=('Roboto', 12)
        )
        self.category_combo.grid(row=1, column=1, padx=(5, 10), pady=5, sticky="ew")

        # Type Field
        ttk.Label(input_frame, text="Type:*", font=('Roboto', 12), anchor='e').grid(row=1, column=2, padx=(10, 5), pady=5, sticky="e")
        self.type_combo = ttk.Combobox(
            input_frame, 
            values=["Income", "Expense"], 
            width=20, 
            font=('Roboto', 12)
        )
        self.type_combo.grid(row=1, column=3, padx=(5, 10), pady=5, sticky="ew")

        # Description Field
        ttk.Label(input_frame, text="Description:", font=('Roboto', 12), anchor='e').grid(row=2, column=0, padx=(10, 5), pady=5, sticky="e")
        self.desc_entry = ttk.Entry(input_frame, font=('Roboto', 12))
        self.desc_entry.grid(row=2, column=1, columnspan=3, padx=(5, 10), pady=5, sticky="ew")

        # Button Frame
        button_frame = ttk.Frame(self.card)
        button_frame.pack(fill=tk.X, padx=12, pady=5)
        button_frame.columnconfigure(0, weight=1)
        button_frame.columnconfigure(1, weight=1)

        ttk.Button(button_frame, text="Add Transaction", style='TButton', command=self.add_transaction).grid(row=0, column=0, padx=5, pady=5, sticky="ew")
        ttk.Button(button_frame, text="Delete Transaction", style='Accent.TButton', command=self.delete_transaction).grid(row=0, column=1, padx=5, pady=5, sticky="ew")

        # Filter Frame
        filter_frame = ttk.LabelFrame(self.card, text="Filter Transactions", style='Card.TFrame')
        filter_frame.pack(fill=tk.X, padx=12, pady=5)

        ttk.Label(filter_frame, text="Start Date:", font=('Roboto', 12)).pack(side=tk.LEFT, padx=5)
        self.start_date = DateEntry(
            filter_frame, 
            date_pattern='yyyy-mm-dd', 
            width=12, 
            font=('Roboto', 12), 
            selectbackground=self.app.colors["secondary"]
        )
        self.start_date.pack(side=tk.LEFT, padx=5)

        ttk.Label(filter_frame, text="End Date:", font=('Roboto', 12)).pack(side=tk.LEFT, padx=5)
        self.end_date = DateEntry(
            filter_frame, 
            date_pattern='yyyy-mm-dd', 
            width=12, 
            font=('Roboto', 12), 
            selectbackground=self.app.colors["secondary"]
        )
        self.end_date.pack(side=tk.LEFT, padx=5)

        ttk.Button(filter_frame, text="Apply Filter", style='TButton', command=self.refresh).pack(side=tk.LEFT, padx=5)
        ttk.Button(filter_frame, text="Clear Filters", style='Accent.TButton', command=self.clear_filters).pack(side=tk.LEFT, padx=5)

        # Transactions Treeview
        self.transactions_tree = ttk.Treeview(
            self.card, 
            columns=("Date", "Amount", "Category", "Type", "Description"), 
            show='headings'
        )
        self.transactions_tree.heading("Date", text="Date")
        self.transactions_tree.heading("Amount", text="Amount")
        self.transactions_tree.heading("Category", text="Category")
        self.transactions_tree.heading("Type", text="Type")
        self.transactions_tree.heading("Description", text="Description")
        self.transactions_tree.column("Date", width=120, anchor='center')
        self.transactions_tree.column("Amount", width=100, anchor='center')
        self.transactions_tree.column("Category", width=120, anchor='center')
        self.transactions_tree.column("Type", width=100, anchor='center')
        self.transactions_tree.column("Description", width=200, anchor='center')
        self.transactions_tree.pack(fill=tk.BOTH, expand=True, padx=12, pady=12)

    def add_transaction(self):
        date = self.date_entry.get().strip()
        amount = self.amount_entry.get().strip()
        category = self.category_combo.get().strip()
        type_ = self.type_combo.get().strip()
        description = self.desc_entry.get().strip()
        try:
            # Log date input for debugging
            logging.debug(f"Date input: '{date}'")
            # Validate date
            if not date:
                messagebox.showerror("Error", "Please select a date")
                return
            try:
                # Ensure date is in yyyy-mm-dd format
                parsed_date = datetime.strptime(date, '%Y-%m-%d')
                date = parsed_date.strftime('%Y-%m-%d')  # Normalize format
            except ValueError as e:
                logging.error(f"Invalid date format: {date}, Error: {str(e)}")
                messagebox.showerror("Error", "Please select a valid date (yyyy-mm-dd)")
                return

            # Validate amount
            if not amount:
                messagebox.showerror("Error", "Amount cannot be empty")
                return
            logging.debug(f"Amount input: {amount}")
            if not re.match(r'^-?\d*\.?\d{0,2}$', amount):
                messagebox.showerror("Error", "Please enter a valid number for Amount (e.g., 50, 12.34, -10.50, .34)")
                return
            try:
                amount = float(amount)
                if '.' in str(amount) and len(str(amount).split('.')[-1]) > 2:
                    messagebox.showerror("Error", "Amount cannot have more than 2 decimal places")
                    return
            except ValueError as e:
                logging.error(f"Failed to convert amount to float: {amount}, Error: {str(e)}")
                messagebox.showerror("Error", "Please enter a valid number for Amount")
                return

            # Validate other required fields
            if not category or not type_:
                messagebox.showerror("Error", "Please fill in all required fields (*)")
                return

            self.app.db.cursor.execute('''
                INSERT INTO transactions (date, amount, category, type, description)
                VALUES (?, ?, ?, ?, ?)
            ''', (date, amount, category, type_, description))
            self.app.db.conn.commit()
            self.refresh()
            self.clear_inputs()
            messagebox.showinfo("Success", "Transaction added successfully")
        except Exception as e:
            logging.error(f"Failed to add transaction: {str(e)}")
            messagebox.showerror("Error", f"Failed to add transaction: {str(e)}")

    def delete_transaction(self):
        selected = self.transactions_tree.selection()
        if not selected:
            messagebox.showerror("Error", "Please select a transaction to delete")
            return
        try:
            item = self.transactions_tree.item(selected[0])
            transaction_id = item['tags'][0] if item['tags'] else None
            if not transaction_id:
                messagebox.showerror("Error", "Unable to determine transaction ID")
                return
            self.app.db.cursor.execute('DELETE FROM transactions WHERE id = ?', (transaction_id,))
            if self.app.db.cursor.rowcount == 0:
                messagebox.showerror("Error", "Transaction not found in database")
                return
            self.app.db.conn.commit()
            self.refresh()
            messagebox.showinfo("Success", "Transaction deleted successfully")
        except Exception as e:
            logging.error(f"Failed to delete transaction: {str(e)}")
            messagebox.showerror("Error", f"Failed to delete transaction: {str(e)}")

    def clear_filters(self):
        self.start_date.set_date("")
        self.end_date.set_date("")
        self.refresh()

    def refresh(self):
        try:
            for item in self.transactions_tree.get_children():
                self.transactions_tree.delete(item)
            start_date = self.start_date.get() or "1900-01-01"
            end_date = self.end_date.get() or "9999-12-31"
            self.app.db.cursor.execute('''
                SELECT id, date, amount, category, type, description
                FROM transactions
                WHERE date BETWEEN ? AND ?
                ORDER BY date DESC
            ''', (start_date, end_date))
            for row in self.app.db.cursor.fetchall():
                id_, date, amount, category, type_, description = row
                self.transactions_tree.insert('', tk.END, values=(date, amount, category, type_, description), tags=(str(id_),))
        except Exception as e:
            logging.error(f"Failed to refresh transactions: {str(e)}")
            messagebox.showerror("Error", f"Failed to refresh transactions: {str(e)}")

    def clear_inputs(self):
        self.date_entry.set_date(datetime.now())  # Reset to today's date
        self.amount_entry.delete(0, tk.END)
        self.category_combo.set("")
        self.type_combo.set("")
        self.desc_entry.delete(0, tk.END)