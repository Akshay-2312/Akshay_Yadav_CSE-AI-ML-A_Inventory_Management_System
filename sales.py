# sales.py
import tkinter as tk
from tkinter import ttk, messagebox, simpledialog, Frame, font as tkFont # Import font
import sqlite3
import os
import re

class SalesWindow:
    def __init__(self, root):
        self.root = root
        self.root.title("Sales / Billing")
        self.root.state('zoomed') # Start maximized
        self.root.configure(bg='#E8EAF6') # Light background for the main window

        # --- Fonts ---
        self.default_font = tkFont.nametofont("TkDefaultFont")
        self.default_font.configure(family="Segoe UI", size=10)
        self.title_font = tkFont.Font(family="Segoe UI Semibold", size=18)
        self.header_font = tkFont.Font(family="Segoe UI Semibold", size=12)
        self.button_font = tkFont.Font(family="Segoe UI", size=10, weight="bold")
        self.label_font = tkFont.Font(family="Segoe UI", size=10)
        self.entry_font = tkFont.Font(family="Segoe UI", size=10)
        self.table_header_font = tkFont.Font(family="Segoe UI Semibold", size=10)
        self.cart_font = tkFont.Font(family="Consolas", size=10) # Monospaced for cart

        # --- Style ---
        style = ttk.Style()
        style.theme_use("clam") # Use a modern theme

        # Configure Treeview style
        style.configure("Treeview.Heading", font=self.table_header_font, background="#BBDEFB", foreground="#1A237E", relief="flat", padding=5)
        style.map("Treeview.Heading", relief=[('active','groove'),('pressed','sunken')])
        style.configure("Treeview",
                        background="white",
                        foreground="black",
                        rowheight=25,
                        fieldbackground="white",
                        font=self.label_font)
        style.map("Treeview", background=[('selected', '#90CAF9')]) # Highlight color

        # --- Variables ---
        self.search_var = tk.StringVar()
        self.qty_var = tk.StringVar(value="1") # Default quantity to 1
        self.cart = []
        self.recent_sales = [] # Initialize recent sales list
        self.selected_medicine = None
        self.conn = None # Initialize db connection variables
        self.cursor = None
        self.view_mode = tk.StringVar(value="cart") # Default view mode is cart

        # --- Main Layout Frames ---
        # Using pack for main layout sections for better resizing behavior
        top_frame = tk.Frame(root, bg='#E8EAF6')
        top_frame.pack(fill=tk.X, padx=20, pady=(10, 5))

        content_frame = tk.Frame(root, bg='#E8EAF6')
        content_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=5)

        bottom_frame = tk.Frame(root, bg='#E8EAF6')
        bottom_frame.pack(fill=tk.X, padx=20, pady=(5, 10))

        # --- Top Section: Search and Filters ---
        search_frame = tk.Frame(top_frame, bg='#E8EAF6')
        search_frame.pack(fill=tk.X)

        search_entry = tk.Entry(search_frame, textvariable=self.search_var, font=self.entry_font, width=50, bd=1, relief=tk.SOLID)
        search_entry.pack(side=tk.LEFT, padx=(0, 10), ipady=4)
        search_entry.insert(0, "Search Medicine...") # Placeholder text
        search_entry.bind("<FocusIn>", lambda _: search_entry.delete('0', 'end') if search_entry.get() == "Search Medicine..." else None)
        search_entry.bind("<FocusOut>", lambda _: search_entry.insert(0, "Search Medicine...") if not search_entry.get() else None)

        search_button = tk.Button(search_frame, text="Search", command=self.search_medicine, bg="#2196F3", fg="white", font=self.button_font, width=10, relief=tk.FLAT, padx=10, pady=3)
        search_button.pack(side=tk.LEFT, padx=5)

        filters_button = tk.Button(search_frame, text="Filters", command=self.show_filters, bg="#FFB74D", fg="#424242", font=self.button_font, width=10, relief=tk.FLAT, padx=10, pady=3)
        filters_button.pack(side=tk.LEFT, padx=5)

        # --- Content Frame Layout (Left: Table/Controls, Right: Billing) ---
        left_panel = tk.Frame(content_frame, bg='#FFFFFF', bd=2, relief=tk.GROOVE)
        left_panel.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 10))

        right_panel = tk.Frame(content_frame, bg='#FFFFFF', bd=2, relief=tk.GROOVE)
        right_panel.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=(10, 0), ipadx=10, ipady=10) # Added padding inside

        # --- Left Panel: Medicine List Table ---
        table_frame = tk.Frame(left_panel, bg='white')
        table_frame.pack(fill=tk.BOTH, expand=True, pady=(10, 5), padx=10)

        # Add scrollbar
        scrollbar_y = ttk.Scrollbar(table_frame, orient=tk.VERTICAL)
        scrollbar_x = ttk.Scrollbar(table_frame, orient=tk.HORIZONTAL)

        self.medicine_table = ttk.Treeview(table_frame,
                                           columns=("Name", "Batch", "Expiry", "Qty", "Price"),
                                           show="headings",
                                           yscrollcommand=scrollbar_y.set,
                                           xscrollcommand=scrollbar_x.set,
                                           selectmode="browse") # Only allow single selection

        scrollbar_y.config(command=self.medicine_table.yview)
        scrollbar_x.config(command=self.medicine_table.xview)

        scrollbar_y.pack(side=tk.RIGHT, fill=tk.Y)
        scrollbar_x.pack(side=tk.BOTTOM, fill=tk.X)

        self.medicine_table.heading("Name", text="Medicine Name", anchor=tk.W)
        self.medicine_table.heading("Batch", text="Batch No", anchor=tk.W)
        self.medicine_table.heading("Expiry", text="Expiry Date", anchor=tk.CENTER)
        self.medicine_table.heading("Qty", text="Available Qty", anchor=tk.CENTER)
        self.medicine_table.heading("Price", text="Price per Unit", anchor=tk.E)

        self.medicine_table.column("Name", width=250, stretch=tk.YES, anchor=tk.W)
        self.medicine_table.column("Batch", width=120, stretch=tk.YES, anchor=tk.W)
        self.medicine_table.column("Expiry", width=100, anchor=tk.CENTER)
        self.medicine_table.column("Qty", width=80, anchor=tk.CENTER)
        self.medicine_table.column("Price", width=100, anchor=tk.E)

        self.medicine_table.pack(fill=tk.BOTH, expand=True)
        self.medicine_table.bind("<<TreeviewSelect>>", self.on_medicine_select)

        # --- Left Panel: Quantity Control ---
        quantity_frame = tk.Frame(left_panel, bg="#FFFFFF", pady=5, padx=10)
        quantity_frame.pack(fill=tk.X)

        tk.Label(quantity_frame, text="Quantity Control:", font=self.label_font, bg="white").pack(side=tk.LEFT, padx=(0, 10))

        self.minus_btn = tk.Button(quantity_frame, text="-", command=self.decrease_quantity,
                                   font=self.button_font, bg="#FF7043", fg="white", width=3, relief=tk.FLAT)
        self.minus_btn.pack(side=tk.LEFT, padx=2)

        # Changed Label to Entry for quantity
        self.qty_entry = tk.Entry(quantity_frame, textvariable=self.qty_var, font=self.entry_font, width=5, bd=1, relief=tk.SOLID, justify='center')
        self.qty_entry.pack(side=tk.LEFT, padx=2, ipady=2)
        # Add validation later if needed

        self.plus_btn = tk.Button(quantity_frame, text="+", command=self.increase_quantity,
                                  font=self.button_font, bg="#66BB6A", fg="white", width=3, relief=tk.FLAT)
        self.plus_btn.pack(side=tk.LEFT, padx=2)

        # --- Left Panel: Action Buttons (Add to Cart) ---
        action_button_frame = tk.Frame(left_panel, bg="#FFFFFF", pady=5, padx=10)
        action_button_frame.pack(fill=tk.X)

        self.add_to_cart_btn = tk.Button(action_button_frame, text="Add to Cart", command=self.add_selected_quantity,
                                         bg="#4CAF50", fg="white", font=self.button_font, width=15, relief=tk.FLAT, padx=10, pady=3)
        self.add_to_cart_btn.pack(side=tk.LEFT, padx=(0, 10))

        # --- Right Panel: Billing Details ---
        # Header frame with title and toggle button
        header_frame = tk.Frame(right_panel, bg='white')
        header_frame.pack(fill=tk.X, pady=(5, 10))

        tk.Label(header_frame, text="Billing Details", font=self.header_font, bg="white", fg="#1A237E").pack(side=tk.LEFT)

        # Toggle button frame
        toggle_frame = tk.Frame(header_frame, bg='white')
        toggle_frame.pack(side=tk.RIGHT, padx=10)

        # Radio buttons for view mode
        cart_radio = tk.Radiobutton(toggle_frame, text="Cart View", variable=self.view_mode, value="cart",
                                   command=self.toggle_view_mode, bg="white", font=self.label_font)
        cart_radio.pack(side=tk.LEFT, padx=5)

        sales_radio = tk.Radiobutton(toggle_frame, text="Recent Sales", variable=self.view_mode, value="sales",
                                    command=self.toggle_view_mode, bg="white", font=self.label_font)
        sales_radio.pack(side=tk.LEFT, padx=5)

        # Frame for the cart text area with scrollbar
        cart_text_frame = tk.Frame(right_panel, bg='white')
        cart_text_frame.pack(fill=tk.BOTH, expand=True, pady=5)

        cart_scrollbar = ttk.Scrollbar(cart_text_frame)
        cart_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        self.cart_text = tk.Text(cart_text_frame, font=self.cart_font, wrap=tk.WORD, bd=0, yscrollcommand=cart_scrollbar.set, state=tk.DISABLED, bg="#F5F5F5") # Start disabled, light grey bg
        self.cart_text.pack(fill=tk.BOTH, expand=True)
        cart_scrollbar.config(command=self.cart_text.yview)
        self.show_cart() # Initialize with "No items" message

        # --- Right Panel: Billing Buttons ---
        self.billing_buttons_frame = tk.Frame(right_panel, bg="white")
        self.billing_buttons_frame.pack(fill=tk.X, pady=5)

        # Cart mode buttons
        self.generate_bill_btn = tk.Button(self.billing_buttons_frame, text="Generate Bill", command=self.generate_bill,
                                           bg="#4CAF50", fg="white", font=self.button_font, width=15, relief=tk.FLAT, padx=10, pady=3)
        self.generate_bill_btn.pack(side=tk.LEFT, padx=(0, 10))

        self.clear_cart_btn = tk.Button(self.billing_buttons_frame, text="Clear Cart", command=self.clear_cart_action,
                                        bg="#F44336", fg="white", font=self.button_font, width=15, relief=tk.FLAT, padx=10, pady=3)
        self.clear_cart_btn.pack(side=tk.LEFT)

        # --- Bottom Buttons ---
        back_button = tk.Button(bottom_frame, text="Back to Dashboard", command=self.go_back, bg="#3498db", fg="white", font=self.button_font, relief=tk.FLAT, padx=10, pady=3)
        back_button.pack(side=tk.LEFT, padx=(0, 10))

        # --- Initialize ---
        self.connect_db() # Connect to DB
        if self.conn: # Only load if connection succeeded
            self.create_table()
            self.load_inventory()
            self.load_sales() # Load recent sales data for sales view

    # --- Database and Helper Methods ---
    def connect_db(self):
        try:
            script_dir = os.path.dirname(os.path.abspath(__file__))
            db_path = os.path.join(script_dir, "db", "store.db")
            self.conn = sqlite3.connect(db_path)
            self.cursor = self.conn.cursor()
        except sqlite3.Error as e:
            messagebox.showerror("Database Error", f"Failed to connect to database: {e}\nAttempted Path: {db_path}")
            self.conn = None
            self.cursor = None
            # Disable DB-dependent buttons if connection fails? (Consider adding this)

    def create_table(self):
        if not self.cursor: return
        try:
            # Ensure inventory table exists
            self.cursor.execute('''
                CREATE TABLE IF NOT EXISTS inventory (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT NOT NULL,
                    batch_no TEXT NOT NULL,
                    expiry_date TEXT NOT NULL,
                    quantity INTEGER NOT NULL,
                    price REAL NOT NULL,
                    UNIQUE(name, batch_no)
                )
            ''')
            # Ensure sales table exists
            self.cursor.execute('''
                CREATE TABLE IF NOT EXISTS sales (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    medicine_id INTEGER,
                    quantity_sold INTEGER,
                    amount REAL,
                    sale_date TEXT DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (medicine_id) REFERENCES inventory(id) ON DELETE SET NULL
                )
            ''')
            # Attempt to add the 'amount' column if it doesn't exist (idempotent)
            try:
                self.cursor.execute("ALTER TABLE sales ADD COLUMN amount REAL")
            except sqlite3.OperationalError as e:
                if "duplicate column name" not in str(e).lower(): raise e # Re-raise if not duplicate column error
            self.conn.commit()
        except sqlite3.Error as e:
            messagebox.showerror("Database Error", f"Failed to create/verify tables: {e}")
            # Rollback might be needed here if partial changes occurred
            if self.conn: self.conn.rollback()


    def load_inventory(self):
        if not self.cursor: return
        try:
            # Clear existing table content first
            for item in self.medicine_table.get_children():
                self.medicine_table.delete(item)
            # Fetch only items with quantity > 0
            self.cursor.execute("SELECT name, batch_no, expiry_date, quantity, price FROM inventory WHERE quantity > 0 ORDER BY name")
            rows = self.cursor.fetchall()
            for row in rows:
                # Format price to 2 decimal places for display
                formatted_row = list(row)
                formatted_row[4] = f"{row[4]:.2f}" # Format price
                self.medicine_table.insert('', 'end', values=formatted_row)
        except sqlite3.Error as e:
            messagebox.showerror("Database Error", f"Error loading inventory: {str(e)}")

    def refresh_medicine_table(self):
        # This function essentially reloads the inventory from DB
        self.load_inventory()

    def search_medicine(self):
        if not self.cursor:
             messagebox.showerror("Database Error", "Database connection not available.")
             return
        keyword = self.search_var.get()
        if not keyword or keyword == "Search Medicine...":
            self.load_inventory() # Show all if search is empty
            return

        try:
            # Clear existing table content
            for item in self.medicine_table.get_children():
                self.medicine_table.delete(item)

            # Query the database for matching medicines with quantity > 0
            self.cursor.execute("""
                SELECT name, batch_no, expiry_date, quantity, price
                FROM inventory
                WHERE name LIKE ? AND quantity > 0
                ORDER BY name
            """, ('%' + keyword + '%',))
            results = self.cursor.fetchall()

            # Populate the table with live results
            for med in results:
                 # Format price to 2 decimal places for display
                formatted_med = list(med)
                formatted_med[4] = f"{med[4]:.2f}" # Format price
                self.medicine_table.insert('', 'end', values=formatted_med)

        except sqlite3.Error as e:
            messagebox.showerror("Database Error", f"Error searching inventory: {str(e)}")

    def on_medicine_select(self, _):
        selected_item_id = self.medicine_table.focus()
        if selected_item_id:
            self.selected_medicine = self.medicine_table.item(selected_item_id, 'values')
            # Maybe highlight or fetch more details if needed
            self.qty_var.set("1") # Reset quantity to 1 when new medicine is selected
        else:
            self.selected_medicine = None

    def increase_quantity(self):
        try:
            current_qty = int(self.qty_var.get())
            if self.selected_medicine:
                available_qty = int(self.selected_medicine[3])
                if current_qty < available_qty:
                    self.qty_var.set(str(current_qty + 1))
                else:
                    messagebox.showwarning("Limit Reached", f"Available quantity is {available_qty}.")
            else:
                 # If no medicine selected, just increment, maybe cap later?
                 self.qty_var.set(str(current_qty + 1))
        except ValueError:
            messagebox.showerror("Invalid Input", "Quantity must be a number.")
            self.qty_var.set("1") # Reset to default
        except IndexError:
             messagebox.showwarning("Selection Error", "Could not read available quantity. Please re-select the medicine.")
             self.selected_medicine = None # Clear selection


    def decrease_quantity(self):
        try:
            current_qty = int(self.qty_var.get())
            if current_qty > 1: # Minimum quantity is 1
                self.qty_var.set(str(current_qty - 1))
            else:
                 self.qty_var.set("1") # Don't go below 1
        except ValueError:
            messagebox.showerror("Invalid Input", "Quantity must be a number.")
            self.qty_var.set("1") # Reset to default

    def add_selected_quantity(self):
        if not self.selected_medicine:
            messagebox.showwarning("No Selection", "Please select a medicine from the table first.")
            return

        try:
            qty_to_add = int(self.qty_var.get())
            if qty_to_add <= 0:
                messagebox.showwarning("Invalid Quantity", "Please enter a quantity greater than 0.")
                return
        except ValueError:
            messagebox.showerror("Invalid Input", "Quantity must be a valid number.")
            self.qty_var.set("1")
            return

        med_name, batch, expiry, available_qty_str, price_str = self.selected_medicine
        available_qty = int(available_qty_str)
        price = float(price_str)

        # Check if quantity is available
        if qty_to_add > available_qty:
            messagebox.showwarning("Insufficient Stock", f"Cannot add {qty_to_add}. Only {available_qty} units available for {med_name} ({batch}).")
            return

        # Check if item already in cart (same name and batch)
        existing_item_index = -1
        for i, item in enumerate(self.cart):
            if item['name'] == med_name and item['batch'] == batch:
                existing_item_index = i
                break

        if existing_item_index != -1:
            # Update quantity if item exists
            new_qty = self.cart[existing_item_index]['qty'] + qty_to_add
            if new_qty > available_qty:
                 messagebox.showwarning("Insufficient Stock", f"Cannot add {qty_to_add}. Only {available_qty - self.cart[existing_item_index]['qty']} more units available for {med_name} ({batch}) in stock (already {self.cart[existing_item_index]['qty']} in cart).")
                 return
            self.cart[existing_item_index]['qty'] = new_qty
            messagebox.showinfo("Cart Updated", f"Updated quantity for {med_name} ({batch}) to {new_qty}.")
        else:
            # Add new item to cart
            item = {
                'name': med_name,
                'batch': batch,
                'expiry': expiry,
                'qty': qty_to_add,
                'price': price,
                'available': available_qty # Store original available qty for reference if needed
            }
            self.cart.append(item)
            messagebox.showinfo("Item Added", f"{qty_to_add} units of {med_name} ({batch}) added to cart.")

        # Update the cart display
        self.show_cart()

        # Reset quantity input and selection state
        self.qty_var.set("1")
        # Optionally clear selection or keep it? Let's keep it for now.
        # self.selected_medicine = None
        # self.medicine_table.selection_remove(self.medicine_table.focus())


    def show_cart(self):
        try:
            self.cart_text.config(state=tk.NORMAL) # Enable editing
            self.cart_text.delete("1.0", tk.END)
            total = 0

            if not self.cart:
                # Display "No items in cart" message centered
                self.cart_text.insert(tk.END, "\n\n\n" + " " * 10 + "No items in cart")
                # Add an icon placeholder (using text for now)
                self.cart_text.insert(tk.END, "\n\n" + " " * 15 + "[🛒]")
                self.cart_text.tag_configure("center", justify='center', font=(self.cart_font.cget("family"), 12))
                self.cart_text.tag_add("center", "1.0", "end")

            else:
                # Header
                header = f"{'Medicine':<20} {'Batch':<12} {'Qty':>4} {'Price':>8} {'Amount':>10}\n"
                separator = "-" * 60 + "\n" # Adjusted separator length
                self.cart_text.insert(tk.END, header)
                self.cart_text.insert(tk.END, separator)

                # Items
                for item in self.cart:
                    subtotal = item['qty'] * item['price']
                    line = f"{item['name'][:19]:<20} {item['batch'][:11]:<12} {item['qty']:>4} {item['price']:>8.2f} {subtotal:>10.2f}\n"
                    self.cart_text.insert(tk.END, line)
                    total += subtotal

                # Footer
                self.cart_text.insert(tk.END, separator)
                self.cart_text.insert(tk.END, f"{'Total Amount:':>50} ₹{total:>8.2f}")

            self.cart_text.config(state=tk.DISABLED) # Disable editing
        except (tk.TclError, AttributeError) as e:
            # Handle the case where the text widget might not exist or be accessible
            print(f"Error updating cart view: {e}")


    def generate_bill(self):
        # Check current view mode
        if self.view_mode.get() == "sales":
            # In sales view, this button refreshes the sales data
            self.load_sales()
            self.show_sales()
            return

        # In cart view, proceed with bill generation
        if not self.cart:
            messagebox.showerror("Empty Cart", "Cannot generate bill. The cart is empty.")
            return

        if not self.conn or not self.cursor:
            messagebox.showerror("Database Error", "Database connection not available.")
            return

        confirm = messagebox.askyesno("Confirm Sale", "Proceed with generating the bill and completing the sale?")
        if not confirm:
            return

        try:
            self.cursor.execute("BEGIN TRANSACTION")

            for item in self.cart:
                med_name = item['name']
                batch = item['batch']
                qty_sold = item['qty']
                price = item['price']
                amount = qty_sold * price

                # Get medicine ID and current quantity again for safety check
                self.cursor.execute("SELECT id, quantity FROM inventory WHERE name = ? AND batch_no = ?", (med_name, batch))
                result = self.cursor.fetchone()

                if not result:
                    raise Exception(f"Critical Error: Medicine {med_name} ({batch}) disappeared from inventory during transaction.")

                med_id, current_qty = result

                if qty_sold > current_qty:
                    raise Exception(f"Critical Error: Insufficient stock for {med_name} ({batch}). Available: {current_qty}, Tried to sell: {qty_sold}.")

                # Update inventory quantity
                self.cursor.execute("UPDATE inventory SET quantity = quantity - ? WHERE id = ?", (qty_sold, med_id))

                # Insert into sales record
                self.cursor.execute(
                    "INSERT INTO sales (medicine_id, quantity_sold, amount) VALUES (?, ?, ?)",
                    (med_id, qty_sold, amount)
                )

            # Commit transaction
            self.conn.commit()

            messagebox.showinfo("Success", "Bill generated and sale recorded successfully!")

            # Clear cart, refresh inventory display, show empty cart
            self.cart.clear()
            self.load_inventory() # Refresh the medicine table
            self.load_sales() # Refresh sales data
            self.show_cart() # Update cart display to show "No items"

        except sqlite3.Error as db_err:
            if self.conn: self.conn.rollback() # Rollback on database error
            messagebox.showerror("Database Error", f"Failed to complete sale due to database error: {db_err}")
        except Exception as e:
            if self.conn: self.conn.rollback() # Rollback on other errors
            messagebox.showerror("Transaction Error", f"Failed to generate bill: {str(e)}")


    def clear_cart_action(self):
        """ Handles the action for the second button in the billing panel.
            In cart mode: Clears the cart
            In sales mode: Exports sales data
        """
        # Check current view mode
        if self.view_mode.get() == "sales":
            # In sales view, this button exports sales data
            self.export_sales_data()
            return

        # In cart view, clear the cart
        if not self.cart:
            messagebox.showinfo("Info", "Cart is already empty.")
            return

        confirm = messagebox.askyesno("Confirm Clear Cart", "Are you sure you want to remove all items from the current bill?")
        if confirm:
            self.cart.clear()
            self.show_cart()
            messagebox.showinfo("Cart Cleared", "All items removed from the cart.")

    def export_sales_data(self):
        """Export recent sales data to a CSV file"""
        if not self.recent_sales:
            messagebox.showinfo("No Data", "There are no sales records to export.")
            return

        try:
            import csv
            from datetime import datetime

            # Generate filename with current date/time
            current_time = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"sales_export_{current_time}.csv"

            with open(filename, 'w', newline='') as csvfile:
                writer = csv.writer(csvfile)
                # Write header
                writer.writerow(['Medicine Name', 'Batch No', 'Quantity', 'Price', 'Amount', 'Sale Date'])

                # Write data
                for item in self.recent_sales:
                    writer.writerow([
                        item['name'],
                        item['batch'],
                        item['qty'],
                        item['price'],
                        item['amount'],
                        item['date']
                    ])

            messagebox.showinfo("Export Successful", f"Sales data exported to {filename}")

        except Exception as e:
            messagebox.showerror("Export Error", f"Failed to export sales data: {str(e)}")

    def load_sales(self):
        """Load recent sales data from the database"""
        if not self.cursor: return

        try:
            # Query to get recent sales with medicine names
            self.cursor.execute("""
                SELECT i.name, i.batch_no, s.quantity_sold, i.price, s.amount, s.sale_date
                FROM sales s
                JOIN inventory i ON s.medicine_id = i.id
                ORDER BY s.sale_date DESC
                LIMIT 50
            """)

            self.recent_sales = []
            rows = self.cursor.fetchall()

            for row in rows:
                sale_item = {
                    'name': row[0],
                    'batch': row[1],
                    'qty': row[2],
                    'price': row[3],
                    'amount': row[4],
                    'date': row[5]
                }
                self.recent_sales.append(sale_item)

        except sqlite3.Error as e:
            messagebox.showerror("Database Error", f"Error loading sales data: {str(e)}")
            self.recent_sales = []

    def toggle_view_mode(self):
        """Toggle between cart view and sales view"""
        mode = self.view_mode.get()

        if mode == "cart":
            # Show cart buttons
            self.generate_bill_btn.config(text="Generate Bill")
            self.clear_cart_btn.config(text="Clear Cart")
            self.show_cart()
        else:  # mode == "sales"
            # Show sales view buttons
            self.generate_bill_btn.config(text="Refresh Sales")
            self.clear_cart_btn.config(text="Export Sales")
            self.show_sales()

    def show_sales(self):
        """Display recent sales in the cart text area"""
        try:
            self.cart_text.config(state=tk.NORMAL)  # Enable editing
            self.cart_text.delete("1.0", tk.END)
            total = 0

            if not self.recent_sales:
                # Display "No sales data" message centered
                self.cart_text.insert(tk.END, "\n\n\n" + " " * 10 + "No recent sales data")
                self.cart_text.insert(tk.END, "\n\n" + " " * 15 + "[📊]")
                self.cart_text.tag_configure("center", justify='center', font=(self.cart_font.cget("family"), 12))
                self.cart_text.tag_add("center", "1.0", "end")
            else:
                # Header
                header = f"{'Medicine':<20} {'Batch':<10} {'Qty':>4} {'Price':>8} {'Amount':>10} {'Date':>12}\n"
                separator = "-" * 70 + "\n"
                self.cart_text.insert(tk.END, header)
                self.cart_text.insert(tk.END, separator)

                # Items
                for item in self.recent_sales:
                    # Format date to show only date part if it's a full timestamp
                    date_str = item['date'] if item['date'] is not None else ""
                    if date_str and ' ' in date_str:  # If format is like "2023-05-01 14:30:00"
                        date_str = date_str.split(' ')[0]

                    line = f"{item['name'][:19]:<20} {item['batch'][:9]:<10} {item['qty']:>4} {item['price']:>8.2f} {item['amount']:>10.2f} {date_str:>12}\n"
                    self.cart_text.insert(tk.END, line)
                    total += item['amount']

                # Footer
                self.cart_text.insert(tk.END, separator)
                self.cart_text.insert(tk.END, f"{'Total Amount:':>50} ₹{total:>8.2f}")

            self.cart_text.config(state=tk.DISABLED)  # Disable editing
        except (tk.TclError, AttributeError) as e:
            # Handle the case where the text widget might not exist or be accessible
            print(f"Error updating sales view: {e}")

    def show_filters(self):
        """ Placeholder for filter functionality """
        messagebox.showinfo("Filters", "Filter functionality is not yet implemented.")

    def go_back(self):
        """ Closes the current sales window. """
        # In a real multi-window app, this might hide the window
        # and show the dashboard window instead.
        self.root.destroy()

    def __del__(self):
        # Close the database connection when the window object is destroyed
        if self.conn:
            self.conn.close()

# --- Main execution ---
if __name__ == "__main__":
    app_root = tk.Tk()
    # Ensure the 'db' directory exists
    script_dir = os.path.dirname(os.path.abspath(__file__))
    db_dir = os.path.join(script_dir, "db")
    if not os.path.exists(db_dir):
        os.makedirs(db_dir)
    sales_window = SalesWindow(app_root)
    app_root.mainloop()
