from ui_main import SilentlyTaskGeneratorApp
import tkinter as tk
from tkinter import messagebox

if __name__ == "__main__":
    try:
        root = tk.Tk()
        app = SilentlyTaskGeneratorApp(root)
        root.mainloop()
    except Exception as e:
        messagebox.showerror("Error", f"An error occurred: {e}") 