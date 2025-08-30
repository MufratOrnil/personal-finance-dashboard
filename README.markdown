# Personal Finance Dashboard

A comprehensive Tkinter-based application for managing personal finances, developed as part of **SDP-2 (Software Development Project 2)**. This project, built with the assistance of AI tools, offers robust features for tracking transactions, budgeting, setting goals, managing reminders, and generating reports with charts. While functional, it may contain issues as it was created as a learning exercise for SDP-2.

## Features

- **User Authentication**: Secure login and registration with bcrypt hashing.
- **Dashboard**: Overview with motivational quotes, expense breakdowns (pie charts), monthly trends (line charts), recent transactions, and upcoming reminders.
- **Transactions**: Add, view, filter, and delete income/expenses with categories and descriptions.
- **Budget**: Set monthly budgets per category, track actual spending vs. budget, and view progress.
- **Goals**: Create financial goals with targets, categories, and due dates; update progress and edit/delete goals.
- **Reminders**: Manage bill reminders with due dates, amounts, and status (Pending/Paid); filter and edit/delete.
- **Reports**: Generate spending reports by category with bar charts; filter by date range and export to PDF.
- **Responsive UI**: Dynamic resizing, modern styling with Roboto font, and color themes.
- **Data Persistence**: Uses SQLite database (`finance.db`) for storing users, transactions, budgets, goals, and reminders.
- **Additional Utilities**: Motivational quotes, progress bars, currency formatting, and error/success messages.

## Prerequisites

- Python 3.8+ (tested with 3.12.3).
- Required libraries (install via `pip`):

  ```
  pip install tk tkinter tkcalendar matplotlib pandas fpdf bcrypt
  ```
- Roboto font (optional for UI; install on your system if needed).
- No internet access required; all operations are local.

## Installation

1. Clone the repository:

   ```
   git clone https://github.com/MufratOrnil/personal-finance-dashboard.git
   cd personal-finance-dashboard
   ```
2. Install dependencies:

   ```
   pip install -r requirements.txt
   ```

   (Create `requirements.txt` with the libraries listed above if not present.)
3. Run the application:

   ```
   python main.py
   ```

## Usage

1. **Launch the App**: Run `python main.py`. An authentication window will appear.
2. **Register/Login**: Create a new account or log in with existing credentials.
3. **Navigate Tabs**:
   - **Dashboard**: View summaries, charts, and quotes.
   - **Transactions**: Add/filter/delete entries.
   - **Budget**: Set/view monthly budgets.
   - **Goals**: Manage long-term goals.
   - **Reminders**: Set/track bill reminders.
   - **Reports**: Generate charts and PDF exports.
4. **Database**: All data is stored in `finance.db` (created automatically).
5. **Logs**: Errors are logged to `app_errors.log`, `database_errors.log`, and `auth_errors.log`.

## Project Structure

```
personal-finance-dashboard/
├── main.py                # Entry point
├── dashboard.py           # Main app class
├── database.py            # SQLite database handling
├── auth_window.py         # Login/register UI
├── utils.py               # Helper functions
├── dashboard_tab.py       # Dashboard tab logic
├── transactions_tab.py    # Transactions tab logic
├── budget_tab.py          # Budget tab logic
├── goals_tab.py           # Goals tab logic
├── reminders_tab.py       # Reminders tab logic
├── reports_tab.py         # Reports tab logic
├── README.md              # This file
├── .gitignore             # Ignore files 
└── finance.db             # Database 
```

## Notes

- **Project Context**: This application was developed as part of **SDP-2 (Software Development Project 2)**, a learning-focused project. It leverages AI tools for code generation and optimization, which accelerated development but may introduce minor bugs or inefficiencies. Users are encouraged to report issues or suggest improvements.
- **Known Limitations**: As an academic project, it may contain imperfections. Test thoroughly before production use, and consider enhancing error handling or security for real-world applications.

## Troubleshooting

- **Missing Dependencies**: Ensure all libraries are installed. If `tkcalendar` or others fail, reinstall via pip.
- **Database Issues**: If `finance.db` is locked or permissions denied, check file permissions or delete and restart.
- **Charts Not Showing**: Verify Matplotlib and Pandas are installed; test with simple plots.
- **UI Resizing Problems**: The app handles resizing dynamically; test on different window sizes.
- **Date Errors**: Uses `yyyy-mm-dd` format; ensure valid dates are entered.
- **Logs**: Check log files for detailed errors.

## Contributing

1. Fork the repository.
2. Create a feature branch (`git checkout -b feature/new-feature`).
3. Commit changes (`git commit -m "Add new feature"`).
4. Push to the branch (`git push origin feature/new-feature`).
5. Open a pull request. Note that this is an SDP-2 project, so contributions should align with educational goals.

## License

MIT License - Feel free to use, modify, and distribute.

## Acknowledgments

- Built with Tkinter for GUI, SQLite for data storage.
- Charts via Matplotlib and Pandas.
- PDF exports with FPDF.
- Developed for **SDP-2 (Software Development Project 2)** with AI assistance to streamline coding and design.
- Inspired by the need for accessible personal finance tools for students and beginners.