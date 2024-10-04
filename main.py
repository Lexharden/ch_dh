import tkinter as tk
from views.main_view import MainView


def main():
    root = tk.Tk()
    root.geometry('550x250')
    root.resizable(False, False)

    _ = MainView(root)
    root.mainloop()


if __name__ == "__main__":
    main()
