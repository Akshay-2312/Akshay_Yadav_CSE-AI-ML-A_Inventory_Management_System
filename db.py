# db.py
import sqlite3

def get_connection():
    return sqlite3.connect("db/store.db")

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
            supplier_id INTEGER
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

if __name__ == "__main__":
    initialize_db()
