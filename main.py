# main.py
import tkinter as tk
from login import LoginWindow

def main():
    root = tk.Tk()
    app = LoginWindow(root)
    root.mainloop()

if __name__ == "__main__":
    main()
