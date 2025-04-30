# employee.py
import tkinter as tk
from tkinter import ttk, messagebox
import sqlite3

class EmployeeWindow:
    def __init__(self, root):
        self.root = root
        self.root.title("Manage Employees")
        self.root.geometry("800x600")

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
        self.conn = sqlite3.connect("db/store.db")
        self.cursor = self.conn.cursor()
        self.create_table()
        self.load_employees()

        # Window state
        self.maximize_btn = tk.Button(self.root, text="🗖", command=self.toggle_maximize, font=("Helvetica", 14))
        self.maximize_btn.place(x=10, y=10)
        self.is_maximized = False
        self.original_form_pos = (10, 70)
        self.original_table_pos = (430, 70)

    def toggle_maximize(self):
        if not self.is_maximized:
            self.root.state('zoomed')
            self.center_main_content()
            self.employee_table.column("ID", width=60)
            self.employee_table.column("Name", width=180)
            self.employee_table.column("Email", width=180)
            self.employee_table.column("Phone", width=120)
            self.employee_table.column("Position", width=120)
            self.employee_table.column("Salary", width=120)
            for child in self.list_frame.winfo_children():
                if isinstance(child, tk.Scrollbar) and child.cget('orient') == 'horizontal':
                    self.employee_table.configure(xscrollcommand=child.set)
                    child.config(command=self.employee_table.xview)
            self.employee_table.update_idletasks()
            self.employee_table.xview_moveto(0)
            self.is_maximized = True
        else:
            self.root.state('normal')
            self.form_frame.place(x=10, y=70, width=400, height=500)
            self.list_frame.place(x=430, y=70, width=350, height=500)
            self.employee_table.column("ID", width=50)
            self.employee_table.column("Name", width=150)
            self.employee_table.column("Email", width=150)
            self.employee_table.column("Phone", width=100)
            self.employee_table.column("Position", width=100)
            self.employee_table.column("Salary", width=100)
            for child in self.list_frame.winfo_children():
                if isinstance(child, tk.Scrollbar) and child.cget('orient') == 'horizontal':
                    self.employee_table.configure(xscrollcommand=child.set)
                    child.config(command=self.employee_table.xview)
            self.employee_table.update_idletasks()
            self.employee_table.xview_moveto(0)
            self.is_maximized = False

    def center_main_content(self):
        self.root.update_idletasks()
        win_width = self.root.winfo_width()
        win_height = self.root.winfo_height()
        form_width = int(win_width * 0.32)
        table_width = int(win_width * 0.56)
        frame_height = int(win_height * 0.8)
        x_start = (win_width - (form_width + table_width + 40)) // 2
        y_center = (win_height - frame_height) // 2
        self.form_frame.place(x=x_start, y=y_center, width=form_width, height=frame_height)
        self.list_frame.place(x=x_start + form_width + 40, y=y_center, width=table_width, height=frame_height)
        self.employee_table.column("ID", width=int(table_width * 0.09))
        self.employee_table.column("Name", width=int(table_width * 0.23))
        self.employee_table.column("Email", width=int(table_width * 0.23))
        self.employee_table.column("Phone", width=int(table_width * 0.15))
        self.employee_table.column("Position", width=int(table_width * 0.15))
        self.employee_table.column("Salary", width=int(table_width * 0.15))

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
            self.load_employees()
            self.clear_fields()
            messagebox.showinfo("Success", "Employee added successfully!")
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
            self.load_employees()
            self.clear_fields()
            messagebox.showinfo("Success", "Employee updated successfully!")
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
        self.conn.close()
