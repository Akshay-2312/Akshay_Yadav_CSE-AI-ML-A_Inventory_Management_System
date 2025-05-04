# login.py
import tkinter as tk
from tkinter import messagebox
import db  # We will use it later for user authentication

# Added functionality to bind Enter and Space keys to buttons
class LoginWindow:
    def __init__(self, root):
        self.root = root
        self.root.title("Login - D R Medical Store")
        self.root.geometry("400x500")
        self.root.resizable(False, False)

        self.username_var = tk.StringVar()
        self.password_var = tk.StringVar()

        # --- Updated UI Components ---
        self.root.configure(bg="#a8d5f0")  # Set background color to light blue as shown in the image

        title = tk.Label(root, text="D R Medical Store", font=("Helvetica", 28, "bold"), bg="#a8d5f0", fg="#2c3e50")
        title.pack(pady=30)

        # Create a rounded frame with white background
        frame = tk.Frame(root, bg="#ffffff", relief=tk.RAISED, bd=1)
        frame.pack(pady=20, padx=30, fill=tk.BOTH, expand=True)

        # Add some padding at the top of the frame
        padding_frame = tk.Frame(frame, bg="#ffffff", height=30)
        padding_frame.pack(fill=tk.X)

        username_label = tk.Label(frame, text="Username", font=("Helvetica", 18), bg="#ffffff", fg="#2c3e50")
        username_label.pack(pady=(10, 5))
        username_entry = tk.Entry(frame, textvariable=self.username_var, font=("Helvetica", 16), bd=1, relief=tk.GROOVE)
        username_entry.pack(pady=(5, 15), padx=30, fill=tk.X)
        username_entry.config(highlightthickness=1, highlightbackground="#e0e0e0")

        password_label = tk.Label(frame, text="Password", font=("Helvetica", 18), bg="#ffffff", fg="#2c3e50")
        password_label.pack(pady=(10, 5))
        password_entry = tk.Entry(frame, textvariable=self.password_var, font=("Helvetica", 16), bd=1, relief=tk.GROOVE, show="*")
        password_entry.pack(pady=(5, 15), padx=30, fill=tk.X)
        password_entry.config(highlightthickness=1, highlightbackground="#e0e0e0")

        # Create a frame for the login button to be inside the white frame
        button_frame = tk.Frame(frame, bg="#ffffff")
        button_frame.pack(pady=20, padx=30, fill=tk.X)

        login_button = tk.Button(button_frame, text="Log In", font=("Helvetica", 16, "bold"),
                                bg="#4a90e2", fg="#ffffff", activebackground="#3a80d2",
                                relief=tk.FLAT, command=self.login, height=2, borderwidth=0)
        login_button.pack(fill=tk.X, padx=5)

        # Adding hover effect to the login button
        def on_enter(_):
            login_button["bg"] = "#3a80d2"

        def on_leave(_):
            login_button["bg"] = "#4a90e2"

        login_button.bind("<Enter>", on_enter)
        login_button.bind("<Leave>", on_leave)

        # Bind Enter and Space keys to the login button
        self.root.bind("<Return>", lambda _: self.login())
        self.root.bind("<space>", lambda _: self.login())

        footer = tk.Label(root, text="© 2025 D R Medical Store", font=("Helvetica", 12), bg="#a8d5f0", fg="#2c3e50")
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
