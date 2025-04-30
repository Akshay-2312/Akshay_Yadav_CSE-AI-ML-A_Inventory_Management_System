# inventory.py
import tkinter as tk
from tkinter import ttk, messagebox
import datetime
import sqlite3

class InventoryWindow:
    def __init__(self, root):
        self.root = root
        self.root.title("Manage Inventory")
        self.root.geometry("800x600")

        # Medicine variables
        self.med_name_var = tk.StringVar()
        self.batch_no_var = tk.StringVar()
        self.expiry_date_var = tk.StringVar()
        self.quantity_var = tk.IntVar()
        self.price_var = tk.DoubleVar()

        # --- Title ---
        title = tk.Label(root, text="Inventory Management", font=("Helvetica", 20, "bold"), bg="#2196F3", fg="white", pady=10)
        title.pack(fill=tk.X)

        # --- Form Frame ---
        form_frame = tk.Frame(root, padx=10, pady=10, bd=3, relief=tk.RIDGE)
        form_frame.place(x=10, y=70, width=400, height=500)

        tk.Label(form_frame, text="Medicine Name:", font=("Helvetica", 12)).grid(row=0, column=0, pady=5)
        tk.Entry(form_frame, textvariable=self.med_name_var, font=("Helvetica", 12)).grid(row=0, column=1, pady=5)

        tk.Label(form_frame, text="Batch No:", font=("Helvetica", 12)).grid(row=1, column=0, pady=5)
        tk.Entry(form_frame, textvariable=self.batch_no_var, font=("Helvetica", 12)).grid(row=1, column=1, pady=5)

        tk.Label(form_frame, text="Expiry Date (YYYY-MM-DD):", font=("Helvetica", 12)).grid(row=2, column=0, pady=5)
        tk.Entry(form_frame, textvariable=self.expiry_date_var, font=("Helvetica", 12)).grid(row=2, column=1, pady=5)

        tk.Label(form_frame, text="Quantity:", font=("Helvetica", 12)).grid(row=3, column=0, pady=5)
        tk.Entry(form_frame, textvariable=self.quantity_var, font=("Helvetica", 12)).grid(row=3, column=1, pady=5)

        tk.Label(form_frame, text="Price per Unit:", font=("Helvetica", 12)).grid(row=4, column=0, pady=5)
        tk.Entry(form_frame, textvariable=self.price_var, font=("Helvetica", 12)).grid(row=4, column=1, pady=5)

        # --- Buttons ---
        tk.Button(form_frame, text="Add Medicine", command=self.add_medicine, width=15, bg="#4CAF50", fg="white").grid(row=5, column=0, pady=20)
        tk.Button(form_frame, text="Update Selected", command=self.update_medicine, width=15, bg="#2196F3", fg="white").grid(row=5, column=1, pady=20)
        tk.Button(form_frame, text="Delete Selected", command=self.delete_medicine, width=15, bg="#F44336", fg="white").grid(row=6, column=0, pady=5)
        tk.Button(form_frame, text="Clear Fields", command=self.clear_fields, width=15, bg="#9C27B0", fg="white").grid(row=6, column=1, pady=5)
        back_button = tk.Button(form_frame, text="Back to Dashboard", command=self.root.destroy, bg="#3498db", fg="white", font=("Helvetica", 12), width=20)
        back_button.grid(row=7, columnspan=2, pady=10)

        # --- Table Frame ---
        self.is_maximized = False
        self.original_table_frame_pos = (450, 70)
        self.table_frame = tk.Frame(root, bd=3, relief=tk.RIDGE)
        self.table_frame.place(x=430, y=70, width=350, height=500)

        # Add horizontal and vertical scrollbars
        x_scroll = tk.Scrollbar(self.table_frame, orient=tk.HORIZONTAL)
        y_scroll = tk.Scrollbar(self.table_frame, orient=tk.VERTICAL)
        self.medicine_table = ttk.Treeview(
            self.table_frame,
            columns=("Name", "Batch", "Expiry", "Qty", "Price"),
            show="headings",
            xscrollcommand=x_scroll.set,
            yscrollcommand=y_scroll.set,
            style="Excel.Treeview"
        )
        x_scroll.config(command=self.medicine_table.xview)
        y_scroll.config(command=self.medicine_table.yview)
        self.medicine_table.grid(row=0, column=0, sticky="nsew")
        y_scroll.grid(row=0, column=1, sticky="ns")
        x_scroll.grid(row=1, column=0, sticky="ew")
        self.table_frame.grid_rowconfigure(0, weight=1)
        self.table_frame.grid_columnconfigure(0, weight=1)

        # Excel-like style for the table
        style = ttk.Style()
        style.configure("Excel.Treeview",
                        font=("Consolas", 11),
                        rowheight=28,
                        borderwidth=1,
                        relief="solid")
        style.configure("Excel.Treeview.Heading",
                        font=("Consolas", 11, "bold"),
                        background="#e0e0e0",
                        borderwidth=1,
                        relief="solid")
        style.map("Excel.Treeview",
                  background=[('selected', '#cce6ff')])

        self.medicine_table.heading("Name", text="Medicine Name")
        self.medicine_table.heading("Batch", text="Batch No")
        self.medicine_table.heading("Expiry", text="Expiry Date")
        self.medicine_table.heading("Qty", text="Quantity")
        self.medicine_table.heading("Price", text="Price")
        self.medicine_table.column("Name", width=150, anchor="center")
        self.medicine_table.column("Batch", width=100, anchor="center")
        self.medicine_table.column("Expiry", width=120, anchor="center")
        self.medicine_table.column("Qty", width=80, anchor="center")
        self.medicine_table.column("Price", width=80, anchor="center")

        self.medicine_table.bind("<ButtonRelease-1>", self.select_row)

        # Add Restore/Maximize button with a symbol at the top left corner
        self.maximize_btn = tk.Button(self.root, text="🗖", command=self.toggle_maximize, font=("Helvetica", 14))
        self.maximize_btn.place(x=10, y=10)

        # Initialize database connection (move this up to ensure it's always set before DB operations)
        self.conn = sqlite3.connect("db/store.db")
        self.cursor = self.conn.cursor()
        self.create_table()
        self.load_inventory()

        # Store references to main content frames for repositioning
        self.form_frame = form_frame

    def create_table(self):
        # Ensure the inventory table exists
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS inventory (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                batch_no TEXT NOT NULL,
                quantity INTEGER DEFAULT 0,
                price REAL NOT NULL,
                expiry_date TEXT
            )
        ''')
        self.conn.commit()

    def load_inventory(self):
        # Load inventory data into the table
        self.medicine_table.delete(*self.medicine_table.get_children())
        self.cursor.execute("SELECT name, batch_no, expiry_date, quantity, price FROM inventory")
        for row in self.cursor.fetchall():
            self.medicine_table.insert('', 'end', values=row)

    def add_medicine(self):
        if self.med_name_var.get() == "" or self.batch_no_var.get() == "":
            messagebox.showerror("Error", "Medicine Name and Batch No are required!")
            return
        try:
            quantity = int(self.quantity_var.get())
            if quantity < 0:
                raise ValueError("Quantity cannot be negative.")
        except ValueError:
            messagebox.showerror("Invalid Input", "Please enter a valid positive integer for quantity.")
            return
        try:
            self.cursor.execute(
                "INSERT INTO inventory (name, batch_no, expiry_date, quantity, price) VALUES (?, ?, ?, ?, ?)",
                (
                    self.med_name_var.get(),
                    self.batch_no_var.get(),
                    self.expiry_date_var.get(),
                    self.quantity_var.get(),
                    self.price_var.get()
                )
            )
            self.conn.commit()
            self.load_inventory()
            self.clear_fields()
            messagebox.showinfo("Success", "Medicine added successfully!")
        except sqlite3.Error as e:
            messagebox.showerror("Database Error", str(e))

    def update_medicine(self):
        selected = self.medicine_table.focus()
        if selected == "":
            messagebox.showerror("Error", "No record selected!")
            return
        values = self.medicine_table.item(selected, 'values')
        try:
            self.cursor.execute(
                "UPDATE inventory SET name = ?, batch_no = ?, expiry_date = ?, quantity = ?, price = ? WHERE name = ? AND batch_no = ?",
                (
                    self.med_name_var.get(),
                    self.batch_no_var.get(),
                    self.expiry_date_var.get(),
                    self.quantity_var.get(),
                    self.price_var.get(),
                    values[0],
                    values[1]
                )
            )
            self.conn.commit()
            self.load_inventory()
            self.clear_fields()
            messagebox.showinfo("Success", "Medicine updated successfully!")
        except sqlite3.Error as e:
            messagebox.showerror("Database Error", str(e))

    def delete_medicine(self):
        selected = self.medicine_table.focus()
        if selected == "":
            messagebox.showerror("Error", "No record selected!")
            return
        values = self.medicine_table.item(selected, 'values')
        try:
            self.cursor.execute("DELETE FROM inventory WHERE name = ? AND batch_no = ?", (values[0], values[1]))
            self.conn.commit()
            self.load_inventory()
            self.clear_fields()
            messagebox.showinfo("Success", "Medicine deleted successfully!")
        except sqlite3.Error as e:
            messagebox.showerror("Database Error", str(e))

    def clear_fields(self):
        self.med_name_var.set("")
        self.batch_no_var.set("")
        self.expiry_date_var.set("")
        self.quantity_var.set(0)
        self.price_var.set(0.0)

    def select_row(self, event):
        selected = self.medicine_table.focus()
        values = self.medicine_table.item(selected, 'values')
        if values:
            self.med_name_var.set(values[0])
            self.batch_no_var.set(values[1])
            self.expiry_date_var.set(values[2])
            self.quantity_var.set(values[3])
            self.price_var.set(values[4])

    def toggle_maximize(self):
        if not self.is_maximized:
            self.root.state('zoomed')
            self.center_main_content()
            # Expand columns for maximized view
            self.medicine_table.column("Name", width=350)
            self.medicine_table.column("Batch", width=200)
            self.medicine_table.column("Expiry", width=250)
            self.medicine_table.column("Qty", width=180)
            self.medicine_table.column("Price", width=180)
            for child in self.table_frame.winfo_children():
                if isinstance(child, tk.Scrollbar) and child.cget('orient') == 'horizontal':
                    self.medicine_table.configure(xscrollcommand=child.set)
                    child.config(command=self.medicine_table.xview)
            self.medicine_table.update_idletasks()
            self.medicine_table.xview_moveto(0)
            self.is_maximized = True
        else:
            self.root.state('normal')
            self.form_frame.place(x=10, y=70, width=400, height=500)
            self.table_frame.place(x=430, y=70, width=350, height=500)
            self.medicine_table.column("Name", width=150)
            self.medicine_table.column("Batch", width=100)
            self.medicine_table.column("Expiry", width=120)
            self.medicine_table.column("Qty", width=80)
            self.medicine_table.column("Price", width=80)
            for child in self.table_frame.winfo_children():
                if isinstance(child, tk.Scrollbar) and child.cget('orient') == 'horizontal':
                    self.medicine_table.configure(xscrollcommand=child.set)
                    child.config(command=self.medicine_table.xview)
            self.medicine_table.update_idletasks()
            self.medicine_table.xview_moveto(0)
            self.is_maximized = False

    def center_main_content(self):
        self.root.update_idletasks()
        win_width = self.root.winfo_width()
        win_height = self.root.winfo_height()
        # Dynamically calculate sizes for maximized state
        form_width = int(win_width * 0.32)
        table_width = int(win_width * 0.56)
        frame_height = int(win_height * 0.8)
        x_start = (win_width - (form_width + table_width + 40)) // 2
        y_center = (win_height - frame_height) // 2
        self.form_frame.place(x=x_start, y=y_center, width=form_width, height=frame_height)
        self.table_frame.place(x=x_start + form_width + 40, y=y_center, width=table_width, height=frame_height)
        # Adjust Treeview columns to fit new table width
        self.medicine_table.column("Name", width=int(table_width * 0.3))
        self.medicine_table.column("Batch", width=int(table_width * 0.15))
        self.medicine_table.column("Expiry", width=int(table_width * 0.22))
        self.medicine_table.column("Qty", width=int(table_width * 0.13))
        self.medicine_table.column("Price", width=int(table_width * 0.2))

    def __del__(self):
        # Close the database connection when the window is closed
        self.conn.close()

