# supplier.py
import tkinter as tk
from tkinter import ttk, messagebox
import sqlite3
import os # Add os import

class SupplierWindow:
    def __init__(self, root):
        self.root = root
        self.root.title("Manage Suppliers")
        self.root.state('zoomed')
        self.root.resizable(True, True)

        # Initialize database connection
        try: # Add try-except block for connection
            # Construct absolute path to the database
            script_dir = os.path.dirname(os.path.abspath(__file__))
            db_path = os.path.join(script_dir, "db", "store.db")
            self.conn = sqlite3.connect(db_path)
            self.cursor = self.conn.cursor()
        except sqlite3.Error as e:
            messagebox.showerror("Database Error", f"Failed to connect to database: {e}\nAttempted Path: {db_path}")
            self.conn = None # Ensure conn is None if connection fails
            self.cursor = None
            # Allow window to open but database operations will fail later if cursor is used without check

        # Variables
        self.name_var = tk.StringVar()
        self.contact_person_var = tk.StringVar()
        self.phone_var = tk.StringVar()
        self.email_var = tk.StringVar()
        self.address_var = tk.StringVar()

        # --- Title ---
        title = tk.Label(root, text="Supplier Management", font=("Helvetica", 20, "bold"), bg="#FF5722", fg="white", pady=10)
        title.pack(fill=tk.X)

        # --- Form Frame ---
        self.form_frame = tk.Frame(root, bd=3, relief=tk.RIDGE, padx=10, pady=10)
        # self.form_frame.place(x=10, y=70, width=400, height=500) # Removed initial fixed place

        tk.Label(self.form_frame, text="Supplier Name*", font=("Helvetica", 12)).grid(row=0, column=0, sticky="w", pady=5, padx=5)
        tk.Entry(self.form_frame, textvariable=self.name_var, font=("Helvetica", 12)).grid(row=0, column=1, pady=5, sticky="ew")

        tk.Label(self.form_frame, text="Contact Person", font=("Helvetica", 12)).grid(row=1, column=0, sticky="w", pady=5, padx=5)
        tk.Entry(self.form_frame, textvariable=self.contact_person_var, font=("Helvetica", 12)).grid(row=1, column=1, pady=5, sticky="ew")

        tk.Label(self.form_frame, text="Phone", font=("Helvetica", 12)).grid(row=2, column=0, sticky="w", pady=5, padx=5)
        tk.Entry(self.form_frame, textvariable=self.phone_var, font=("Helvetica", 12)).grid(row=2, column=1, pady=5, sticky="ew")

        tk.Label(self.form_frame, text="Email", font=("Helvetica", 12)).grid(row=3, column=0, sticky="w", pady=5, padx=5)
        tk.Entry(self.form_frame, textvariable=self.email_var, font=("Helvetica", 12)).grid(row=3, column=1, pady=5, sticky="ew")

        tk.Label(self.form_frame, text="Address", font=("Helvetica", 12)).grid(row=4, column=0, sticky="w", pady=5, padx=5)
        tk.Entry(self.form_frame, textvariable=self.address_var, font=("Helvetica", 12)).grid(row=4, column=1, pady=5, sticky="ew")

        # Configure column 1 to expand
        self.form_frame.grid_columnconfigure(1, weight=1)

        # Buttons moved down one row to accommodate new fields
        tk.Button(self.form_frame, text="Add Supplier", command=self.add_supplier, bg="#4CAF50", fg="white", width=20, font=("Helvetica", 10)).grid(row=5, columnspan=2, pady=15)
        tk.Button(self.form_frame, text="Update Info", command=self.update_supplier, bg="#2196F3", fg="white", width=20, font=("Helvetica", 10)).grid(row=6, columnspan=2, pady=8)
        tk.Button(self.form_frame, text="Delete Supplier", command=self.delete_supplier, bg="#F44336", fg="white", width=20, font=("Helvetica", 10)).grid(row=7, columnspan=2, pady=8)
        tk.Button(self.form_frame, text="Clear Fields", command=self.clear_fields, bg="#9C27B0", fg="white", width=20, font=("Helvetica", 10)).grid(row=8, columnspan=2, pady=8)
        back_button = tk.Button(self.form_frame, text="Back to Dashboard", command=self.root.destroy, bg="#3498db", fg="white", width=20, font=("Helvetica", 10))
        back_button.grid(row=9, columnspan=2, pady=8)

        # --- Supplier List Frame ---
        self.list_frame = tk.Frame(root, bd=3, relief=tk.RIDGE)
        # self.list_frame.place(x=430, y=70, width=350, height=500) # Removed initial fixed place
        # Add horizontal and vertical scrollbars
        x_scroll = tk.Scrollbar(self.list_frame, orient=tk.HORIZONTAL)
        y_scroll = tk.Scrollbar(self.list_frame, orient=tk.VERTICAL)
        self.supplier_table = ttk.Treeview(
            self.list_frame,
            columns=("ID", "Name", "Contact Person", "Phone", "Email", "Address"),
            show="headings",
            xscrollcommand=x_scroll.set,
            yscrollcommand=y_scroll.set,
            style="Excel.Treeview"
        )
        
        # Configure column headings
        self.supplier_table.heading("ID", text="ID")
        self.supplier_table.heading("Name", text="Supplier Name")
        self.supplier_table.heading("Contact Person", text="Contact Person")
        self.supplier_table.heading("Phone", text="Phone")
        self.supplier_table.heading("Email", text="Email")
        self.supplier_table.heading("Address", text="Address")
        x_scroll.config(command=self.supplier_table.xview)
        y_scroll.config(command=self.supplier_table.yview)
        self.supplier_table.grid(row=0, column=0, sticky="nsew")
        y_scroll.grid(row=0, column=1, sticky="ns")
        x_scroll.grid(row=1, column=0, sticky="ew")
        self.list_frame.grid_rowconfigure(0, weight=1)
        self.list_frame.grid_columnconfigure(0, weight=1)
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

        self.supplier_table.bind("<ButtonRelease-1>", self.get_cursor)

        # Now create the table and load data
        self.create_table()

        # Center content initially and bind resize event
        self.center_main_content()
        self.reset_scrollbars()
        self.root.bind("<Configure>", lambda event: self.on_resize()) # Handle resize

        # Removed toggle_maximize button and related logic
        # self.maximize_btn = tk.Button(self.root, text="🗖", command=self.toggle_maximize, font=("Helvetica", 14))
        # self.maximize_btn.place(x=10, y=10)
        # self.is_maximized = False
        # self.original_form_pos = (10, 70)
        # self.original_table_pos = (430, 70)

    # def toggle_maximize(self): # Removed function
    #     pass # Keep function definition to avoid breaking references if any (though unlikely)

    def reset_scrollbars(self):
        """Forces the Treeview scrollbars to update if needed."""
        self.root.update_idletasks()
        pass # No specific action usually needed here

    def center_main_content(self):
        """Adjusts layout, keeping form fixed and expanding table."""
        self.root.update_idletasks()
        window_width = self.root.winfo_width()
        window_height = self.root.winfo_height()
        title_height = 50 # Approximate height of the title bar + padding

        form_width = 400
        form_height = 500 # Adjust if form height changed
        form_x = 10
        form_y = title_height + 20

        self.form_frame.place(x=form_x, y=form_y, width=form_width, height=form_height)

        table_x = form_x + form_width + 20
        table_y = form_y
        table_width = window_width - table_x - 10
        table_height = window_height - table_y - 30

        if table_width < 200: table_width = 200
        if table_height < 200: table_height = 200

        self.list_frame.place(x=table_x, y=table_y, width=table_width, height=table_height)

    def on_resize(self):
        """Handles window resize events to readjust layout."""
        # Avoid recursive calls during state transitions
        if hasattr(self, '_resizing'):
            return
        self._resizing = True
        self.center_main_content()
        self.reset_scrollbars()
        # Use 'after' to clear the flag once the resize handling is done
        self.root.after(100, lambda: delattr(self, '_resizing'))

    def create_table(self):
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS suppliers (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                contact_person TEXT,
                phone TEXT,
                email TEXT,
                address TEXT NULL
            )
        ''')
        self.conn.commit()
        self.load_suppliers()

    def delete_supplier(self):
        selected = self.supplier_table.focus()
        if selected == "":
            messagebox.showerror("Error", "No record selected!")
            return
        values = self.supplier_table.item(selected, 'values')
        try:
            self.cursor.execute("DELETE FROM suppliers WHERE id = ?", (values[0],))
            self.conn.commit()
            self.load_suppliers()
            self.clear_fields()
            messagebox.showinfo("Success", "Supplier deleted successfully!")
        except sqlite3.Error as e:
            messagebox.showerror("Database Error", str(e))

    def add_supplier(self):
        if self.name_var.get() == "":
            messagebox.showerror("Error", "Supplier Name is required!")
            return
        try:
            self.cursor.execute(
                "INSERT INTO suppliers (name, contact_person, phone, email, address) VALUES (?, ?, ?, ?, ?)",
                (
                    self.name_var.get(),
                    self.contact_person_var.get(),
                    self.phone_var.get(),
                    self.email_var.get(),  
                    self.address_var.get()
                )
            )
            self.conn.commit()
            # self.clear_fields() # Keep fields populated after add
            messagebox.showinfo("Success", "Supplier added successfully!")
            self.load_suppliers() # Reload table AFTER showing the message
        except sqlite3.Error as e:
            messagebox.showerror("Database Error", str(e))

    def load_suppliers(self):
        # Clear existing items
        for item in self.supplier_table.get_children():
            self.supplier_table.delete(item)
        try:
            self.cursor.execute("SELECT * FROM suppliers")
            rows = self.cursor.fetchall()
            for row in rows:
                self.supplier_table.insert("", tk.END, values=row)
        except sqlite3.Error as e:
            messagebox.showerror("Database Error", str(e))

    def get_cursor(self, ev):
        selected = self.supplier_table.focus()
        values = self.supplier_table.item(selected, 'values')
        if values:
            self.name_var.set(values[1])
            self.contact_person_var.set(values[2])
            self.phone_var.set(values[3])
            self.email_var.set(values[4])
            self.address_var.set(values[5])

    def update_supplier(self):
        selected = self.supplier_table.focus()
        if selected == "":
            messagebox.showerror("Error", "No record selected!")
            return
        values = self.supplier_table.item(selected, 'values')
        try:
            self.cursor.execute(
                "UPDATE suppliers SET name = ?, contact_person = ?, phone = ?, email = ?, address = ? WHERE id = ?",
                (
                    self.name_var.get(),
                    self.contact_person_var.get(),
                    self.phone_var.get(),
                    self.email_var.get(),
                    self.address_var.get(),
                    values[0]
                )
            )
            self.conn.commit()
            # self.clear_fields() # Keep fields populated after update
            messagebox.showinfo("Success", "Supplier updated successfully!")
            self.load_suppliers() # Reload table AFTER showing the message
        except sqlite3.Error as e:
            messagebox.showerror("Database Error", str(e))

    def clear_fields(self):
        self.name_var.set("")
        self.contact_person_var.set("")
        self.phone_var.set("")
        self.email_var.set("")
        self.address_var.set("")

    def __del__(self):
        if hasattr(self, 'conn') and self.conn:
            self.conn.close()
