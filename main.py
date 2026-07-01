import tkinter as tk
from gui import create_main_window

def main():
    root = tk.Tk()
    create_main_window(root)
    root.mainloop()

if __name__ == "__main__":
    main()