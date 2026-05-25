# main.py
import tkinter as tk
from gui import QuoridorGUI


def main():
    root = tk.Tk()

    # Keep the window fixed size so the board proportions stay correct
    root.resizable(False, False)

    # Launch the Quoridor GUI
    app = QuoridorGUI(root)
    root.mainloop()


if __name__ == "__main__":
    main()
