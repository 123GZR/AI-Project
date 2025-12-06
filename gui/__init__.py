import tkinter as tk
from tkinter import ttk
from .main_window import ComputerExpertGUI

if __name__ == "__main__":
    root = tk.Tk()
    app = ComputerExpertGUI(root)
    root.mainloop()
