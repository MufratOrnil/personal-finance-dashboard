import tkinter as tk
from dashboard import PersonalFinanceDashboard
from auth_window import AuthWindow
import logging
import sys

# Check for required dependencies
try:
    import tkcalendar
    import matplotlib
    import pandas
    import fpdf
    import bcrypt
except ImportError as e:
    print(f"Missing dependency: {e.name}. Please install it using 'pip install {e.name.lower()}'")
    sys.exit(1)

# Setup logging for initialization errors
logging.basicConfig(
    filename='app_errors.log',
    level=logging.ERROR,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

if __name__ == "__main__":
    try:
        root = tk.Tk()
        app = PersonalFinanceDashboard(root)
        auth = AuthWindow(app)
        root.mainloop()
    except Exception as e:
        logging.error(f"Application initialization failed: {str(e)}")
        raise