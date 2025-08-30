import tkinter as tk
from tkinter import ttk, messagebox
from tkcalendar import DateEntry
import logging
from datetime import datetime

class GoalsTab:
    def __init__(self, app):
        self.app = app
        self.frame = ttk.Frame(self.app.notebook)
        self.app.notebook.add(self.frame, text="Goals")
        logging.debug("Initializing GoalsTab")
        self.setup_ui()
        self.check_and_update_schema()
        try:
            logging.debug("Attempting to refresh Goals tab")
            self.refresh()
        except Exception as e:
            logging.error(f"Failed to initialize Goals tab: {str(e)}")
            messagebox.showerror("Error", f"Failed to load Goals tab: {str(e)}. Please ensure the database is accessible and schema is updated.")

    def setup_ui(self):
        self.card = ttk.Frame(self.frame, style='Card.TFrame')
        self.card.pack(fill=tk.BOTH, expand=True, padx=12, pady=12)
        logging.debug("Created card frame for GoalsTab")

        # Input Frame with Grid Layout
        input_frame = ttk.LabelFrame(self.card, text="Set Goal", style='Card.TFrame')
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

        # Target Date Field
        ttk.Label(input_frame, text="Target Date:*", font=('Roboto', 12), anchor='e').grid(row=3, column=0, padx=(10, 5), pady=5, sticky="e")
        self.target_date = DateEntry(
            input_frame,
            date_pattern='yyyy-mm-dd',
            width=20,
            font=('Roboto', 12),
            selectbackground=self.app.colors["secondary"]
        )
        self.target_date.set_date(datetime.now())
        self.target_date.grid(row=3, column=1, padx=(5, 10), pady=5, sticky="ew")

        # Button Frame
        button_frame = ttk.Frame(input_frame)
        button_frame.grid(row=4, column=0, columnspan=2, padx=5, pady=5, sticky="ew")
        button_frame.columnconfigure(0, weight=1)
        button_frame.columnconfigure(1, weight=1)
        button_frame.columnconfigure(2, weight=1)
        button_frame.columnconfigure(3, weight=1)

        ttk.Button(button_frame, text="Add Goal", style='TButton', command=self.add_goal).grid(row=0, column=0, padx=5, pady=5, sticky="ew")
        ttk.Button(button_frame, text="Clear Form", style='TButton', command=self.clear_form).grid(row=0, column=1, padx=5, pady=5, sticky="ew")
        ttk.Button(button_frame, text="Delete Goal", style='Accent.TButton', command=self.delete_goal).grid(row=0, column=2, padx=5, pady=5, sticky="ew")
        ttk.Button(button_frame, text="Update Goal", style='TButton', command=self.update_goal).grid(row=0, column=3, padx=5, pady=5, sticky="ew")

        # Goals Treeview
        self.goals_tree = ttk.Treeview(
            self.card,
            columns=("Name", "Goal Amount ($)", "Category", "Target Date", "Progress"),
            show='headings',
            style='Treeview'
        )
        self.goals_tree.heading("Name", text="Name")
        self.goals_tree.heading("Goal Amount ($)", text="Goal Amount ($)")
        self.goals_tree.heading("Category", text="Category")
        self.goals_tree.heading("Target Date", text="Target Date")
        self.goals_tree.heading("Progress", text="Progress")
        self.goals_tree.column("Name", width=120, anchor='center')
        self.goals_tree.column("Goal Amount ($)", width=100, anchor='center')
        self.goals_tree.column("Category", width=120, anchor='center')
        self.goals_tree.column("Target Date", width=100, anchor='center')
        self.goals_tree.column("Progress", width=100, anchor='center')
        self.goals_tree.pack(fill=tk.BOTH, expand=True, padx=12, pady=12)
        logging.debug("Created goals_tree in GoalsTab")

        # Progress Bar Frame
        self.progress_frame = ttk.Frame(self.card, style='Card.TFrame')
        self.progress_frame.pack(fill=tk.X, padx=12, pady=5)
        self.progress_label = ttk.Label(self.progress_frame, text="Goal Progress", font=('Roboto', 12))
        self.progress_label.pack(side=tk.LEFT, padx=5)
        self.progress_bar = ttk.Progressbar(self.progress_frame, orient=tk.HORIZONTAL, length=200, mode='determinate', style='Progress.TFrame')
        self.progress_bar.pack(side=tk.LEFT, padx=5)
        logging.debug("Created progress_bar in GoalsTab")

    def check_and_update_schema(self):
        try:
            cursor = self.app.db.cursor
            cursor.execute('PRAGMA table_info(goals)')
            columns = [row[1] for row in cursor.fetchall()]
            if 'progress' not in columns:
                cursor.execute('ALTER TABLE goals ADD COLUMN progress REAL DEFAULT 0.0')
                self.app.db.conn.commit()
                logging.info("Added 'progress' column to goals table")
        except Exception as e:
            logging.error(f"Failed to update goals table schema: {str(e)}")
            messagebox.showerror("Error", f"Failed to update database schema: {str(e)}. Please check the database connection.")

    def add_goal(self):
        name = self.name_entry.get().strip()
        amount = self.amount_entry.get().strip()
        category = self.category_combo.get().strip()
        target_date = self.target_date.get().strip()
        try:
            if not name or not amount or not category or not target_date:
                messagebox.showerror("Error", "Please fill in all required fields (*)")
                return
            if not amount.replace('.', '').isdigit() or float(amount) <= 0:
                messagebox.showerror("Error", "Please enter a valid positive number for Amount")
                return
            try:
                datetime.strptime(target_date, '%Y-%m-%d')
            except ValueError:
                messagebox.showerror("Error", "Please select a valid Target Date (yyyy-mm-dd)")
                return
            amount = float(amount)
            self.app.db.cursor.execute('''
                INSERT INTO goals (name, amount, category, target_date, progress)
                VALUES (?, ?, ?, ?, ?)
            ''', (name, amount, category, target_date, 0.0))
            self.app.db.conn.commit()
            logging.debug(f"Added goal: {name}, {amount}, {category}, {target_date}")
            self.refresh()
            self.clear_form()
            messagebox.showinfo("Success", "Goal added successfully")
        except Exception as e:
            logging.error(f"Failed to add goal: {str(e)}")
            messagebox.showerror("Error", f"Failed to add goal: {str(e)}")

    def delete_goal(self):
        selected = self.goals_tree.selection()
        if not selected:
            messagebox.showerror("Error", "Please select a goal to delete")
            return
        try:
            item = self.goals_tree.item(selected[0])
            goal_id = item['tags'][0] if item['tags'] else None
            if not goal_id:
                messagebox.showerror("Error", "Unable to determine goal ID")
                return
            self.app.db.cursor.execute('DELETE FROM goals WHERE id = ?', (goal_id,))
            if self.app.db.cursor.rowcount == 0:
                messagebox.showerror("Error", "Goal not found in database")
                return
            self.app.db.conn.commit()
            self.refresh()
            messagebox.showinfo("Success", "Goal deleted successfully")
        except Exception as e:
            logging.error(f"Failed to delete goal: {str(e)}")
            messagebox.showerror("Error", f"Failed to delete goal: {str(e)}")

    def update_goal(self):
        selected = self.goals_tree.selection()
        if not selected:
            messagebox.showerror("Error", "Please select a goal to update")
            return
        try:
            item = self.goals_tree.item(selected[0])
            goal_id = item['tags'][0] if item['tags'] else None
            if not goal_id:
                messagebox.showerror("Error", "Unable to determine goal ID")
                return
            self.app.db.cursor.execute('''
                SELECT name, amount, category, target_date, progress
                FROM goals WHERE id = ?
            ''', (goal_id,))
            goal_data = self.app.db.cursor.fetchone()
            if not goal_data:
                messagebox.showerror("Error", "Goal not found in database")
                return
            name, amount, category, target_date, progress = goal_data

            # Populate form with current values
            self.name_entry.delete(0, tk.END)
            self.name_entry.insert(0, name)
            self.amount_entry.delete(0, tk.END)
            self.amount_entry.insert(0, str(amount))
            self.category_combo.set(category)
            self.target_date.set_date(target_date)

            # Create a new window for updating
            update_window = tk.Toplevel(self.frame)
            update_window.title("Update Goal")
            update_window.geometry("300x250")
            update_window.transient(self.frame)
            update_window.grab_set()

            # Paid Amount Field
            ttk.Label(update_window, text="Paid Amount (if any):", font=('Roboto', 12)).pack(pady=5)
            paid_amount_entry = ttk.Entry(update_window, width=20, font=('Roboto', 12))
            paid_amount_entry.pack(pady=5)

            # Save button
            def save_update():
                new_name = self.name_entry.get().strip()
                new_category = self.category_combo.get().strip()
                new_target_date = self.target_date.get().strip()
                paid_amount = paid_amount_entry.get().strip()
                try:
                    # Validate non-amount fields
                    if not new_name or not new_category or not new_target_date:
                        messagebox.showerror("Error", "Please fill in all required fields (*)")
                        return
                    try:
                        datetime.strptime(new_target_date, '%Y-%m-%d')  # Fixed date format
                    except ValueError:
                        messagebox.showerror("Error", "Please select a valid Target Date (yyyy-mm-dd)")
                        return

                    # Handle amount update based on paid amount
                    new_amount = amount  # Default to current amount
                    new_progress = progress
                    if paid_amount:
                        if not paid_amount.replace('.', '').isdigit() or float(paid_amount) <= 0:
                            messagebox.showerror("Error", "Please enter a valid positive number for Paid Amount")
                            return
                        paid_amount = float(paid_amount)
                        if paid_amount > amount:
                            messagebox.showerror("Error", "Paid Amount cannot exceed the goal amount")
                            return
                        new_amount = amount - paid_amount  # Reduce goal amount by paid amount
                        new_progress = ((amount - new_amount) / amount) * 100 if amount > 0 else 0.0

                    self.app.db.cursor.execute('''
                        UPDATE goals SET name = ?, amount = ?, category = ?, target_date = ?, progress = ?
                        WHERE id = ?
                    ''', (new_name, new_amount, new_category, new_target_date, new_progress, goal_id))
                    self.app.db.conn.commit()
                    logging.debug(f"Updated goal {goal_id}: {new_name}, {new_amount}, {new_category}, {new_target_date}, progress: {new_progress}%")
                    self.refresh()
                    self.clear_form()
                    update_window.destroy()
                    messagebox.showinfo("Success", "Goal updated successfully")
                except Exception as e:
                    logging.error(f"Failed to update goal: {str(e)}")
                    messagebox.showerror("Error", f"Failed to update goal: {str(e)}")

            ttk.Button(update_window, text="Save Changes", style='TButton', command=save_update).pack(pady=10)
        except Exception as e:
            logging.error(f"Failed to prepare goal update: {str(e)}")
            messagebox.showerror("Error", f"Failed to prepare goal update: {str(e)}")

    def refresh(self):
        try:
            logging.debug("Starting refresh of Goals tab")
            for item in self.goals_tree.get_children():
                self.goals_tree.delete(item)
            self.app.db.cursor.execute('''
                SELECT id, name, amount, category, target_date, progress
                FROM goals
                ORDER BY target_date DESC
            ''')
            for row in self.app.db.cursor.fetchall():
                id_, name, amount, category, target_date, progress = row
                self.goals_tree.insert('', tk.END, values=(name, f"{amount:.2f}", category, target_date, f"{progress:.0f}%"), tags=(str(id_),))
            logging.debug("Updated goals_tree with database data")

            # Update progress bar (average progress of all goals)
            self.app.db.cursor.execute('SELECT AVG(progress) FROM goals')
            avg_progress = self.app.db.cursor.fetchone()[0] or 0.0
            self.progress_bar['value'] = min(max(avg_progress, 0), 100)
            logging.debug(f"Updated progress_bar with value: {avg_progress:.0f}%")
        except Exception as e:
            logging.error(f"Failed to refresh Goals data: {str(e)}")
            messagebox.showwarning("Warning", f"Failed to refresh Goals data: {str(e)}")

    def clear_form(self):
        """Clear all input fields in the Goals tab."""
        logging.debug("Clearing form in GoalsTab")
        self.name_entry.delete(0, tk.END)
        self.amount_entry.delete(0, tk.END)
        self.category_combo.set("")
        self.target_date.set_date(datetime.now())