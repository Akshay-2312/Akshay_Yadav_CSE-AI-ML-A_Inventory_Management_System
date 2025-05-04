# inventory.py
import tkinter as tk
from tkinter import ttk, messagebox
import datetime
import sqlite3
import os # Add os import
import csv # For export
from tkinter import simpledialog # For filter

class InventoryWindow:
    def __init__(self, root):
        self.root = root
        self.root.title("Manage Inventory")
        self.root.state('zoomed')
        self.root.resizable(True, True)

        # Medicine variables
        self.med_name_var = tk.StringVar()
        self.batch_no_var = tk.StringVar()
        self.expiry_date_var = tk.StringVar()
        self.quantity_var = tk.IntVar()
        self.price_var = tk.DoubleVar()
        self.selected_item_id = None # Add variable to store selected item ID

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
        tk.Button(form_frame, text="Add Medicine", command=self.add_medicine, width=15, bg="#4CAF50", fg="white", font=("Helvetica", 11, "bold")).grid(row=5, column=0, pady=15, padx=5)
        tk.Button(form_frame, text="Update Selected", command=self.update_medicine, width=15, bg="#2196F3", fg="white", font=("Helvetica", 11, "bold")).grid(row=5, column=1, pady=15, padx=5)
        tk.Button(form_frame, text="Delete Selected", command=self.delete_medicine, width=15, bg="#F44336", fg="white", font=("Helvetica", 11, "bold")).grid(row=6, column=0, pady=10, padx=5) # Main delete button - keep for now or remove if only row actions desired? Keeping for now.
        tk.Button(form_frame, text="Clear Fields", command=self.clear_fields, width=15, bg="#9C27B0", fg="white", font=("Helvetica", 11, "bold")).grid(row=6, column=1, pady=10, padx=5)
        # Use the new back_to_dashboard method
        back_button = tk.Button(form_frame, text="Back to Dashboard", command=self.back_to_dashboard, bg="#5dade2", fg="white", font=("Helvetica", 11, "bold"), width=20) # Slightly lighter blue
        back_button.grid(row=7, columnspan=2, pady=15)

        # --- Table Frame ---
        self.is_maximized = False
        self.original_table_frame_pos = (450, 70) # Store original pos for restore
        self.table_frame = tk.Frame(root, bd=3, relief=tk.RIDGE)
        # Adjusted width slightly to fit 800px window width better
        self.table_frame.place(x=430, y=70, width=350, height=500)

        # --- Table Buttons Sub-Frame ---
        table_buttons_frame = tk.Frame(self.table_frame)
        table_buttons_frame.grid(row=0, column=0, columnspan=2, sticky="ew", pady=(0, 5)) # Place above treeview

        # Add Filter Entry
        self.filter_var = tk.StringVar()
        filter_entry = tk.Entry(table_buttons_frame, textvariable=self.filter_var, width=15)
        filter_entry.pack(side=tk.LEFT, padx=5)
        # filter_entry.bind("<KeyRelease>", self.filter_data) # REMOVED: Filter on key release

        filter_btn = tk.Button(table_buttons_frame, text="Filter", command=self.filter_data, width=10) # Command triggers filter
        filter_btn.pack(side=tk.LEFT, padx=5)
        export_btn = tk.Button(table_buttons_frame, text="Export", command=self.export_data, width=10)
        export_btn.pack(side=tk.LEFT, padx=5)
        print_btn = tk.Button(table_buttons_frame, text="Print", command=self.print_data, width=10)
        print_btn.pack(side=tk.LEFT, padx=5)
        # --- END ADD ---

        # Add horizontal and vertical scrollbars
        x_scroll = tk.Scrollbar(self.table_frame, orient=tk.HORIZONTAL)
        y_scroll = tk.Scrollbar(self.table_frame, orient=tk.VERTICAL)
        self.medicine_table = ttk.Treeview(
            self.table_frame,
            # Add 'ID' column
            columns=("ID", "Name", "Batch", "Expiry", "Qty", "Price"), # Removed "Actions"
            show="headings",
            xscrollcommand=x_scroll.set,
            yscrollcommand=y_scroll.set,
            style="Excel.Treeview"
        )
        x_scroll.config(command=self.medicine_table.xview)
        y_scroll.config(command=self.medicine_table.yview)
        # Adjust grid placement for treeview and scrollbars
        self.medicine_table.grid(row=1, column=0, sticky="nsew") # CHANGE row=0 to row=1
        y_scroll.grid(row=1, column=1, sticky="ns")             # CHANGE row=0 to row=1
        x_scroll.grid(row=2, column=0, sticky="ew")             # CHANGE row=1 to row=2
        # Adjust row/column configure
        self.table_frame.grid_rowconfigure(0, weight=0) # ADD weight=0 for button row
        self.table_frame.grid_rowconfigure(1, weight=1) # CHANGE row 0 to 1
        self.table_frame.grid_columnconfigure(0, weight=1) # Keep column 0 weight 1

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

        self.medicine_table.heading("ID", text="ID") # Add ID heading
        self.medicine_table.heading("Name", text="Medicine Name")
        self.medicine_table.heading("Batch", text="Batch No")
        self.medicine_table.heading("Expiry", text="Expiry Date")
        self.medicine_table.heading("Qty", text="Quantity")
        self.medicine_table.heading("Price", text="Price")
        # Removed Actions heading
        self.medicine_table.column("ID", width=50, anchor="center") # Add ID column config
        self.medicine_table.column("Name", width=150, anchor="center")
        self.medicine_table.column("Batch", width=100, anchor="center")
        self.medicine_table.column("Expiry", width=120, anchor="center")
        self.medicine_table.column("Qty", width=80, anchor="center")
        self.medicine_table.column("Price", width=80, anchor="center")
        # Removed Actions column config

        self.medicine_table.bind("<ButtonRelease-1>", self.select_row) # This handles row selection for form buttons
        # REMOVED: Double-click binding
        # self.medicine_table.bind("<Double-1>", self.edit_selected_row_via_form)
        # REMOVED: Binding for handling clicks within the actions column
        # self.medicine_table.bind("<Button-1>", self.handle_table_click)
        # Store references to main content frames *before* DB connection
        self.form_frame = form_frame

        # Initialize database connection
        try: # Add try-except block for connection
            # Construct absolute path to the database
            script_dir = os.path.dirname(os.path.abspath(__file__))
            db_path = os.path.join(script_dir, "db", "store.db")
            self.conn = sqlite3.connect(db_path)
            self.cursor = self.conn.cursor()
            self.create_table()
            self.load_inventory()
        except sqlite3.Error as e:
            messagebox.showerror("Database Error", f"Failed to connect to database: {e}\nAttempted Path: {db_path}")
            self.conn = None # Ensure conn is None if connection fails
            self.cursor = None
            # Allow window to open but database operations will fail later if cursor is used without check

        # Center content initially and bind resize event
        self.center_main_content()
        self.root.bind("<Configure>", lambda event: self.on_resize()) # Handle resize

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

    def load_inventory(self, filter_term=None):
        """Loads inventory data into the table, optionally filtering by name."""
        self.medicine_table.delete(*self.medicine_table.get_children())
        try:
            # Fetch ID along with other columns
            query = "SELECT id, name, batch_no, expiry_date, quantity, price FROM inventory"
            params = []
            if filter_term:
                # Filter by name (case-insensitive)
                query += " WHERE LOWER(name) LIKE LOWER(?)"
                params.append(f"%{filter_term}%")
            query += " ORDER BY name" # Optional: order by name

            self.cursor.execute(query, params)
            for row_data in self.cursor.fetchall():
                # row_data contains (id, name, batch, expiry, qty, price)
                # Insert only the database data, no action text needed
                self.medicine_table.insert('', 'end', values=row_data, iid=row_data[0]) # Use DB ID as item ID (iid)
        except sqlite3.Error as e:
            messagebox.showerror("Database Error", f"Failed to load inventory: {e}")
        except Exception as e: # Catch other potential errors
             messagebox.showerror("Error", f"An unexpected error occurred during loading: {e}")


    def add_medicine(self):
        # --- Basic Validation ---
        med_name = self.med_name_var.get().strip()
        batch_no = self.batch_no_var.get().strip()
        expiry_date_str = self.expiry_date_var.get().strip()

        if not med_name or not batch_no:
            messagebox.showerror("Error", "Medicine Name and Batch No are required!")
            return

        # --- Quantity Validation ---
        try:
            quantity = int(self.quantity_var.get())
            if quantity < 0:
                messagebox.showerror("Invalid Input", "Quantity cannot be negative.")
                return
        except ValueError:
            messagebox.showerror("Invalid Input", "Please enter a valid integer for quantity.")
            return

        # --- Price Validation ---
        try:
            price = float(self.price_var.get())
            if price < 0:
                 messagebox.showerror("Invalid Input", "Price cannot be negative.")
                 return
        except ValueError:
            messagebox.showerror("Invalid Input", "Please enter a valid number for price.")
            return

        # --- Date Validation (Basic Format Check) ---
        try:
            if expiry_date_str: # Only validate if not empty
                datetime.datetime.strptime(expiry_date_str, '%Y-%m-%d')
        except ValueError:
            messagebox.showerror("Invalid Input", "Please enter Expiry Date in YYYY-MM-DD format.")
            return

        # --- Database Insertion ---
        try:
            self.cursor.execute(
                "INSERT INTO inventory (name, batch_no, expiry_date, quantity, price) VALUES (?, ?, ?, ?, ?)",
                (med_name, batch_no, expiry_date_str, quantity, price)
            )
            self.conn.commit()
            self.clear_fields() # Clear fields after successful add
            messagebox.showinfo("Success", "Medicine added successfully!")
            self.load_inventory() # Reload table
        except sqlite3.IntegrityError: # Catch potential unique constraint errors if added
             messagebox.showerror("Database Error", f"Medicine '{med_name}' with Batch No '{batch_no}' might already exist.")
        except sqlite3.Error as e:
            messagebox.showerror("Database Error", f"Failed to add medicine: {e}")


    def update_medicine(self):
        # Use stored ID instead of selected Treeview item
        if self.selected_item_id is None:
            messagebox.showerror("Error", "No record selected to update!")
            return

        # --- Get data and Validate (similar to add_medicine) ---
        med_name = self.med_name_var.get().strip()
        batch_no = self.batch_no_var.get().strip()
        expiry_date_str = self.expiry_date_var.get().strip()

        if not med_name or not batch_no:
            messagebox.showerror("Error", "Medicine Name and Batch No are required!")
            return
        try:
            quantity = int(self.quantity_var.get())
            if quantity < 0:
                messagebox.showerror("Invalid Input", "Quantity cannot be negative.")
                return
        except ValueError:
            messagebox.showerror("Invalid Input", "Please enter a valid integer for quantity.")
            return
        try:
            price = float(self.price_var.get())
            if price < 0:
                 messagebox.showerror("Invalid Input", "Price cannot be negative.")
                 return
        except ValueError:
            messagebox.showerror("Invalid Input", "Please enter a valid number for price.")
            return
        try:
            if expiry_date_str:
                datetime.datetime.strptime(expiry_date_str, '%Y-%m-%d')
        except ValueError:
            messagebox.showerror("Invalid Input", "Please enter Expiry Date in YYYY-MM-DD format.")
            return

        # --- Database Update using ID ---
        try:
            self.cursor.execute(
                "UPDATE inventory SET name = ?, batch_no = ?, expiry_date = ?, quantity = ?, price = ? WHERE id = ?",
                (med_name, batch_no, expiry_date_str, quantity, price, self.selected_item_id)
            )
            self.conn.commit()
            self.clear_fields() # Clear fields after successful update
            messagebox.showinfo("Success", "Medicine updated successfully!")
            self.load_inventory() # Reload table
        except sqlite3.Error as e:
            messagebox.showerror("Database Error", f"Failed to update medicine: {e}")


    def delete_medicine(self):
        # Use stored ID and add confirmation
        if self.selected_item_id is None:
            messagebox.showerror("Error", "No record selected to delete!")
            return

        # --- Confirmation ---
        confirm = messagebox.askyesno("Confirm Delete", f"Are you sure you want to delete the selected medicine record (ID: {self.selected_item_id})?")
        if not confirm:
            return

        # --- Database Deletion using ID ---
        try:
            self.cursor.execute("DELETE FROM inventory WHERE id = ?", (self.selected_item_id,))
            self.conn.commit()
            self.load_inventory()
            self.clear_fields() # Clear fields and selection after delete
            messagebox.showinfo("Success", "Medicine deleted successfully!")
        except sqlite3.Error as e:
            messagebox.showerror("Database Error", f"Failed to delete medicine: {e}")


    def clear_fields(self):
        self.med_name_var.set("")
        self.batch_no_var.set("")
        self.expiry_date_var.set("")
        self.quantity_var.set(0) # Use set(0) for IntVar
        self.price_var.set(0.0) # Use set(0.0) for DoubleVar
        self.selected_item_id = None # Reset selected ID
        # Deselect row in table visually
        if self.medicine_table.selection(): # Check if there is a selection
            self.medicine_table.selection_remove(self.medicine_table.selection())


    # REMOVED: handle_table_click function as it's no longer needed

    def select_row(self, event=None): # Modified to accept event from binding
        """Populates the form with data from the selected row."""
        selected_items = self.medicine_table.selection()
        if not selected_items: # No row selected
            self.clear_fields()
            return

        item_iid = selected_items[0] # Get the first selected item's iid

        if not item_iid or not self.medicine_table.exists(item_iid):
            self.clear_fields()
            return

        values = self.medicine_table.item(item_iid, 'values')
        if values:
            # values tuple: (id, name, batch, expiry, qty, price) - No Actions text anymore
            self.selected_item_id = values[0] # Store the ID (which should match item_iid)
            self.med_name_var.set(values[1])
            self.batch_no_var.set(values[2])
            self.expiry_date_var.set(values[3] if values[3] else "")
            try:
                self.quantity_var.set(int(float(values[4])))
            except (ValueError, TypeError):
                self.quantity_var.set(0)
            try:
                self.price_var.set(float(values[5]))
            except (ValueError, TypeError):
                self.price_var.set(0.0)
            # Ensure the row is visually selected (already handled by Treeview selection)
            # self.medicine_table.selection_set(item_iid) # Not needed when using selection()
            self.medicine_table.focus(item_iid) # Keep focus on selected row

    # REMOVED: populate_form_for_edit function

    # REMOVED: delete_single_row function

    # --- Implemented Table Actions ---
    def export_data(self):
        """Exports the current table data (visible rows) to a CSV file."""
        # Ensure exports directory exists
        export_dir = "exports"
        if not os.path.exists(export_dir):
            try:
                os.makedirs(export_dir)
            except OSError as e:
                 messagebox.showerror("Error", f"Could not create export directory '{export_dir}': {e}")
                 return

        # Generate filename with timestamp
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = os.path.join(export_dir, f"inventory_export_{timestamp}.csv")

        try:
            with open(filename, 'w', newline='', encoding='utf-8') as csvfile:
                writer = csv.writer(csvfile)

                # Write header row (matching visible table columns)
                # Get column identifiers ('ID', 'Name', etc.), excluding the 'Actions' column for export
                cols = list(self.medicine_table["columns"])
                if "Actions" in cols:
                    cols.remove("Actions") # Don't export the placeholder Actions column
                headers = [self.medicine_table.heading(col)["text"] for col in cols]
                writer.writerow(headers)

                # Write data rows currently visible in the table, excluding the Actions text
                for item_id in self.medicine_table.get_children():
                    # Get values (no longer includes action text)
                    row_values = self.medicine_table.item(item_id)['values']
                    # No slicing needed anymore
                    writer.writerow(row_values)

            messagebox.showinfo("Export Successful", f"Inventory data exported to:\n{os.path.abspath(filename)}") # Show full path

        except IOError as e:
            messagebox.showerror("Export Error", f"Failed to write CSV file: {e}")
        except Exception as e:
            messagebox.showerror("Export Error", f"An unexpected error occurred during export: {e}")


    def print_data(self):
        # Basic placeholder - Actual printing is complex and platform-dependent
        # Consider libraries like 'reportlab' for PDF generation or platform APIs
        messagebox.showinfo("Info", "Print functionality requires specific libraries (e.g., reportlab for PDF) or platform integration and is not implemented in this basic version.")


    def filter_data(self, event=None):
        """Filters the inventory table based on the text in the filter entry when Filter button is clicked."""
        filter_term = self.filter_var.get().strip()
        self.load_inventory(filter_term=filter_term)
        # Clear selection after filtering to avoid confusion
        self.clear_fields()


    # --- Back to Dashboard ---
    def back_to_dashboard(self):
        # This needs coordination with the main application structure.
        # Option 1: If InventoryWindow is a Toplevel, just destroy it.
        # self.root.destroy() # This closes the Toplevel
        # Option 2: If InventoryWindow is a Frame within the main root,
        #           hide this frame and show the dashboard frame.
        # Example (assuming main_app has methods to switch frames):
        # if hasattr(self.root, 'show_dashboard'): # Check if main app has the method
        #     self.root.show_dashboard()
        # else:
        #     messagebox.showwarning("Navigation Error", "Cannot navigate back to dashboard. Main application structure unknown.")
        # For now, using destroy as it was originally, assuming it might be a Toplevel or standalone
        # If it's part of a larger app, this needs changing in main.py/dashboard.py
        try:
            # Check if it's the main root window or a Toplevel
            if isinstance(self.root, tk.Tk):
                 # If it's the main root, maybe hide instead of destroy?
                 # This depends heavily on the app structure. Destroying main root exits app.
                 # For now, assume it's meant to close this specific view/window.
                 # If it's the *only* window, destroying it quits.
                 # Let's keep destroy() but add a note.
                 print("Attempting to destroy root window (might exit app if it's the main Tk instance).")
                 self.root.destroy()
            elif isinstance(self.root, tk.Toplevel):
                 self.root.destroy() # Close the Toplevel window
            else:
                 # If it's a frame, we can't destroy it directly this way.
                 # Needs coordination. Show warning.
                 messagebox.showwarning("Navigation Error", "Cannot navigate back. Requires coordination with main application.")

        except tk.TclError:
             print("Info: Inventory window already closed or main loop finished.")


    def toggle_maximize(self):
        """Toggles the window between maximized and normal state."""
        if self.is_maximized:
            # Restore (approximate previous state before maximize)
            self.root.state('normal')
            self.maximize_btn.config(text="🗖") # Maximize symbol
        else:
            # Maximize
            self.root.state('zoomed')
            self.maximize_btn.config(text="🗗") # Restore symbol

        self.is_maximized = not self.is_maximized
        # Recenter/adjust layout after state change
        # Use 'after' to allow window manager time to process state change
        self.root.after(50, self.center_main_content)
        self.root.after(60, self.reset_scrollbars)

    def reset_scrollbars(self):
        """Forces the Treeview scrollbars to update if needed."""
        self.root.update_idletasks()
        # Often, simply ensuring the container frame (table_frame) resizes correctly
        # with the window is enough for the Treeview scrollbars.
        pass # No specific action usually needed here

    def center_main_content(self):
        """Adjusts layout, keeping form fixed and expanding table."""
        self.root.update_idletasks() # Ensure window dimensions are current
        window_width = self.root.winfo_width()
        window_height = self.root.winfo_height()
        title_height = 50 # Approximate height of the title bar + padding

        form_width = 400 # Keep form width fixed
        form_height = 500 # Keep form height fixed
        form_x = 10
        form_y = title_height + 20 # y=70 originally

        # Place form frame
        self.form_frame.place(x=form_x, y=form_y, width=form_width, height=form_height)

        # Place table frame, making it fill remaining space dynamically
        table_x = form_x + form_width + 20 # Start table after form + padding
        table_y = form_y
        table_width = window_width - table_x - 10 # Fill remaining width (-10 margin)
        table_height = window_height - table_y - 30 # Fill remaining height (-30 margin)

        # Ensure minimum dimensions for the table frame
        if table_width < 200: table_width = 200
        if table_height < 200: table_height = 200

        self.table_frame.place(x=table_x, y=table_y, width=table_width, height=table_height)
        # Update original position store if needed, though dynamic placement might make it less critical
        # self.original_table_frame_pos = (table_x, table_y)

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

    def __del__(self):
        # Close the database connection when the window is closed
        if hasattr(self, 'conn') and self.conn: # Check if conn exists and is not None
            self.conn.close()

