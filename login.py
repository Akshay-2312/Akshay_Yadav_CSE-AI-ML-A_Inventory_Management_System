# login.py
import tkinter as tk
from tkinter import messagebox
import db  # We will use it later for user authentication

# Added functionality to bind Enter and Space keys to buttons
class LoginWindow:
    def __init__(self, root):
        self.root = root
        self.root.title("Login - D R Medical Store")
        self.root.geometry("400x400")
        self.root.resizable(False, False)

        self.username_var = tk.StringVar()
        self.password_var = tk.StringVar()

        # --- Updated UI Components ---
        self.root.configure(bg="#e8f4f8")  # Set background color

        title = tk.Label(root, text="D R Medical Store", font=("Helvetica", 28, "bold"), bg="#e8f4f8", fg="#2c3e50")
        title.pack(pady=30)

        frame = tk.Frame(root, bg="#ffffff", relief=tk.RAISED, bd=2)
        frame.pack(pady=30, padx=30, fill=tk.BOTH, expand=True)

        username_label = tk.Label(frame, text="Username", font=("Helvetica", 16), bg="#ffffff", fg="#34495e")
        username_label.pack(pady=15)
        username_entry = tk.Entry(frame, textvariable=self.username_var, font=("Helvetica", 16), bd=3, relief=tk.GROOVE)
        username_entry.pack(pady=10, padx=20, fill=tk.X)

        password_label = tk.Label(frame, text="Password", font=("Helvetica", 16), bg="#ffffff", fg="#34495e")
        password_label.pack(pady=15)
        password_entry = tk.Entry(frame, textvariable=self.password_var, font=("Helvetica", 16), bd=3, relief=tk.GROOVE, show="*")
        password_entry.pack(pady=10, padx=20, fill=tk.X)

        login_button = tk.Button(root, text="Login", font=("Helvetica", 14, "bold"), bg="#3498db", fg="#ffffff", activebackground="#2980b9", relief=tk.FLAT, command=self.login)
        login_button.pack(pady=20, padx=10, fill=tk.X)

        # Adding hover effect to the login button
        def on_enter(e):
            login_button["bg"] = "#2980b9"

        def on_leave(e):
            login_button["bg"] = "#3498db"

        login_button.bind("<Enter>", on_enter)
        login_button.bind("<Leave>", on_leave)

        # Bind Enter and Space keys to the login button
        self.root.bind("<Return>", lambda event: self.login())
        self.root.bind("<space>", lambda event: self.login())

        footer = tk.Label(root, text="© 2025 D R Medical Store", font=("Helvetica", 12), bg="#e8f4f8", fg="#95a5a6")
        footer.pack(side=tk.BOTTOM, pady=15)

    def login(self):
        username = self.username_var.get()
        password = self.password_var.get()

        if username == "admin" and password == "admin123":
            messagebox.showinfo("Login Success", "Welcome to D R Medical Store Inventory System!")
            self.root.destroy()

            # Open Dashboard
            import dashboard
            root_dash = tk.Tk()
            dashboard.DashboardWindow(root_dash)
            root_dash.mainloop()
        else:
            messagebox.showerror("Login Failed", "Invalid Username or Password")
