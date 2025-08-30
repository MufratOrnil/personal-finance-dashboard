import random
from tkinter import ttk

def get_motivational_quote():
    quotes = [
        "The secret to getting ahead is getting started.",
        "Money doesn’t buy happiness, but it buys freedom.",
        "A budget is telling your money where to go instead of wondering where it went.",
        "The goal isn’t more money. The goal is living life on your terms.",
        "Financial freedom is available to those who learn about it and work for it."
    ]
    return random.choice(quotes)

def create_progress_bar(progress, color='#008080'):
    """Create a progress bar widget with specified color."""
    frame = ttk.Frame()
    bar = ttk.Frame(frame, style='Progress.TFrame')
    bar.configure(style='Progress.TFrame', background=color)
    bar.place(relwidth=progress/100, relheight=1.0)
    return frame

def format_currency(amount):
    """Format amount as currency with $ symbol, handling locale-independent formatting."""
    try:
        # Ensure amount is a float and format with 2 decimal places
        return f"${float(amount):,.2f}"
    except (ValueError, TypeError):
        return "$0.00"

def success_message(parent, message):
    """Display a styled success message."""
    label = ttk.Label(
        parent,
        text=f"✔ {message}",
        font=('Roboto', 12, 'bold'),
        foreground='#4CAF50',
        background='#FFFFFF'
    )
    label.pack(pady=5)
    parent.after(3000, label.destroy)

def error_message(parent, message):
    """Display a styled error message."""
    label = ttk.Label(
        parent,
        text=f"❌ {message}",
        font=('Roboto', 12, 'italic'),
        foreground='#F44336',
        background='#FFFFFF'
    )
    label.pack(pady=5)
    parent.after(3000, label.destroy)