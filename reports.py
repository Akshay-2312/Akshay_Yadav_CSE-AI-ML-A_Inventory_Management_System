import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import sqlite3
import csv
from fpdf import FPDF


# Added a back button to return to the dashboard
class ReportsWindow:
    def __init__(self, root):
        self.root = root
        self.root.title("Reports - D R Medical Store")
        self.root.geometry("900x600")
        self.root.configure(bg="#f0f4f7")
        self.is_maximized = False
        self.original_content_pos = (50, 70)
        self.maximize_btn = tk.Button(self.root, text="🗖", command=self.toggle_maximize, font=("Helvetica", 14))
        self.maximize_btn.place(x=10, y=10)

        title = tk.Label(self.root, text="Reports Section", font=("Helvetica", 20, "bold"), bg="#2c3e50", fg="white", pady=10)
        title.pack(fill=tk.X)

        message = tk.Label(self.root, text="Select a report to view or export.", font=("Helvetica", 14), bg="#f0f4f7", fg="#34495e")
        message.pack(pady=20)

        tk.Button(self.root, text="Stock Report", command=self.stock_report, width=20).pack(pady=10)
        tk.Button(self.root, text="Export to CSV", command=self.export_to_csv, width=20).pack(pady=10)
        tk.Button(self.root, text="Export to PDF", command=self.export_to_pdf, width=20).pack(pady=10)

        back_button = tk.Button(self.root, text="Back to Dashboard", command=self.root.destroy, bg="#3498db", fg="white", font=("Helvetica", 12))
        back_button.pack(side=tk.BOTTOM, pady=10)

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
            conn = sqlite3.connect("db/store.db")
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

    def toggle_maximize(self):
        if not self.is_maximized:
            self.root.state('zoomed')
            self.center_main_content()
            self.is_maximized = True
        else:
            self.root.state('normal')
            self.content_frame.place(x=self.original_content_pos[0], y=self.original_content_pos[1])
            self.is_maximized = False

    def center_main_content(self):
        self.root.update_idletasks()
        win_width = self.root.winfo_width()
        win_height = self.root.winfo_height()
        content_width = self.content_frame.winfo_width()
        content_height = self.content_frame.winfo_height()
        x_center = (win_width - content_width) // 2
        y_center = (win_height - content_height) // 2
        self.content_frame.place(x=x_center, y=y_center)
