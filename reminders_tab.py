import tkinter as tk
from tkinter import ttk, messagebox
from tkcalendar import DateEntry
import logging
import re
from datetime import datetime

class RemindersTab:
    def __init__(self, app):
        self.app = app
        self.frame = ttk.Frame(self.app.notebook)
        self.app.notebook.add(self.frame, text="Reminders")
        self.setup_ui()
        self.check_and_update_schema()  # Ensure schema is updated
        try:
            self.refresh()
        except Exception as e:
            logging.error(f"Failed to initialize Reminders tab: {str(e)}")
            messagebox.showerror("Error", f"Failed to load Reminders tab: {str(e)}. Please ensure the database is accessible and schema is updated.")

    def setup_ui(self):
        self.card = ttk.Frame(self.frame, style='Card.TFrame')
        self.card.pack(fill=tk.BOTH, expand=True, padx=12, pady=12)

        # Input Frame with Grid Layout
        input_frame = ttk.LabelFrame(self.card, text="Add Reminder", style='Card.TFrame')
        input_frame.pack(fill=tk.X, padx=12, pady=12)
        input_frame.columnconfigure(1, weight=1)

        # Name Field
        ttk.Label(input_frame, text="Name:*", font=('Roboto', 12), anchor='e').grid(row=0, column=0, padx=(10, 5), pady=5, sticky="e")
        self.name_entry = ttk.Entry(input_frame, width=20, font=('Roboto', 12))
        self.name_entry.grid(row=0, column=1, padx=(5, 10), pady=5, sticky="ew")

        # Amount Field
        ttk.Label(input_frame, text="Amount:*", font=('Roboto', 12), anchor='e').grid(row=1, column=0, padx=(10, 5), pady=5, sticky="e")
        self.amount_entry = ttk.Entry(input_frame, width=20, font=('Roboto', 12))
        self.amount_entry.grid(row=1, column=1, padx=(5, 10), pady=5, sticky="ew")

        # Category Field
        ttk.Label(input_frame, text="Category:*", font=('Roboto', 12), anchor='e').grid(row=2, column=0, padx=(10, 5), pady=5, sticky="e")
        self.category_combo = ttk.Combobox(
            input_frame, 
            values=["Housing", "Food", "Transport", "Entertainment", "Utilities", "Healthcare"], 
            width=20, 
            font=('Roboto', 12)
        )
        self.category_combo.grid(row=2, column=1, padx=(5, 10), pady=5, sticky="ew")

        # Due Date Field
        ttk.Label(input_frame, text="Due Date:*", font=('Roboto', 12), anchor='e').grid(row=3, column=0, padx=(10, 5), pady=5, sticky="e")
        self.due_date = DateEntry(
            input_frame, 
            date_pattern='yyyy-mm-dd', 
            width=20, 
            font=('Roboto', 12), 
            selectbackground=self.app.colors["secondary"]
        )
        self.due_date.set_date(datetime.now())
        self.due_date.grid(row=3, column=1, padx=(5, 10), pady=5, sticky="ew")

        # Status Field
        ttk.Label(input_frame, text="Status:*", font=('Roboto', 12), anchor='e').grid(row=4, column=0, padx=(10, 5), pady=5, sticky="e")
        self.status_combo = ttk.Combobox(
            input_frame, 
            values=["Pending", "Paid"], 
            width=20, 
            font=('Roboto', 12)
        )
        self.status_combo.set("Pending")  # Default to Pending
        self.status_combo.grid(row=4, column=1, padx=(5, 10), pady=5, sticky="ew")

        # Button Frame
        button_frame = ttk.Frame(input_frame)
        button_frame.grid(row=5, column=0, columnspan=2, padx=5, pady=5, sticky="ew")
        button_frame.columnconfigure(0, weight=1)
        button_frame.columnconfigure(1, weight=1)
        button_frame.columnconfigure(2, weight=1)

        ttk.Button(button_frame, text="Add Reminder", style='TButton', command=self.add_reminder).grid(row=0, column=0, padx=5, pady=5, sticky="ew")
        ttk.Button(button_frame, text="Clear Form", style='TButton', command=self.clear_form).grid(row=0, column=1, padx=5, pady=5, sticky="ew")
        ttk.Button(button_frame, text="Delete Reminder", style='Accent.TButton', command=self.delete_reminder).grid(row=0, column=2, padx=5, pady=5, sticky="ew")

        # Filter Frame
        filter_frame = ttk.LabelFrame(self.card, text="Filter Reminders", style='Card.TFrame')
        filter_frame.pack(fill=tk.X, padx=12, pady=5)

        ttk.Label(filter_frame, text="Start Date:*", font=('Roboto', 12)).pack(side=tk.LEFT, padx=5)
        self.start_date = DateEntry(
            filter_frame, 
            date_pattern='yyyy-mm-dd', 
            width=12, 
            font=('Roboto', 12), 
            selectbackground=self.app.colors["secondary"]
        )
        self.start_date.set_date(datetime.now())
        self.start_date.pack(side=tk.LEFT, padx=5)

        ttk.Label(filter_frame, text="End Date:*", font=('Roboto', 12)).pack(side=tk.LEFT, padx=5)
        self.end_date = DateEntry(
            filter_frame, 
            date_pattern='yyyy-mm-dd', 
            width=12, 
            font=('Roboto', 12), 
            selectbackground=self.app.colors["secondary"]
        )
        self.end_date.set_date(datetime.now())
        self.end_date.pack(side=tk.LEFT, padx=5)

        ttk.Button(filter_frame, text="Apply Filter", style='TButton', command=self.refresh).pack(side=tk.LEFT, padx=5)
        ttk.Button(filter_frame, text="Clear Filters", style='Accent.TButton', command=self.clear_filters).pack(side=tk.LEFT, padx=5)

        # Reminders Treeview
        self.reminders_tree = ttk.Treeview(
            self.card, 
            columns=("Name", "Amount ($)", "Category", "Due Date", "Status"), 
            show='headings'
        )
        self.reminders_tree.heading("Name", text="Name")
        self.reminders_tree.heading("Amount ($)", text="Amount ($)")
        self.reminders_tree.heading("Category", text="Category")
        self.reminders_tree.heading("Due Date", text="Due Date")
        self.reminders_tree.heading("Status", text="Status")
        self.reminders_tree.column("Name", width=120, anchor='center')
        self.reminders_tree.column("Amount ($)", width=100, anchor='center')
        self.reminders_tree.column("Category", width=120, anchor='center')
        self.reminders_tree.column("Due Date", width=100, anchor='center')
        self.reminders_tree.column("Status", width=100, anchor='center')
        self.reminders_tree.pack(fill=tk.BOTH, expand=True, padx=12, pady=12)

    def check_and_update_schema(self):
        try:
            cursor = self.app.db.cursor
            cursor.execute('PRAGMA table_info(reminders)')
            columns = [row[1] for row in cursor.fetchall()]
            if 'status' not in columns:
                cursor.execute('ALTER TABLE reminders ADD COLUMN status TEXT DEFAULT "Pending"')
                self.app.db.conn.commit()
                logging.info("Added 'status' column to reminders table")
            if 'paid' not in columns:
                cursor.execute('ALTER TABLE reminders ADD COLUMN paid INTEGER DEFAULT 0')
                self.app.db.conn.commit()
                logging.info("Added 'paid' column to reminders table")
                # Migrate status to paid
                cursor.execute("UPDATE reminders SET paid = (CASE WHEN status = 'Paid' THEN 1 ELSE 0 END)")
                self.app.db.conn.commit()
                logging.info("Migrated status to paid column")
        except Exception as e:
            logging.error(f"Failed to update reminders table schema: {str(e)}")
            messagebox.showerror("Error", f"Failed to update database schema: {str(e)}. Please check the database connection.")

    def add_reminder(self):
        name = self.name_entry.get().strip()
        amount = self.amount_entry.get().strip()
        category = self.category_combo.get().strip()
        due_date = self.due_date.get().strip()
        status = self.status_combo.get().strip()
        try:
            if not name or not amount or not category or not due_date or not status:
                messagebox.showerror("Error", "Please fill in all required fields (*)")
                return
            if not re.match(r'^\d*\.?\d{0,2}$', amount):
                messagebox.showerror("Error", "Please enter a valid number for Amount (e.g., 50, 12.34)")
                return
            amount = float(amount)
            try:
                datetime.strptime(due_date, '%Y-%m-%d')
            except ValueError:
                messagebox.showerror("Error", "Please select a valid Due Date (yyyy-mm-dd)")
                return
            if status not in ["Pending", "Paid"]:
                messagebox.showerror("Error", "Status must be either Pending or Paid")
                return
            paid = 1 if status == "Paid" else 0
            self.app.db.cursor.execute('''
                INSERT INTO reminders (name, amount, category, due_date, status, paid)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (name, amount, category, due_date, status, paid))
            self.app.db.conn.commit()
            self.refresh()
            self.clear_form()
            messagebox.showinfo("Success", "Reminder added successfully")
        except Exception as e:
            logging.error(f"Failed to add reminder: {str(e)}")
            messagebox.showerror("Error", f"Failed to add reminder: {str(e)}")

    def delete_reminder(self):
        selected = self.reminders_tree.selection()
        if not selected:
            messagebox.showerror("Error", "Please select a reminder to delete")
            return
        try:
            item = self.reminders_tree.item(selected[0])
            reminder_id = item['tags'][0] if item['tags'] else None
            if not reminder_id:
                messagebox.showerror("Error", "Unable to determine reminder ID")
                return
            self.app.db.cursor.execute('DELETE FROM reminders WHERE id = ?', (reminder_id,))
            if self.app.db.cursor.rowcount == 0:
                messagebox.showerror("Error", "Reminder not found in database")
                return
            self.app.db.conn.commit()
            self.refresh()
            messagebox.showinfo("Success", "Reminder deleted successfully")
        except Exception as e:
            logging.error(f"Failed to delete reminder: {str(e)}")
            messagebox.showerror("Error", f"Failed to delete reminder: {str(e)}")

    def clear_filters(self):
        self.start_date.set_date(datetime.now())
        self.end_date.set_date(datetime.now())
        self.refresh()

    def refresh(self):
        try:
            for item in self.reminders_tree.get_children():
                self.reminders_tree.delete(item)
            start_date = self.start_date.get() or "1900-01-01"
            end_date = self.end_date.get() or "9999-12-31"
            self.app.db.cursor.execute('''
                SELECT id, name, amount, category, due_date, status
                FROM reminders
                WHERE due_date BETWEEN ? AND ?
                ORDER BY due_date DESC
            ''', (start_date, end_date))
            for row in self.app.db.cursor.fetchall():
                id_, name, amount, category, due_date, status = row
                self.reminders_tree.insert('', tk.END, values=(name, f"{amount:.2f}", category, due_date, status), tags=(str(id_),))
        except Exception as e:
            logging.error(f"Failed to refresh reminders: {str(e)}")
            messagebox.showerror("Error", f"Failed to refresh reminders: {str(e)}")

    def clear_form(self):
        self.name_entry.delete(0, tk.END)
        self.amount_entry.delete(0, tk.END)
        self.category_combo.set("")
        self.due_date.set_date(datetime.now())
        self.status_combo.set("Pending")