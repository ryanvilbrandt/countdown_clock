import threading
import tkinter as tk
from math import ceil
from time import time
from tkinter import ttk

import pystray
from PIL import Image

INITIAL_TIME = 3 * 60
FONT_SIZE = 72
ICON_PATH = "clock.jpg"


class CountdownClock:

    x, y = 0, 0
    dragging = False
    timer_end, paused_time = None, INITIAL_TIME
    running = False
    timer_id = None

    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Countdown Clock")
        self.root.overrideredirect(True)

        # Create a system tray icon
        self.image = Image.open(ICON_PATH)
        self.menu = (
            pystray.MenuItem("Reset Clock", self.reset_clock, default=True),
            pystray.MenuItem("Pause / Play", self.pause_play),
            pystray.MenuItem("Exit", self.on_exit)
        )
        self.icon = pystray.Icon("Countdown Clock", self.image, "Countdown Clock", self.menu)

        self.countdown_label = ttk.Label(self.root, text=self.get_time_label(), font=("Helvetica", FONT_SIZE))
        self.countdown_label.pack(padx=20, pady=20)

        # Bind the mouse events to the functions
        self.root.bind("<ButtonPress-1>", self.start_drag)
        self.root.bind("<ButtonRelease-1>", self.stop_drag)
        self.root.bind("<B1-Motion>", self.on_drag)

        # Always on top
        self.root.attributes('-topmost', True)

        # Get current window size and set to minimum
        self.root.update()
        self.root.wm_minsize(width=self.root.winfo_width(), height=self.root.winfo_height())

    # Loop functions
    def run(self):
        self.run_icon_loop()
        self.run_timer_loop()
        self.root.mainloop()

    def run_icon_loop(self):
        threading.Thread(name="icon.run()", target=self.icon.run, daemon=True).start()

    def run_timer_loop(self):
        t = threading.Thread(name="timer_loop", target=self.timer_loop, daemon=True)
        t.start()

    def timer_loop(self):
        if self.timer_id:
            self.root.after_cancel(self.timer_id)
        if self.running:
            t = time()
            if t <= self.timer_end:
                label = self.get_time_label()
            else:
                label = self.get_time_label() if (int(t) % 2 != 0) else ""
            self.countdown_label.config(text=label)
            self.root.update()
        self.timer_id = self.root.after(100, self.timer_loop)

    # Function to handle mouse button press event
    def start_drag(self, event):
        self.x, self.y = event.x, event.y
        self.dragging = True

    # Function to handle mouse button release event
    def stop_drag(self, event):
        self.dragging = False

    # Function to handle mouse motion event (dragging)
    def on_drag(self, event):
        if self.dragging:
            x0, y0 = self.root.winfo_x(), self.root.winfo_y()
            self.root.geometry(f"+{x0 + (event.x - self.x)}+{y0 + (event.y - self.y)}")

    def get_time_label(self):
        if self.running:
            # If the timer is running, display the remaining time between now and the timer ending
            t = ceil(self.timer_end - time())
        else:
            # If the timer isn't running, display the stored time in paused_time
            t = ceil(self.paused_time)
        t = max(t, 0)
        minutes = int(t // 60)
        seconds = int(t % 60)
        return f"{minutes}:{seconds:>02}"

    def reset_clock(self):
        self.timer_end = time() + INITIAL_TIME
        self.running = True

    def pause_play(self):
        if self.running:
            # On pause, store time remaining in paused_time
            self.paused_time = self.timer_end - time()
            self.running = False
        else:
            # On play, create new timer_end value from paused_time
            self.timer_end = time() + self.paused_time
            self.running = True

    def on_exit(self, *args):
        self.icon.stop()  # Remove the system tray icon
        self.root.destroy()


if __name__ == "__main__":
    app = CountdownClock()
    app.run()
