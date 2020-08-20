import tkinter as tk
import sys
from pages import StartPage


class MainApp(tk.Tk):
    def __init__(self, server):
        tk.Tk.__init__(self)
        self._frame = None
        self._password = None
        self._articles = []
        self.server = server

        self.switch_frame(StartPage)
        self.geometry("450x450")
        self.title("EditorPS Client 0.9a")

    def switch_frame(self, frame_class):
        new_frame = frame_class(self)
        if self._frame is not None:
            self._frame.destroy()
        self._frame = new_frame
        self._frame.pack()


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: ./main.py server_address")
        exit(1)
    server = sys.argv[1]
    app = MainApp(server)
    app.mainloop()

