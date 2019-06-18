import constants
import Tkinter as tk

class Craft(constants.correction):
    def create_window(self):
        self.app.counter += 1
        t = tk.Toplevel(self.app.master)
        t.wm_title("Window #%s" % self.app.counter)
        l = tk.Label(t, text="This is window #%s" % self.app.counter)
        l.pack(side="top", fill="both", expand=True, padx=100, pady=100)
        # self.app.master.after(1, lambda: t.focus_force())
        # t.tkraise()

    def __init__(self, app):
        self.app = app