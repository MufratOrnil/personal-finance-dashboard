import tkinter as tk
from tkinter import ttk, messagebox
from tkcalendar import DateEntry
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import pandas as pd
from fpdf import FPDF
import logging
import os

class ReportsTab:
    def __init__(self, app):
        self.app = app
        self.frame = ttk.Frame(self.app.notebook)
        self.app.notebook.add(self.frame, text="Reports")
        self.setup_ui()
        self.refresh()

    def setup_ui(self):
        self.card = ttk.Frame(self.frame, style='Card.TFrame')
        self.card.pack(fill=tk.BOTH, expand=True, padx=12, pady=12)

        filter_frame = ttk.Frame(self.card)
        filter_frame.pack(fill=tk.X, padx=12, pady=12)

        ttk.Label(filter_frame, text="Start Date").pack(side=tk.LEFT, padx=5)
        self.start_date = DateEntry(filter_frame, date_pattern='yyyy-mm-dd')
        self.start_date.pack(side=tk.LEFT, padx=5)

        ttk.Label(filter_frame, text="End Date").pack(side=tk.LEFT, padx=5)
        self.end_date = DateEntry(filter_frame, date_pattern='yyyy-mm-dd')
        self.end_date.pack(side=tk.LEFT, padx=5)

        ttk.Button(filter_frame, text="Generate Report", style='TButton', command=self.generate_report).pack(side=tk.LEFT, padx=5)
        ttk.Button(filter_frame, text="Export to PDF", style='Accent.TButton', command=self.export_to_pdf).pack(side=tk.LEFT, padx=5)

        self.figure, self.ax = plt.subplots(figsize=(8, 4))
        self.canvas = FigureCanvasTkAgg(self.figure, master=self.card)
        self.canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True, padx=12, pady=12)

    def refresh(self):
        try:
            self.generate_report()
        except Exception as e:
            logging.error(f"Failed to refresh reports: {str(e)}")
            messagebox.showerror("Error", f"Failed to refresh reports: {str(e)}")

    def generate_report(self):
        try:
            start_date = self.start_date.get() or "1900-01-01"
            end_date = self.end_date.get() or "9999-12-31"
            self.app.db.cursor.execute('''
                SELECT category, SUM(amount) as total
                FROM transactions
                WHERE date BETWEEN ? AND ?
                GROUP BY category
            ''', (start_date, end_date))
            data = self.app.db.cursor.fetchall()
            if not data:
                self.ax.clear()
                self.ax.text(0.5, 0.5, "No data available", horizontalalignment='center', verticalalignment='center')
                self.canvas.draw()
                return
            df = pd.DataFrame(data, columns=['category', 'total'])
            self.ax.clear()
            df.plot(kind='bar', x='category', y='total', ax=self.ax, color=self.app.colors["primary"])
            self.ax.set_title("Spending by Category")
            self.ax.set_xlabel("Category")
            self.ax.set_ylabel("Total Amount")
            self.canvas.draw()
        except Exception as e:
            logging.error(f"Failed to generate report: {str(e)}")
            messagebox.showerror("Error", f"Failed to generate report: {str(e)}")

    def export_to_pdf(self):
        try:
            start_date = self.start_date.get() or "1900-01-01"
            end_date = self.end_date.get() or "9999-12-31"
            self.app.db.cursor.execute('''
                SELECT date, amount, category, type, description
                FROM transactions
                WHERE date BETWEEN ? AND ?
                ORDER BY date
            ''', (start_date, end_date))
            data = self.app.db.cursor.fetchall()
            if not data:
                messagebox.showinfo("Info", "No transactions to export")
                return
            pdf = FPDF()
            pdf.add_page()
            pdf.set_font("Arial", size=12)
            pdf.cell(200, 10, txt="Personal Finance Report", ln=True, align='C')
            pdf.ln(10)
            pdf.set_font("Arial", size=10)
            for row in data:
                pdf.cell(0, 10, txt=str(row), ln=True)
            output_path = "report.pdf"
            pdf.output(output_path)
            messagebox.showinfo("Success", f"Report exported to {output_path}")
        except Exception as e:
            logging.error(f"Failed to export PDF: {str(e)}")
            messagebox.showerror("Error", f"Failed to export PDF: {str(e)}")