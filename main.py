import tkinter as tk
from gui import create_main_window

try:
    from tkinterdnd2 import TkinterDnD
except ImportError:
    TkinterDnD = None

def main():
    root = TkinterDnD.Tk() if TkinterDnD else tk.Tk()
    create_main_window(root)
    root.mainloop()

if __name__ == "__main__":
    main()
