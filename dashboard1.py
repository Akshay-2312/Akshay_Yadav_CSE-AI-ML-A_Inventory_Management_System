import tkinter as tk
from tkinter import ttk
import mysql.connector

class Dashboard:
    def __init__(self, root):
        self.root = root
        self.root.title("Dashboard - D R Medical Store")
        self.root.geometry("600x400")

        self.connection = mysql.connector.connect(
            host="localhost",
            user="root",
            password="",
            database="drmedical"
        )

        # Title
        title = tk.Label(root, text="Dashboard", font=("Arial", 24, "bold"))
        title.pack(pady=10)

        # Treeview for Stats
        columns = ("Item", "Value")
        self.tree = ttk.Treeview(root, columns=columns, show="headings")
        for col in columns:
            self.tree.heading(col, text=col)
        self.tree.pack(fill="both", expand=True)

        self.load_data()

    def load_data(self):
        cursor = self.connection.cursor()

        cursor.execute("SELECT COUNT(*) FROM inventory")
        total_meds = cursor.fetchone()[0]

        cursor.execute("SELECT COUNT(*) FROM employees")
        total_emps = cursor.fetchone()[0]

        cursor.execute("SELECT COUNT(*) FROM inventory WHERE quantity < 10")
        low_stock = cursor.fetchone()[0]

        cursor.execute("SELECT COUNT(*) FROM inventory WHERE expiry_date <= DATE_ADD(CURDATE(), INTERVAL 30 DAY)")
        expiring_soon = cursor.fetchone()[0]

        cursor.execute("SELECT SUM(amount) FROM sales WHERE DATE(sale_date) = CURDATE()")
        today_sales = cursor.fetchone()[0]
        today_sales = today_sales if today_sales else 0

        # Insert into tree
        stats = [
            ("Total Medicines", total_meds),
            ("Total Employees", total_emps),
            ("Low Stock Alerts", low_stock),
            ("Expiring Medicines Soon", expiring_soon),
            ("Today's Sales", f"₹{today_sales}")
        ]

        for stat in stats:
            self.tree.insert("", tk.END, values=stat)

        cursor.close()

# For testing separately:
if __name__ == "__main__":
    root = tk.Tk()
    obj = Dashboard(root)
    root.mainloop()
