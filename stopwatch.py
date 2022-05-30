import time
import tkinter as tk
from ctypes import windll


GWL_EXSTYLE = -20
WS_EX_APPWINDOW = 0x00040000
WS_EX_TOOLWINDOW = 0x00000080


def set_appwindow(root):
    hwnd = windll.user32.GetParent(root.winfo_id())
    style = windll.user32.GetWindowLongPtrW(hwnd, GWL_EXSTYLE)
    style = style & ~WS_EX_TOOLWINDOW
    style = style | WS_EX_APPWINDOW
    res = windll.user32.SetWindowLongPtrW(hwnd, GWL_EXSTYLE, style)
    # re-assert the new window style
    root.wm_withdraw()
    root.after(10, lambda: root.wm_deiconify())


class TimerApp(tk.Frame):
    import winsound
    from ctypes import windll

    def __init__(self, parent, *args, **kwargs):
        tk.Frame.__init__(self, parent, *args, **kwargs)
        self.parent = parent
        self.initialize_gui()

    def initialize_gui(self):
        self.parent.title("Stop Watch")
        self.parent.resizable(False, False)
        self.parent.geometry(
            # these will control where the timer is placed our stopwatch was built 105x30
            "105x30+1600+1050"
        )
        self.parent.configure(bg="#212121")
        self.parent.attributes("-topmost", "true")
        self.elapsed = 0
        self.timer = False
        self.after_id = None
        self.timeformat = tk.StringVar()
        self.timeformat.set("")
        # mousebindings scroll functionality and mouse clicking for movement
        self.parent.bind("<MouseWheel>", self.mousewheel)
        self.parent.bind("<Shift-MouseWheel>", self.shiftmousewheel)
        self.parent.bind("<Control-MouseWheel>", self.ctrlmousewheel)
        self.parent.bind("<Button-2>", self.smartclick2)
        self.parent.bind("<ButtonPress-1>", self.start_move)
        self.parent.bind("<ButtonRelease-1>", self.stop_move)
        self.parent.bind("<B1-Motion>", self.do_move)
        self.samebuttonocd = tk.Label(
            self.parent, bg="#212121", fg="#89b5f0", text="◌", font=("Dank Mono", 6)
        )
        self.measurement_label = tk.Label(
            self.parent, bg="#212121", fg="#89b5f0", text="◌", font=("Dank Mono", 6)
        )
        self.display_timer()
        self.pixel = tk.PhotoImage(width=1, height=1)
        self.timer_label = tk.Label(
            self.parent,
            bg="#212121",
            fg="#89b5f0",
            textvariable=self.timeformat,
            font=("Dank Mono", 25),
        )

        self.button3 = tk.Button(
            self.parent,
            bg="#99aab5",
            image=self.pixel,
            width=1,
            height=1,
            compound="c",
            relief="flat",
            command=self.clear_clock,
        )
        self.button4 = tk.Button(
            self.parent,
            bg="#99B5A4",
            image=self.pixel,
            width=1,
            height=1,
            compound="c",
            relief="flat",
            command=self.smartclick,
        )
        self.buttondestruct = tk.Button(
            self.parent,
            bg="#3b3b3e",
            image=self.pixel,
            width=1,
            height=1,
            compound="c",
            relief="flat",
            command=lambda: self.parent.destroy(),
        )
        # placing our specific components onto the 105x30 sized stopwatch
        self.measurement_label.place(x=35, y=2)
        self.measurement_label.lift()
        self.samebuttonocd.place(x=35, y=14)
        self.samebuttonocd.lift()
        self.button4.place(x=55, y=5)
        self.button4.lift()  # x97 y20
        self.button3.place(x=97, y=10)
        self.button3.lift()
        self.buttondestruct.place(x=97, y=0)
        self.buttondestruct.lift()
        self.button4.place(x=97, y=20)
        self.button4.lift()
        self.timer_label.place(x=-3, y=-8)

    def start_move(self, event):
        self.x = event.x
        self.y = event.y

    def stop_move(self, event):
        self.x = None
        self.y = None

    def do_move(self, event):
        deltax = event.x - self.x
        deltay = event.y - self.y
        x = self.parent.winfo_x() + deltax
        y = self.parent.winfo_y() + deltay
        self.parent.geometry(f"+{x}+{y}")

    def start_clock(self):
        self.start_time = time.perf_counter()
        self.after_id = self.after(1000, self.update_clock)

    def stop_clock(self):
        if self.after_id:
            self.after_cancel(self.after_id)
            self.after_id = None

    def clear_clock(self):
        was_running = True if self.after_id else False
        self.stop_clock()
        self.elapsed = 0
        self.timer = False

        self.display_timer()
        if was_running:
            self.start_clock()

    def smartclick(self):
        if self.button4["bg"] == "#99B5A4":
            self.button4["bg"] = "#b599aa"
            self.start_clock()

        else:
            self.button4["bg"] = "#99B5A4"
            self.stop_clock()

    def smartclick2(self, event):
        if self.button4["bg"] == "#99B5A4":
            self.button4["bg"] = "#b599aa"
            self.start_clock()

        else:
            self.button4["bg"] = "#99B5A4"
            self.stop_clock()

    def display_timer(self):  # display timer
        hours, remainder = divmod(self.elapsed, 3600)
        minutes, seconds = divmod(remainder, 60)

        if self.elapsed == 0:
            self.timeformat.set("{:02d}:{:02d}".format(minutes, seconds))
            self.measurement_label["text"] = "◌"
            self.samebuttonocd["text"] = "◌"

        if 0 < self.elapsed <= 3599:
            self.timeformat.set("{:02d}:{:02d}".format(minutes, seconds))
            self.measurement_label["text"] = "◌"
            self.samebuttonocd["text"] = "◌"
        elif self.elapsed >= 3600:
            self.timeformat.set("{:02d}:{:02d}".format(hours, minutes))
            self.measurement_label["text"] = "●"
            self.samebuttonocd["text"] = "●"

    def update_clock(self):
        if self.after_id and self.timer:
            now = time.perf_counter()
            delta_time = round(now - self.start_time)
            self.start_time = now
            self.elapsed -= delta_time
            self.display_timer()
            self.timerended()
            self.after_id = self.after(1000, self.update_clock)

        else:
            now = time.perf_counter()
            delta_time = round(now - self.start_time)
            self.start_time = now
            self.elapsed += delta_time
            self.display_timer()
            self.after_id = self.after(1000, self.update_clock)

    def update_symbol(self): # changes our symbol based on hour or minute
        if self.samebuttonocd["text"] == "●" and self.measurement_label["text"] == "●":
            self.measurement_label["text"] = "◌"
            self.samebuttonocd["text"] = "◌"
        elif (
            self.samebuttonocd["text"] == "◌" and self.measurement_label["text"] == "◌"
        ):
            self.samebuttonocd["text"] = "●"
            self.measurement_label["text"] = "●"

    def timerended(self):
        if self.elapsed == -1:
            duration = 1000
            freq = 200
            # stops our sound after it goes into negatives
            self.winsound.Beep(freq, duration)
            self.stop_clock()
            self.button4["bg"] = "#99B5A4"

        if self.elapsed <= 0:
            # plays a windows sound that occurs when our times reaches 00:00
            self.after(400, self.update_symbol)
            duration = 1000
            freq = 200
            self.winsound.Beep(freq, duration)
            self.display_timer()

    def timer1(self):
        #adds 1 minute
        was_running = True if self.after_id else False
        self.stop_clock()
        self.elapsed += 60
        self.timer = True
        self.display_timer()
        if was_running:
            self.smartclick()

    def timer10(self):
        #adds 10 minute
        was_running = True if self.after_id else False
        self.stop_clock()
        self.elapsed += 600
        self.timer = True
        self.display_timer()
        if was_running:
            self.smartclick()

    def timer60(self):
        #adds 1 hour
        was_running = True if self.after_id else False
        self.stop_clock()
        self.elapsed += 3000  # prev 3600 for 60 minutes
        self.timer = True
        self.display_timer()
        if was_running:
            self.smartclick()

    def shiftmousewheel(self, event):
        if event.num == 5 or event.delta == -120:
            self.elapsed -= 1200
            self.timer10()
            if self.elapsed < 0:
                self.clear_clock()
        if event.num == 4 or event.delta == 120:
            self.timer10()
            if self.elapsed < 0:
                self.clear_clock()

    def mousewheel(self, event):
        if event.num == 5 or event.delta == -120:
            self.elapsed -= 120
            self.timer1()
            if self.elapsed < 0:
                self.clear_clock()

        if event.num == 4 or event.delta == 120:
            self.timer1()
            if self.elapsed < 0:
                self.clear_clock()

    def ctrlmousewheel(self, event):
        if event.num == 5 or event.delta == -120:
            self.elapsed -= 6000  # prev -7200 for 60 min
            self.timer60()
            if self.elapsed < 0:
                self.clear_clock()
        if event.num == 4 or event.delta == 120:
            self.timer60()
            if self.elapsed < 0:
                self.clear_clock()


def main():
    root = tk.Tk()
    root.overrideredirect(True)
    start = TimerApp(root)
    root.after(10, lambda: set_appwindow(root))
    start.mainloop()


if __name__ == "__main__":

    main()
