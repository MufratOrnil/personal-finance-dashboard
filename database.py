import sqlite3
import bcrypt
import logging
import os

# Setup logging for database errors
logging.basicConfig(
    filename='database_errors.log',
    level=logging.DEBUG,  # Changed to DEBUG for detailed migration logs
    format='%(asctime)s - %(levelname)s - %(message)s'
)

class Database:
    def __init__(self, db_name):
        try:
            # Check if directory is writable
            db_dir = os.path.dirname(os.path.abspath(db_name))
            if not os.access(db_dir, os.W_OK):
                raise PermissionError(f"Directory {db_dir} is not writable. Please ensure the application has write permissions.")
            self.conn = sqlite3.connect(db_name)
            self.conn.execute("PRAGMA foreign_keys = ON")  # Enable foreign key support
            self.cursor = self.conn.cursor()
            self.create_tables()
            self.migrate_schema()
            logging.info("Database initialized successfully")
        except Exception as e:
            logging.error(f"Failed to initialize database: {str(e)}")
            raise

    def create_tables(self):
        try:
            self.cursor.execute('''
                CREATE TABLE IF NOT EXISTS users (
                    username TEXT PRIMARY KEY,
                    password BLOB NOT NULL
                )
            ''')
            logging.debug("Created users table")
            self.cursor.execute('''
                CREATE TABLE IF NOT EXISTS transactions (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    date TEXT NOT NULL,
                    amount REAL NOT NULL,
                    category TEXT NOT NULL,
                    type TEXT NOT NULL CHECK(type IN ('Income', 'Expense', 'Savings')),
                    description TEXT
                )
            ''')
            logging.debug("Created transactions table")
            self.cursor.execute('''
                CREATE TABLE IF NOT EXISTS budgets (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    category TEXT NOT NULL,
                    amount REAL NOT NULL,
                    month TEXT NOT NULL
                )
            ''')
            logging.debug("Created budgets table")
            self.cursor.execute('''
                CREATE TABLE IF NOT EXISTS goals (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT NOT NULL UNIQUE,
                    amount REAL NOT NULL,
                    category TEXT NOT NULL,
                    target_date TEXT NOT NULL
                )
            ''')
            logging.debug("Created goals table")
            self.cursor.execute('''
                CREATE TABLE IF NOT EXISTS reminders (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT NOT NULL,
                    amount REAL NOT NULL,
                    category TEXT NOT NULL,
                    due_date TEXT NOT NULL,
                    paid INTEGER NOT NULL
                )
            ''')
            logging.debug("Created reminders table")
            self.conn.commit()
        except Exception as e:
            logging.error(f"Failed to create tables: {str(e)}")
            raise

    def migrate_schema(self):
        try:
            # Check if 'reminders' table exists
            self.cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='reminders'")
            if not self.cursor.fetchone():
                logging.debug("Reminders table does not exist; will be created by create_tables")
                return

            # Check columns in reminders table
            self.cursor.execute("PRAGMA table_info(reminders)")
            columns = [info[1] for info in self.cursor.fetchall()]
            logging.debug(f"Reminders table columns: {columns}")

            if 'category' not in columns:
                logging.info("Adding category column to reminders table")
                try:
                    self.cursor.execute('''
                        ALTER TABLE reminders ADD COLUMN category TEXT NOT NULL DEFAULT 'General'
                    ''')
                    self.conn.commit()
                    logging.info("Successfully added category column to reminders table")
                except sqlite3.OperationalError as e:
                    logging.error(f"Failed to add category column: {str(e)}")
                    # Fallback: Recreate reminders table if ALTER fails (e.g., locked database)
                    self.cursor.execute('''
                        CREATE TABLE reminders_new (
                            id INTEGER PRIMARY KEY AUTOINCREMENT,
                            name TEXT NOT NULL,
                            amount REAL NOT NULL,
                            category TEXT NOT NULL,
                            due_date TEXT NOT NULL,
                            paid INTEGER NOT NULL
                        )
                    ''')
                    self.cursor.execute('''
                        INSERT INTO reminders_new (id, name, amount, due_date, paid)
                        SELECT id, name, amount, due_date, paid FROM reminders
                    ''')
                    self.cursor.execute('''
                        UPDATE reminders_new SET category = 'General' WHERE category IS NULL
                    ''')
                    self.cursor.execute('DROP TABLE reminders')
                    self.cursor.execute('ALTER TABLE reminders_new RENAME TO reminders')
                    self.conn.commit()
                    logging.info("Recreated reminders table with category column")
            else:
                logging.debug("Category column already exists in reminders table")
        except Exception as e:
            logging.error(f"Failed to migrate schema: {str(e)}")
            raise

    def register_user(self, username, password):
        try:
            hashed = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
            self.cursor.execute('INSERT INTO users (username, password) VALUES (?, ?)', (username, hashed))
            self.conn.commit()
            return True
        except sqlite3.IntegrityError:
            logging.error(f"Username {username} already exists")
            return False
        except Exception as e:
            logging.error(f"Registration error: {str(e)}")
            return False

    def login_user(self, username, password):
        try:
            self.cursor.execute('SELECT password FROM users WHERE username = ?', (username,))
            result = self.cursor.fetchone()
            if result:
                stored_hash = result[0]
                if not isinstance(stored_hash, bytes) or not stored_hash.startswith(b'$2b$'):
                    logging.error(f"Invalid hash format for {username}")
                    return False
                return bcrypt.checkpw(password.encode('utf-8'), stored_hash)
            logging.error(f"No user found for {username}")
            return False
        except ValueError as e:
            logging.error(f"Password validation error for {username}: {str(e)}")
            return False
        except Exception as e:
            logging.error(f"Login error for {username}: {str(e)}")
            return False

    def close(self):
        try:
            self.conn.close()
        except Exception as e:
            logging.error(f"Failed to close database: {str(e)}")