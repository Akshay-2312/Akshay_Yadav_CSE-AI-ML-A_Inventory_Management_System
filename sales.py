# sales.py
import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
import sqlite3

class SalesWindow:
    def __init__(self, root):
        self.root = root
        self.root.title("Sales/Billing")
        self.root.geometry("800x600")

        # Variables
        self.search_var = tk.StringVar()
        self.cart = []
        self.is_maximized = False
        self.original_form_pos = (10, 70)
        self.original_table_pos = (580, 120)
        self.maximize_btn = tk.Button(self.root, text="🗖", command=self.toggle_maximize, font=("Helvetica", 14))
        self.maximize_btn.place(x=10, y=10)

        # --- Title ---
        title = tk.Label(root, text="Sales / Billing System", font=("Helvetica", 20, "bold"), bg="#673AB7", fg="white", pady=10)
        title.pack(fill=tk.X)

        # --- Search Frame ---
        search_frame = tk.Frame(root, pady=10)
        search_frame.place(x=10, y=70)

        tk.Label(search_frame, text="Search Medicine:", font=("Helvetica", 12)).grid(row=0, column=0, padx=5)
        tk.Entry(search_frame, textvariable=self.search_var, font=("Helvetica", 12), width=30).grid(row=0, column=1, padx=5)
        tk.Button(search_frame, text="Search", command=self.search_medicine, bg="#4CAF50", fg="white", width=10).grid(row=0, column=2, padx=5)

        # --- Medicine List Table ---
        self.medicine_table = ttk.Treeview(root, columns=("Name", "Batch", "Expiry", "Qty", "Price"), show="headings")
        self.medicine_table.heading("Name", text="Medicine Name")
        self.medicine_table.heading("Batch", text="Batch No")
        self.medicine_table.heading("Expiry", text="Expiry Date")
        self.medicine_table.heading("Qty", text="Available Qty")
        self.medicine_table.heading("Price", text="Price per Unit")
        self.medicine_table.column("Name", width=150)
        self.medicine_table.column("Batch", width=100)
        self.medicine_table.column("Expiry", width=100)
        self.medicine_table.column("Qty", width=80)
        self.medicine_table.column("Price", width=80)
        self.medicine_table.place(x=10, y=120, width=550, height=500)

        # --- Cart Frame ---
        cart_frame = tk.Frame(root, bd=3, relief=tk.RIDGE)
        cart_frame.place(x=580, y=120, width=600, height=500)

        tk.Label(cart_frame, text="Billing Details", font=("Helvetica", 16, "bold")).pack(pady=10)

        self.cart_text = tk.Text(cart_frame, font=("Courier", 12))
        self.cart_text.pack(fill=tk.BOTH, expand=True)

        # --- Buttons ---
        tk.Button(cart_frame, text="Add to Cart", command=self.add_to_cart, bg="#2196F3", fg="white", width=15).pack(pady=5)
        tk.Button(cart_frame, text="Generate Bill", command=self.generate_bill, bg="#4CAF50", fg="white", width=15).pack(pady=5)
        tk.Button(cart_frame, text="Clear Cart", command=self.clear_cart, bg="#F44336", fg="white", width=15).pack(pady=5)

        # --- Dummy Inventory (for now) ---
        self.inventory = [
            ["Paracetamol", "B123", "2025-05-30", 100, 5],
            ["Amoxicillin", "B234", "2024-11-15", 50, 10],
            ["Cough Syrup", "B345", "2025-01-10", 30, 50],
            ["Vitamin C", "B456", "2026-02-20", 200, 2],
        ]
        self.refresh_medicine_table()

        # Initialize database connection
        self.conn = sqlite3.connect("db/store.db")
        self.cursor = self.conn.cursor()
        self.create_table()
        self.load_sales()

        back_button = tk.Button(self.root, text="Back to Dashboard", command=self.root.destroy, bg="#3498db", fg="white", font=("Helvetica", 12))
        back_button.pack(side=tk.BOTTOM, pady=10)

    def create_table(self):
        # Ensure the sales table exists
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS sales (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                medicine_id INTEGER,
                quantity_sold INTEGER,
                amount REAL,
                sale_date TEXT DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (medicine_id) REFERENCES inventory(id) ON DELETE CASCADE
            )
        ''')
        self.conn.commit()

    def load_sales(self):
        # Load sales data into the table
        self.cart_text.delete("1.0", tk.END)
        self.cursor.execute("SELECT * FROM sales")
        for row in self.cursor.fetchall():
            self.cart_text.insert(tk.END, f"{row}\n")

    def refresh_medicine_table(self):
        for item in self.medicine_table.get_children():
            self.medicine_table.delete(item)
        for med in self.inventory:
            self.medicine_table.insert('', 'end', values=med)

    def search_medicine(self):
        keyword = self.search_var.get().lower()
        results = []
        for med in self.inventory:
            if keyword in med[0].lower():
                results.append(med)
        
        for item in self.medicine_table.get_children():
            self.medicine_table.delete(item)
        
        for med in results:
            self.medicine_table.insert('', 'end', values=med)

    def add_to_cart(self):
        selected = self.medicine_table.focus()
        if selected == "":
            messagebox.showerror("Error", "Select a medicine to add!")
            return
        values = self.medicine_table.item(selected, 'values')
        if not values:
            return

        qty = simpledialog.askinteger("Quantity", "Enter quantity:", minvalue=1, maxvalue=int(values[3]))
        if qty is None:
            return

        if qty > int(values[3]):
            messagebox.showerror("Error", "Not enough stock available!")
            return

        med_name, batch, expiry, available_qty, price_per_unit = values
        amount = qty * float(price_per_unit)

        try:
            # Update inventory
            self.cursor.execute("UPDATE inventory SET quantity = quantity - ? WHERE name = ? AND batch_no = ?", (qty, med_name, batch))

            # Add to sales
            self.cursor.execute(
                "INSERT INTO sales (medicine_id, quantity_sold, amount) VALUES ((SELECT id FROM inventory WHERE name = ? AND batch_no = ?), ?, ?)",
                (med_name, batch, qty, amount)
            )
            self.conn.commit()
            self.load_sales()
            messagebox.showinfo("Success", "Item added to cart and sales updated!")
        except sqlite3.Error as e:
            messagebox.showerror("Database Error", str(e))

    def show_cart(self):
        self.cart_text.delete("1.0", tk.END)
        total = 0
        for item in self.cart:
            line = f"{item[0]} ({item[1]}) x {item[3]} = ₹{item[3]*float(item[4]):.2f}\n"
            self.cart_text.insert(tk.END, line)
            total += item[3]*float(item[4])
        self.cart_text.insert(tk.END, "\n-------------------------\n")
        self.cart_text.insert(tk.END, f"Total Amount: ₹{total:.2f}")

    def generate_bill(self):
        if not self.cart:
            messagebox.showerror("Error", "Cart is empty!")
            return
        messagebox.showinfo("Success", "Bill generated successfully!")
        self.cart.clear()
        self.clear_cart()

    def clear_cart(self):
        self.cart.clear()
        self.cart_text.delete("1.0", tk.END)
        self.refresh_medicine_table()

    def toggle_maximize(self):
        if not self.is_maximized:
            self.root.state('zoomed')
            self.center_main_content()
            self.is_maximized = True
        else:
            self.root.state('normal')
            self.search_frame.place(x=self.original_form_pos[0], y=self.original_form_pos[1])
            self.medicine_table.place(x=self.original_form_pos[0], y=120)
            self.cart_frame.place(x=self.original_table_pos[0], y=120)
            self.is_maximized = False

    def center_main_content(self):
        self.root.update_idletasks()
        win_width = self.root.winfo_width()
        win_height = self.root.winfo_height()
        form_width = self.search_frame.winfo_width()
        table_width = self.medicine_table.winfo_width()
        cart_width = self.cart_frame.winfo_width()
        total_width = table_width + cart_width + 40
        x_start = (win_width - total_width) // 2
        y_center = (win_height - max(self.medicine_table.winfo_height(), self.cart_frame.winfo_height())) // 2
        self.search_frame.place(x=x_start, y=y_center)
        self.medicine_table.place(x=x_start, y=y_center+50)
        self.cart_frame.place(x=x_start + table_width + 40, y=y_center+50)

    def __del__(self):
        # Close the database connection when the window is closed
        self.conn.close()

