import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import sqlite3
import csv
import os  # Import the os module
from fpdf import FPDF
from db import get_low_stock_items, get_near_expiry_items

# --- Standalone Report Functions ---

def show_low_stock_report(parent_root): # Added parent_root argument
    low_stock_items = get_low_stock_items()
    # Use parent_root to associate the Toplevel window correctly
    report_window = tk.Toplevel(parent_root)
    report_window.title("Low Stock Report")
    report_window.geometry("600x400")
    report_window.resizable(True, True)
    report_window.configure(bg="#f0f4f7")
    report_window.transient(parent_root) # Make it transient to the window that called it
    report_window.grab_set() # Grab focus

    if low_stock_items:
        columns = ("Item Name", "Current Quantity", "Low Stock Threshold")
        tree = ttk.Treeview(report_window, columns=columns, show="headings")
        for col in columns:
            tree.heading(col, text=col)
            tree.column(col, width=150, anchor=tk.CENTER)
        tree.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        for item in low_stock_items:
            # Assuming get_low_stock_items returns tuples like (name, quantity, threshold)
            tree.insert("", tk.END, values=item)
    else:
        message_label = tk.Label(report_window, text="No items are currently low on stock.", font=("Helvetica", 12), bg="#f0f4f7", fg="#34495e")
        message_label.pack(pady=20)

def show_expiry_report(parent_root): # Added parent_root argument
    near_expiry_items = get_near_expiry_items()
    # Use parent_root to associate the Toplevel window correctly
    report_window = tk.Toplevel(parent_root)
    report_window.title("Expiry Alert Report")
    report_window.geometry("600x400")
    report_window.resizable(True, True)
    report_window.configure(bg="#f0f4f7")
    report_window.transient(parent_root) # Make it transient
    report_window.grab_set() # Grab focus

    if near_expiry_items:
        columns = ("Item Name", "Expiry Date")
        tree = ttk.Treeview(report_window, columns=columns, show="headings")
        for col in columns:
            tree.heading(col, text=col)
            tree.column(col, width=200, anchor=tk.CENTER)
        tree.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        for item in near_expiry_items:
            # Assuming get_near_expiry_items returns tuples like (name, expiry_date)
            tree.insert("", tk.END, values=item)
    else:
        message_label = tk.Label(report_window, text="No items are nearing expiry or expired.", font=("Helvetica", 12), bg="#f0f4f7", fg="#34495e")
        message_label.pack(pady=20)

# Added a back button to return to the dashboard
class ReportsWindow:
    def __init__(self, root):
        self.root = root
        self.root.title("Reports - D R Medical Store")
        self.root.geometry("900x600")
        self.root.resizable(True, True)
        self.root.configure(bg="#f0f4f7")
        self.is_maximized = False
        # self.original_content_pos = (50, 70) # Store original position if needed
        self.maximize_btn = tk.Button(self.root, text="🗖", command=self.toggle_maximize, font=("Helvetica", 14), relief=tk.FLAT, bd=0)
        self.maximize_btn.place(x=10, y=10) # Place near top-left

        title = tk.Label(self.root, text="Reports Section", font=("Helvetica", 20, "bold"), bg="#2c3e50", fg="white", pady=10)
        title.pack(fill=tk.X)

        message = tk.Label(self.root, text="Select a report to view or export.", font=("Helvetica", 14), bg="#f0f4f7", fg="#34495e")
        message.pack(pady=20)

        tk.Button(self.root, text="Stock Report", command=self.stock_report, width=20).pack(pady=10)
        tk.Button(self.root, text="Export to CSV", command=self.export_to_csv, width=20).pack(pady=10)
        tk.Button(self.root, text="Export to PDF", command=self.export_to_pdf, width=20).pack(pady=10)
        tk.Button(self.root, text="Low Stock Report", command=lambda: show_low_stock_report(self.root), width=20).pack(pady=10) # Pass self.root
        tk.Button(self.root, text="Expiry Alert Report", command=lambda: show_expiry_report(self.root), width=20).pack(pady=10) # Pass self.root

        back_button = tk.Button(self.root, text="Back to Dashboard", command=self.root.destroy, bg="#3498db", fg="white", font=("Helvetica", 12))
        back_button.pack(side=tk.BOTTOM, pady=10)

        # Center content initially and bind resize event
        self.center_main_content()
        self.root.bind("<Configure>", lambda event: self.on_resize()) # Handle resize

  # Implemented functionality for stock report, export to CSV, and export to PDF
    def stock_report(self):
        query = "SELECT * FROM inventory"
        data = self.fetch_data(query)
        if data:
            self.show_report("Stock Report", data, ("ID", "Name", "Quantity", "Expiry", "Price"))
        else:
            messagebox.showinfo("Stock Report", "No stock data available.")

    def fetch_data(self, query):
        try:
            # Get the directory where the current script (reports.py) is located
            script_dir = os.path.dirname(os.path.abspath(__file__))
            # Construct the absolute path to the database file
            db_path = os.path.join(script_dir, "db", "store.db")
            conn = sqlite3.connect(db_path)
            cursor = conn.cursor()
            cursor.execute(query)
            data = cursor.fetchall()
            conn.close()
            return data
        except sqlite3.Error as e:
            messagebox.showerror("Database Error", str(e))
            return None

    def show_report(self, title, data, columns):
        report_window = tk.Toplevel(self.root)
        report_window.title(title)
        report_window.geometry("800x400")

        tree = ttk.Treeview(report_window, columns=columns, show="headings")
        for col in columns:
            tree.heading(col, text=col)
            tree.column(col, width=100)
        tree.pack(fill=tk.BOTH, expand=True)

        for row in data:
            tree.insert("", tk.END, values=row)

    def export_to_csv(self):
        query = "SELECT * FROM inventory"
        data = self.fetch_data(query)
        if data:
            file = filedialog.asksaveasfilename(defaultextension=".csv", filetypes=[("CSV Files", "*.csv")])
            if file:
                with open(file, mode='w', newline='') as f:
                    writer = csv.writer(f)
                    writer.writerow(["ID", "Name", "Quantity", "Expiry", "Price"])
                    writer.writerows(data)
                messagebox.showinfo("Export to CSV", f"Data exported successfully to {file}")
        else:
            messagebox.showinfo("Export to CSV", "No data available to export.")

    def export_to_pdf(self):
        query = "SELECT * FROM inventory"
        data = self.fetch_data(query)
        if data:
            file = filedialog.asksaveasfilename(defaultextension=".pdf", filetypes=[("PDF Files", "*.pdf")])
            if file:
                pdf = FPDF()
                pdf.add_page()
                pdf.set_font("Arial", size=12)

                pdf.cell(200, 10, txt="Stock Report", ln=True, align="C")
                pdf.ln(10)

                col_names = ["ID", "Name", "Quantity", "Expiry", "Price"]
                for col in col_names:
                    pdf.cell(40, 10, col, border=1)
                pdf.ln()

                for row in data:
                    for item in row:
                        pdf.cell(40, 10, str(item), border=1)
                    pdf.ln()

                pdf.output(file)
                messagebox.showinfo("Export to PDF", f"Data exported successfully to {file}")
        else:
            messagebox.showinfo("Export to PDF", "No data available to export.")
    # Removed show_low_stock_report and show_expiry_report methods from the class

    def toggle_maximize(self):
        """Toggles the window between maximized and normal state."""
        if self.is_maximized:
            self.root.state('normal')
            self.maximize_btn.config(text="🗖") # Maximize symbol
        else:
            self.root.state('zoomed')
            self.maximize_btn.config(text="🗗") # Restore symbol
        self.is_maximized = not self.is_maximized
        self.root.after(50, self.center_main_content)

    def center_main_content(self):
        """Adjusts layout (placeholder for reports window)."""
        # Centering logic might be simple or complex depending on layout.
        # For now, just ensure it exists.
        self.root.update_idletasks()
        pass # Add specific centering logic if needed for packed buttons

    def on_resize(self):
        """Handles window resize events to readjust layout."""
        # Avoid recursive calls during state transitions triggered by toggle_maximize
        if hasattr(self, '_resizing'):
            return
        self._resizing = True
        self.center_main_content()
        # Use 'after' to clear the flag once the resize handling is done
        self.root.after(100, lambda: delattr(self, '_resizing'))
