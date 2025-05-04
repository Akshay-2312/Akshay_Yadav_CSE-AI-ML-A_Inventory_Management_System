# dashboard.py
import tkinter as tk
from tkinter import messagebox, ttk, font as tkFont
import db # Import the database module

# Placeholder imports for potential future command linking
import inventory
import sales
import employee
import supplier
import reports
# import settings # Placeholder for potential future settings module

class DashboardWindow:
    def __init__(self, root):
        self.root = root
        self.root.title("D R Medical Store - Inventory Dashboard")
        self.root.geometry("1200x750") # Increased size for more content
        self.root.resizable(True, True)
        self.root.configure(bg="#f0f4f7") # Light background for the main window

        # --- Fonts ---
        self.title_font = tkFont.Font(family="Helvetica", size=16, weight="bold")
        self.card_title_font = tkFont.Font(family="Helvetica", size=11, weight="bold")
        self.card_value_font = tkFont.Font(family="Helvetica", size=14, weight="bold")
        self.card_desc_font = tkFont.Font(family="Helvetica", size=9)
        self.card_change_font = tkFont.Font(family="Helvetica", size=9)

        # --- Store references to summary labels ---
        self.summary_value_labels = [] # To store the value labels for updating
        self.summary_change_labels = [] # To store the change labels (though we'll keep them static for now)

        # --- Header ---
        header_frame = tk.Frame(root, bg="#2c3e50") # Darker blue header
        header_frame.pack(fill=tk.X, pady=(0, 10)) # Add some padding below header
        header_label = tk.Label(header_frame, text="D R Medical Store - Dashboard",
                                font=self.title_font, bg="#2c3e50", fg="white", pady=15)
        header_label.pack()

        # --- Main Content Area ---
        main_content_frame = tk.Frame(root, bg="#f0f4f7", padx=20, pady=10)
        main_content_frame.pack(expand=True, fill=tk.BOTH)

        # --- Summary Cards Section ---
        summary_frame = tk.Frame(main_content_frame, bg="#f0f4f7")
        summary_frame.pack(fill=tk.X, pady=(0, 20)) # Padding below summary cards

        summary_cards_data = [
            {"title": "Total Inventory", "value": "1,234", "change": "+5%", "icon": "📦", "color": "#1abc9c"},
            {"title": "Today's Sales", "value": "₹ 15,670", "change": "+12%", "icon": "💰", "color": "#3498db"},
            {"title": "Low Stock Items", "value": "42", "change": "-2%", "icon": "⚠️", "color": "#e67e22"},
            {"title": "Near Expiry Item", "value": "0", "change": "", "icon": "⏰", "color": "#f39c12"} # Changed title, icon, color, placeholder value/change
        ]

        for i, card_data in enumerate(summary_cards_data):
            card = self.create_summary_card(summary_frame, card_data)
            card.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=10) # Pack cards horizontally

        # --- Action Cards Section ---
        actions_frame = tk.Frame(main_content_frame, bg="#f0f4f7")
        actions_frame.pack(expand=True, fill=tk.BOTH)

        action_cards_data = [
            {"title": "Manage Inventory", "desc": "Add, update, view stock levels.", "icon": "📊", "command": self.manage_inventory},
            {"title": "Sales / Billing", "desc": "Process sales and generate bills.", "icon": "🛒", "command": self.sales_billing},
            {"title": "Manage Employees", "desc": "Add, update employee details.", "icon": "👥", "command": self.manage_employees},
            {"title": "Manage Suppliers", "desc": "Add, update supplier information.", "icon": "🏭", "command": self.manage_suppliers},
            {"title": "View Reports", "desc": "Generate sales, stock reports.", "icon": "📄", "command": self.view_reports},
            {"title": "Logout", "desc": "Log out from the application.", "icon": "🚪", "command": self.logout} # Changed to Logout
        ]

        num_cols = 3
        for index, card_data in enumerate(action_cards_data):
            row = index // num_cols
            col = index % num_cols
            card = self.create_action_card(actions_frame, card_data)

            actions_frame.grid_columnconfigure(col, weight=1, uniform="action_card") # Make columns uniform
            actions_frame.grid_rowconfigure(row, weight=1, uniform="action_card")    # Make rows uniform

            card.grid(row=row, column=col, padx=15, pady=15, sticky="nsew") # Grid layout for action cards

        # --- Footer ---
        footer_frame = tk.Frame(root, bg="#ecf0f1", pady=8)
        footer_frame.pack(fill=tk.X, side=tk.BOTTOM, pady=(10, 0)) # Padding above footer
        footer_label = tk.Label(footer_frame, text="© 2025 D R Medical Store | Inventory Management System",
                                font=("Helvetica", 9), bg="#ecf0f1", fg="#7f8c8d")
        footer_label.pack()

        # --- Initial data load ---
        self.update_summary_cards() # Call the update function after UI is built

    def create_summary_card(self, parent, data):
        card_frame = tk.Frame(parent, bg="white", relief=tk.RIDGE, bd=1, padx=15, pady=15)

        icon_label = tk.Label(card_frame, text=data["icon"], font=("Arial", 24), bg="white", fg=data["color"])
        icon_label.pack(pady=(0, 5))

        title_label = tk.Label(card_frame, text=data["title"], font=self.card_title_font, bg="white", fg="#555")
        title_label.pack(pady=(0, 5))

        value_label = tk.Label(card_frame, text="Loading...", font=self.card_value_font, bg="white", fg="#333") # Initial text
        value_label.pack(pady=(0, 5))
        self.summary_value_labels.append(value_label) # Store the label reference

        # Keep change label static for now as per requirements
        change_label = tk.Label(card_frame, text="+0.0%", font=self.card_change_font, bg="white", fg="#7f8c8d") # Static placeholder
        change_label.pack()
        self.summary_change_labels.append(change_label) # Store reference if needed later

        return card_frame

    def create_action_card(self, parent, data):
        card_frame = tk.Frame(parent, bg="white", relief=tk.RAISED, bd=2, padx=20, pady=20)
        card_frame.bind("<Enter>", lambda e, cf=card_frame: cf.config(bg="#e8f0fe")) # Hover effect
        card_frame.bind("<Leave>", lambda e, cf=card_frame: cf.config(bg="white"))   # Hover effect
        card_frame.bind("<Button-1>", lambda e, cmd=data["command"]: cmd()) # Click effect

        icon_label = tk.Label(card_frame, text=data["icon"], font=("Arial", 30), bg="white")
        icon_label.pack(pady=(0, 10))
        icon_label.bind("<Button-1>", lambda e, cmd=data["command"]: cmd()) # Make icon clickable too

        title_label = tk.Label(card_frame, text=data["title"], font=self.card_title_font, bg="white")
        title_label.pack(pady=(0, 5))
        title_label.bind("<Button-1>", lambda e, cmd=data["command"]: cmd()) # Make title clickable too

        desc_label = tk.Label(card_frame, text=data["desc"], font=self.card_desc_font, bg="white", fg="#666", wraplength=150) # Wrap description
        desc_label.pack()
        desc_label.bind("<Button-1>", lambda e, cmd=data["command"]: cmd()) # Make description clickable too

        # Rebind hover effects for labels as well
        for widget in [icon_label, title_label, desc_label]:
            widget.bind("<Enter>", lambda e, cf=card_frame: cf.config(bg="#e8f0fe"))
            widget.bind("<Leave>", lambda e, cf=card_frame: cf.config(bg="white"))

        return card_frame

    # --- Placeholder Command Methods (Keep relevant ones, add new ones) ---
    def manage_inventory(self):
        # print("Opening Manage Inventory...") # Keep print for debugging if needed
        # Placeholder: Open actual window later
        new_window = tk.Toplevel(self.root)
        inventory.InventoryWindow(new_window)

    def sales_billing(self):
        # print("Opening Sales/Billing...")
        # Placeholder: Open actual window later
        new_window = tk.Toplevel(self.root)
        sales.SalesWindow(new_window)

    def manage_employees(self):
        # print("Opening Manage Employees...")
        # Placeholder: Open actual window later
        new_window = tk.Toplevel(self.root)
        employee.EmployeeWindow(new_window)

    def manage_suppliers(self):
        # print("Opening Manage Suppliers...")
        # Placeholder: Open actual window later
        new_window = tk.Toplevel(self.root)
        supplier.SupplierWindow(new_window)

    def view_reports(self):
        # print("Opening View Reports...")
        # Placeholder: Open actual window later
        new_window = tk.Toplevel(self.root)
        reports.ReportsWindow(new_window)

    def system_settings(self): # New placeholder method
        print("Opening System Settings...")
        messagebox.showinfo("Settings", "System Settings module not yet implemented.")

    def logout(self):
        """Logs the user out (placeholder)."""
        print("Logging out...")
        # In a real app, you'd destroy the dashboard and show the login window
        if messagebox.askokcancel("Logout", "Are you sure you want to logout?"):
            self.root.destroy() # Close the dashboard window
            # Here you would typically re-initialize and show the login window
            # e.g., import login; login.show_login_window()

    # Removed the old logout method as it's replaced by Settings card

    def update_summary_cards(self):
        """Fetches data from db and updates the summary card labels."""
        try:
            # 1. Total Inventory Value
            total_inv_value = db.get_total_inventory_value()
            self.summary_value_labels[0].config(text=f"₹ {total_inv_value:,.2f}")
        except Exception as e:
            print(f"Error fetching total inventory value: {e}")
            self.summary_value_labels[0].config(text="Error")

        try:
            # 2. Today's Sales Value
            today_sales = db.get_todays_sales_value()
            self.summary_value_labels[1].config(text=f"₹ {today_sales:,.2f}")
        except Exception as e:
            print(f"Error fetching today's sales: {e}")
            self.summary_value_labels[1].config(text="Error")

        try:
            # 3. Low Stock Items Count
            low_stock_items = db.get_low_stock_items() # This returns a list of dicts
            low_stock_count = len(low_stock_items)
            self.summary_value_labels[2].config(text=f"{low_stock_count}")
        except Exception as e:
            print(f"Error fetching low stock count: {e}")
            self.summary_value_labels[2].config(text="Error")

        try:
            # 4. Pending Orders (Placeholder)
            # Assuming no direct table for this, using 0 as placeholder
            pending_orders_count = 0 # Placeholder value
            self.summary_value_labels[3].config(text=f"{pending_orders_count}")
        except Exception as e:
            # This block might not be strictly necessary for a placeholder, but good practice
            print(f"Error setting pending orders count: {e}")
            self.summary_value_labels[3].config(text="Error")

        # Note: Percentage change labels remain static as per requirements.

# --- Main execution block (for testing dashboard directly) ---
if __name__ == "__main__":
    root = tk.Tk()
    app = DashboardWindow(root)
    root.mainloop()
