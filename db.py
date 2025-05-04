# db.py
import sqlite3
import os
import sys
import datetime # Added for expiry date calculations

def get_connection():
    """ Get a connection to the SQLite database. Handles script and bundled exe paths. """
    if hasattr(sys, '_MEIPASS'):
        # Running in a PyInstaller bundle
        # Assume 'db/store.db' was added relative to the bundle root using --add-data db;db
        base_path = sys._MEIPASS
        db_path = os.path.join(base_path, "db", "store.db")
    else:
        # Running as a normal script
        # Construct path relative to this file's directory (db.py)
        script_dir = os.path.dirname(os.path.abspath(__file__)) # Directory containing db.py
        db_path = os.path.join(script_dir, "db", "store.db") # Path to db/store.db relative to script_dir

    try:
        # print(f"Attempting to connect to DB at: {db_path}") # Optional: Add for debugging
        conn = sqlite3.connect(db_path)
        return conn
    except sqlite3.OperationalError as e:
        print(f"!!! Critical Error: Could not connect to database at {db_path}")
        print(f"!!! Error details: {e}")
        # Depending on application structure, might want to show an error dialog or exit
        # For now, re-raise to make the failure clear upstream.
        raise e # Re-raise the specific error

def initialize_db():
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS medicines (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT,
            batch_no TEXT,
            quantity INTEGER,
            price REAL,
            mfg_date TEXT,
            exp_date TEXT,
            supplier_id INTEGER,
            low_stock_threshold INTEGER DEFAULT 5 -- Added for low stock alerts
        )
    ''')

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS employees (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT,
            contact TEXT,
            role TEXT,
            joining_date TEXT,
            salary REAL
        )
    ''')

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS suppliers (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT,
            contact TEXT,
            address TEXT
        )
    ''')

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS sales (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            medicine_id INTEGER,
            quantity_sold INTEGER,
            sale_date TEXT,
            customer_name TEXT
        )
    ''')

    conn.commit()
    conn.close()

# --- Functions for Alerts ---

def get_low_stock_items():
    """Fetches items where quantity is at or below the low stock threshold."""
    conn = get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute('''
            SELECT name, quantity
            FROM inventory -- Changed table from medicines to inventory
            WHERE quantity <= 10 -- Changed condition to use hardcoded threshold 10
        ''')
        items = cursor.fetchall()
        # Convert list of tuples to list of dicts for easier handling (optional)
        # Adjusted to reflect removal of threshold from query
        low_stock_list = [{'name': name, 'quantity': qty}
                          for name, qty in items]
        return low_stock_list
    except sqlite3.Error as e:
        print(f"Database error fetching low stock items: {e}")
        return [] # Return empty list on error
    finally:
        conn.close()

def get_near_expiry_items(days_threshold=30):
    """
    Fetches items expiring within the specified threshold (in days)
    or already expired. Handles TEXT dates in 'YYYY-MM-DD' format.
    """
    conn = get_connection()
    cursor = conn.cursor()
    try:
        # Calculate the date threshold
        threshold_date = (datetime.date.today() + datetime.timedelta(days=days_threshold)).strftime('%Y-%m-%d')
        today_date = datetime.date.today().strftime('%Y-%m-%d')

        # Query items expiring on or before the threshold date,
        # including those already expired (exp_date <= today_date)
        # and those expiring soon (exp_date <= threshold_date)
        # Exclude items with NULL or invalid expiry dates if necessary
        cursor.execute('''
            SELECT name, expiry_date -- Changed column from exp_date to expiry_date
            FROM inventory -- Changed table from medicines to inventory
            WHERE expiry_date IS NOT NULL
              AND expiry_date != ''
              AND date(expiry_date) <= date(?) -- Use date() for comparison, changed column
        ''', (threshold_date,)) # Compare against the future threshold date

        items = cursor.fetchall()
        # Convert list of tuples to list of dicts (optional)
        # Adjusted dictionary key to match column name change
        near_expiry_list = [{'name': name, 'expiry_date': exp} for name, exp in items]
        return near_expiry_list
    except sqlite3.Error as e:
        print(f"Database error fetching near expiry items: {e}")
        return [] # Return empty list on error
    except ValueError as e:
        # Handle potential errors if date conversion fails for some rows
        print(f"Date conversion error fetching near expiry items: {e}")
        return []
    finally:
        conn.close()

# --- End Functions for Alerts ---
# --- Functions for Dashboard Summary ---

def get_total_inventory_value():
    """Calculates the total value of all items in stock (sum of quantity * price)."""
    conn = get_connection()
    cursor = conn.cursor()
    total_value = 0
    try:
        # Assuming 'inventory' table has 'quantity' and 'price' columns
        cursor.execute("SELECT SUM(quantity * price) FROM inventory WHERE quantity > 0")
        result = cursor.fetchone()
        if result and result[0] is not None:
            total_value = result[0]
    except sqlite3.Error as e:
        print(f"Database error calculating total inventory value: {e}")
        # Return 0 or raise error depending on desired handling
    finally:
        conn.close()
    return total_value

def get_todays_sales_value():
    """Calculates the total sales value for today."""
    conn = get_connection()
    cursor = conn.cursor()
    total_sales = 0
    try:
        today_date = datetime.date.today().strftime('%Y-%m-%d')
        # Join sales with inventory to get the price for each sold item
        # Assumes 'sales' has 'medicine_id', 'quantity_sold', 'sale_date'
        # Assumes 'inventory' has 'id' and 'price'
        # Note: This uses the *current* price from inventory. For historical accuracy,
        # the price at the time of sale should ideally be stored in the sales table.
        cursor.execute("""
            SELECT SUM(s.quantity_sold * i.price)
            FROM sales s
            JOIN inventory i ON s.medicine_id = i.id
            WHERE date(s.sale_date) = date(?)
        """, (today_date,))
        result = cursor.fetchone()
        if result and result[0] is not None:
            total_sales = result[0]
    except sqlite3.Error as e:
        print(f"Database error calculating today's sales value: {e}")
    finally:
        conn.close()
    return total_sales

# --- End Functions for Dashboard Summary ---


if __name__ == "__main__":
    initialize_db()
    print("Database initialized.")
    # Example usage (optional, for testing)
    # print("\nLow Stock Items:")
    # print(get_low_stock_items())
    # print("\nNear Expiry Items (within 60 days):")
    # print(get_near_expiry_items(days_threshold=60))
