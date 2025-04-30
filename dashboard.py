# dashboard.py
import tkinter as tk
from tkinter import messagebox

class DashboardWindow:
    def __init__(self, root):
        self.root = root
        self.root.title("Dashboard - D R Medical Store")
        self.root.geometry("1200x700")  # Increased window size for better display
        self.root.resizable(False, False)

        # --- Updated Top Title ---
        self.root.configure(bg="#f0f4f7")  # Set background color
        title = tk.Label(root, text="D R Medical Store - Inventory Dashboard", 
                         font=("Helvetica", 24, "bold"), bg="#2c3e50", fg="white", pady=15)
        title.pack(fill=tk.X)

        # --- Updated Buttons for Different Operations ---
        btn_frame = tk.Frame(root, bg="#f0f4f7", pady=30)
        btn_frame.pack()

        button_style = {
            "font": ("Helvetica", 16, "bold"),
            "bg": "#3498db",
            "fg": "white",
            "activebackground": "#2980b9",
            "relief": tk.FLAT,
            "width": 25,
            "height": 2
        }

        buttons = [
            ("Manage Inventory", self.manage_inventory),
            ("Sales/Billing", self.sales),
            ("Manage Employees", self.manage_employee),
            ("Manage Suppliers", self.manage_supplier),
            ("View Reports", self.view_reports),
            ("Logout", self.logout)
        ]

        for i, (text, command) in enumerate(buttons):
            btn = tk.Button(btn_frame, text=text, command=command, **button_style)
            btn.grid(row=i // 2, column=i % 2, padx=30, pady=20)

            # Adding hover effect to the buttons
            def on_enter(e, button=btn):
                button["bg"] = "#2980b9"

            def on_leave(e, button=btn):
                button["bg"] = "#3498db"

            btn.bind("<Enter>", on_enter)
            btn.bind("<Leave>", on_leave)

        footer = tk.Label(root, text="© 2025 D R Medical Store", font=("Helvetica", 12), bg="#f0f4f7", fg="#95a5a6")
        footer.pack(side=tk.BOTTOM, pady=15)

    # --- Functions for Buttons ---
    def manage_inventory(self):
        import inventory
        new_window = tk.Toplevel(self.root)
        inventory.InventoryWindow(new_window)

    def sales(self):
        import sales
        new_window = tk.Toplevel(self.root)
        sales.SalesWindow(new_window)

    def manage_employee(self):
        import employee
        new_window = tk.Toplevel(self.root)
        employee.EmployeeWindow(new_window)

    def manage_supplier(self):
        import supplier
        new_window = tk.Toplevel(self.root)
        supplier.SupplierWindow(new_window)

    def view_reports(self):
        import reports
        new_window = tk.Toplevel(self.root)
        reports.ReportsWindow(new_window)

    def logout(self):
        confirm = messagebox.askyesno("Logout", "Are you sure you want to logout?")
        if confirm:
            self.root.destroy()


