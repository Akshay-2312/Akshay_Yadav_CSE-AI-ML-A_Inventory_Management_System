# employee.py
import tkinter as tk
from tkinter import ttk, messagebox
import sqlite3
import os # Add os import

class EmployeeWindow:
    def __init__(self, root):
        self.root = root
        self.root.title("Manage Employees")
        self.root.state('zoomed')
        self.root.resizable(True, True)

        # Variables
        self.name_var = tk.StringVar()
        self.phone_var = tk.StringVar()
        self.email_var = tk.StringVar()
        self.position_var = tk.StringVar()
        self.salary_var = tk.DoubleVar()

        # --- Title ---
        title = tk.Label(root, text="Employee Management", font=("Helvetica", 20, "bold"), bg="#009688", fg="white", pady=10)
        title.pack(fill=tk.X)

        # --- Form Frame ---
        self.form_frame = tk.Frame(root, bd=3, relief=tk.RIDGE, padx=10, pady=10)
        self.form_frame.place(x=10, y=70, width=400, height=500)

        tk.Label(self.form_frame, text="Employee Name", font=("Helvetica", 12)).grid(row=0, column=0, sticky="w", pady=5)
        tk.Entry(self.form_frame, textvariable=self.name_var, font=("Helvetica", 12)).grid(row=0, column=1, pady=5)

        tk.Label(self.form_frame, text="Phone Number", font=("Helvetica", 12)).grid(row=1, column=0, sticky="w", pady=5)
        tk.Entry(self.form_frame, textvariable=self.phone_var, font=("Helvetica", 12)).grid(row=1, column=1, pady=5)

        tk.Label(self.form_frame, text="Email Address", font=("Helvetica", 12)).grid(row=2, column=0, sticky="w", pady=5)
        tk.Entry(self.form_frame, textvariable=self.email_var, font=("Helvetica", 12)).grid(row=2, column=1, pady=5)

        tk.Label(self.form_frame, text="Position", font=("Helvetica", 12)).grid(row=3, column=0, sticky="w", pady=5)
        tk.Entry(self.form_frame, textvariable=self.position_var, font=("Helvetica", 12)).grid(row=3, column=1, pady=5)

        tk.Label(self.form_frame, text="Salary", font=("Helvetica", 12)).grid(row=4, column=0, sticky="w", pady=5)
        tk.Entry(self.form_frame, textvariable=self.salary_var, font=("Helvetica", 12)).grid(row=4, column=1, pady=5)

        tk.Button(self.form_frame, text="Add Employee", command=self.add_employee, bg="#4CAF50", fg="white", width=20).grid(row=5, columnspan=2, pady=20)
        tk.Button(self.form_frame, text="Update Info", command=self.update_employee, bg="#2196F3", fg="white", width=20).grid(row=6, columnspan=2, pady=10)
        tk.Button(self.form_frame, text="Delete Employee", command=self.delete_employee, bg="#F44336", fg="white", width=20).grid(row=7, columnspan=2, pady=10)
        tk.Button(self.form_frame, text="Clear Fields", command=self.clear_fields, bg="#9C27B0", fg="white", width=20).grid(row=8, columnspan=2, pady=10)

        # Added a back button under the Clear Fields button to return to the dashboard
        back_button = tk.Button(self.form_frame, text="Back to Dashboard", command=self.root.destroy, bg="#3498db", fg="white", width=20)
        back_button.grid(row=9, columnspan=2, pady=10)

        # --- Employee List Frame ---
        self.list_frame = tk.Frame(root, bd=3, relief=tk.RIDGE)
        self.list_frame.place(x=430, y=70, width=350, height=500)
        # Add horizontal and vertical scrollbars
        x_scroll = tk.Scrollbar(self.list_frame, orient=tk.HORIZONTAL)
        y_scroll = tk.Scrollbar(self.list_frame, orient=tk.VERTICAL)
        self.employee_table = ttk.Treeview(
            self.list_frame,
            columns=("ID", "Name", "Email", "Phone", "Position", "Salary"),
            show="headings",
            xscrollcommand=x_scroll.set,
            yscrollcommand=y_scroll.set,
            style="Excel.Treeview"
        )
        x_scroll.config(command=self.employee_table.xview)
        y_scroll.config(command=self.employee_table.yview)
        self.employee_table.grid(row=0, column=0, sticky="nsew")
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

        self.employee_table.column("ID", width=50)
        self.employee_table.column("Name", width=150)
        self.employee_table.column("Email", width=150)
        self.employee_table.column("Phone", width=100)
        self.employee_table.column("Position", width=100)
        self.employee_table.column("Salary", width=100)
        self.employee_table.heading("ID", text="ID")
        self.employee_table.heading("Name", text="Name")
        self.employee_table.heading("Email", text="Email")
        self.employee_table.heading("Phone", text="Phone")
        self.employee_table.heading("Position", text="Position")
        self.employee_table.heading("Salary", text="Salary")

        self.employee_table.bind("<ButtonRelease-1>", self.get_cursor)

        # Initialize database connection
        try: # Add try-except block for connection
            # Construct absolute path to the database
            script_dir = os.path.dirname(os.path.abspath(__file__))
            db_path = os.path.join(script_dir, "db", "store.db")
            self.conn = sqlite3.connect(db_path)
            self.cursor = self.conn.cursor()
            self.create_table()
            self.load_employees()
        except sqlite3.Error as e:
            messagebox.showerror("Database Error", f"Failed to connect to database: {e}\nAttempted Path: {db_path}")
            self.conn = None # Ensure conn is None if connection fails
            self.cursor = None
            # Allow window to open but database operations will fail later if cursor is used without check

        # Center content initially and bind resize event
        self.center_main_content()
        self.root.bind("<Configure>", lambda event: self.on_resize()) # Handle resize

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
        form_height = 500
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
        # Avoid recursive calls during state transitions triggered by toggle_maximize
        if hasattr(self, '_resizing'):
            return
        self._resizing = True
        self.center_main_content()
        self.reset_scrollbars()
        # Use 'after' to clear the flag once the resize handling is done
        self.root.after(100, lambda: delattr(self, '_resizing'))

    def create_table(self):
        # Ensure the employees table exists
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS employees (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                email TEXT,
                phone TEXT,
                position TEXT,
                salary REAL
            )
        ''')
        self.conn.commit()

    def load_employees(self):
        # Load employee data into the table
        self.employee_table.delete(*self.employee_table.get_children())
        self.cursor.execute("SELECT id, name, email, phone, position, salary FROM employees")
        for row in self.cursor.fetchall():
            self.employee_table.insert('', 'end', values=row)

    def add_employee(self):
        if self.name_var.get() == "" or self.phone_var.get() == "":
            messagebox.showerror("Error", "Name and Phone number are required!")
            return
        try:
            self.cursor.execute(
                "INSERT INTO employees (name, email, phone, position, salary) VALUES (?, ?, ?, ?, ?)",
                (
                    self.name_var.get(),
                    self.email_var.get(),
                    self.phone_var.get(),
                    self.position_var.get(),
                    self.salary_var.get()
                )
            )
            self.conn.commit()
            # self.clear_fields() # Keep fields populated after add
            messagebox.showinfo("Success", "Employee added successfully!")
            self.load_employees() # Reload table AFTER showing the message
        except sqlite3.Error as e:
            messagebox.showerror("Database Error", str(e))

    def get_cursor(self, ev):
        selected = self.employee_table.focus()
        values = self.employee_table.item(selected, 'values')
        if values:
            self.name_var.set(values[1])
            self.email_var.set(values[2])
            self.phone_var.set(values[3])
            self.position_var.set(values[4])
            self.salary_var.set(values[5])

    def update_employee(self):
        selected = self.employee_table.focus()
        if selected == "":
            messagebox.showerror("Error", "No record selected!")
            return
        values = self.employee_table.item(selected, 'values')
        try:
            self.cursor.execute(
                "UPDATE employees SET name = ?, email = ?, phone = ?, position = ?, salary = ? WHERE id = ?",
                (
                    self.name_var.get(),
                    self.email_var.get(),
                    self.phone_var.get(),
                    self.position_var.get(),
                    self.salary_var.get(),
                    values[0]  # Use the 'id' column
                )
            )
            self.conn.commit()
            # self.clear_fields() # Keep fields populated after update
            messagebox.showinfo("Success", "Employee updated successfully!")
            self.load_employees() # Reload table AFTER showing the message
        except sqlite3.Error as e:
            messagebox.showerror("Database Error", str(e))

    def delete_employee(self):
        selected = self.employee_table.focus()
        if selected == "":
            messagebox.showerror("Error", "No record selected!")
            return
        values = self.employee_table.item(selected, 'values')
        try:
            self.cursor.execute("DELETE FROM employees WHERE id = ?", (values[0],))  # Use the 'id' column
            self.conn.commit()
            self.load_employees()
            self.clear_fields()
            messagebox.showinfo("Success", "Employee deleted successfully!")
        except sqlite3.Error as e:
            messagebox.showerror("Database Error", str(e))

    def clear_fields(self):
        self.name_var.set("")
        self.phone_var.set("")
        self.email_var.set("")
        self.position_var.set("")
        self.salary_var.set(0.0)

    def __del__(self):
        # Close the database connection when the window is closed
        if hasattr(self, 'conn') and self.conn: # Check if conn exists and is not None
            self.conn.close()
