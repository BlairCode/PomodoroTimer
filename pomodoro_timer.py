import tkinter as tk
import tkinter.ttk as ttk
import time

class PomodoroTimer:
    def __init__(self, root):
        self.root = root
        self.root.title("Pomodoro Timer")
        self.root.geometry("400x250")
        self.root.resizable(True, True)
        self.root.configure(bg="#FF6347")
        self.root.overrideredirect(True)
        self.root.minsize(300, 200)

        self.work_time = 25 * 60
        self.break_time = 5 * 60
        self.current_time = self.work_time
        self.is_running = False
        self.is_work = True
        self.timer_id = None
        self.is_minimized = False

        self.style = ttk.Style()
        self.style.theme_use('clam')
        self.style.configure("Custom.Horizontal.TProgressbar", troughcolor="#FFDAB9", background="#FF9999", thickness=20)
        self.style.configure("TButton", font=("Helvetica", 12), background="#FFDAB9", foreground="#8B0000")
        self.style.configure("TLabel", background="#FF6347", foreground="#FFFFFF")
        self.style.configure("TFrame", background="#FF6347")

        self.create_titlebar()
        self.create_widgets()

    def create_titlebar(self):
        self.titlebar = tk.Frame(self.root, bg="#FFDAB9", relief="raised", bd=0)
        self.titlebar.pack(side="top", fill="x")

        title_label = tk.Label(self.titlebar, text="Pomodoro Timer", bg="#FFDAB9", fg="#8B0000", font=("Helvetica", 10))
        title_label.pack(side="left", padx=10)

        close_button = tk.Button(self.titlebar, text="×", command=self.root.quit, bg="#FFDAB9", fg="#8B0000", font=("Helvetica", 12), bd=0, activebackground="#FF9999")
        close_button.pack(side="right", padx=5)

        minimize_button = tk.Button(self.titlebar, text="–", command=self.minimize_window, bg="#FFDAB9", fg="#8B0000", font=("Helvetica", 12), bd=0, activebackground="#FF9999")
        minimize_button.pack(side="right", padx=5)

        self.titlebar.bind("<Button-1>", self.start_move)
        self.titlebar.bind("<B1-Motion>", self.on_motion)
        title_label.bind("<Button-1>", self.start_move)
        title_label.bind("<B1-Motion>", self.on_motion)

    def start_move(self, event):
        self.x = event.x
        self.y = event.y

    def on_motion(self, event):
        deltax = event.x - self.x
        deltay = event.y - self.y
        x = self.root.winfo_x() + deltax
        y = self.root.winfo_y() + deltay
        self.root.geometry(f"+{x}+{y}")

    def minimize_window(self):
        self.is_minimized = True
        self.root.withdraw()

    def create_widgets(self):
        self.title_label = ttk.Label(self.root, text="Work Time", font=("Helvetica", 16))
        self.title_label.pack(pady=10)

        self.time_label = ttk.Label(self.root, text="25:00", font=("Helvetica", 40))
        self.time_label.pack(pady=10)

        self.progress = ttk.Progressbar(self.root, length=200, mode="determinate", maximum=self.work_time, style="Custom.Horizontal.TProgressbar")
        self.progress.pack(pady=10, fill="x", padx=20)

        self.button_frame = ttk.Frame(self.root)
        self.button_frame.pack(pady=10)

        self.start_button = ttk.Button(self.button_frame, text="Start", command=self.start_timer)
        self.start_button.grid(row=0, column=0, padx=5)
        self.stop_button = ttk.Button(self.button_frame, text="Stop", command=self.stop_timer)
        self.stop_button.grid(row=0, column=1, padx=5)
        self.reset_button = ttk.Button(self.button_frame, text="Reset", command=self.reset_timer)
        self.reset_button.grid(row=0, column=2, padx=5)

        self.root.bind("<Configure>", self.update_progress_length)
        self.root.bind("<Button-1>", self.start_resize)
        self.root.bind("<B1-Motion>", self.on_resize)

    def start_resize(self, event):
        if event.y > self.root.winfo_height() - 10 or event.x > self.root.winfo_width() - 10:
            self.resize_x = event.x
            self.resize_y = event.y
            self.is_resizing = True

    def on_resize(self, event):
        if hasattr(self, 'is_resizing') and self.is_resizing:
            new_width = max(300, self.root.winfo_width() + (event.x - self.resize_x))
            new_height = max(200, self.root.winfo_height() + (event.y - self.resize_y))
            self.root.geometry(f"{new_width}x{new_height}")
            self.resize_x = event.x
            self.resize_y = event.y

    def update_progress_length(self, event):
        new_width = max(200, self.root.winfo_width() - 40)
        self.progress.configure(length=new_width)

    def start_timer(self):
        if not self.is_running:
            self.is_running = True
            self.start_button.config(text="Pause")
            self.update_timer()
        else:
            self.is_running = False
            self.start_button.config(text="Start")
            if self.timer_id:
                self.root.after_cancel(self.timer_id)
                self.timer_id = None

    def show_alert(self, message):
        self.root.attributes("-topmost", False)
        alert = tk.Toplevel(self.root)
        alert.title("Pomodoro Timer")
        alert.geometry("300x150")
        alert.resizable(False, False)
        alert.configure(bg="#FF6347")
        alert.transient(self.root)
        alert.grab_set()
        alert.overrideredirect(True)

        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()
        x = (screen_width - 300) // 2
        y = (screen_height - 150) // 2
        alert.geometry(f"300x150+{x}+{y}")

        frame = tk.Frame(alert, bg="#FF6347")
        frame.pack(expand=True, fill="both")

        label = ttk.Label(frame, text=message, font=("Helvetica", 14), background="#FF6347", foreground="#FFFFFF")
        label.pack(pady=20)

        button = ttk.Button(frame, text="OK", command=lambda: self.close_alert(alert))
        button.pack(pady=10)

        alert.attributes("-topmost", True)
        alert.lift()
        alert.focus_force()

    def close_alert(self, alert):
        alert.destroy()
        self.is_running = True
        self.start_button.config(text="Pause")
        self.update_timer()

    def update_timer(self):
        if self.is_running and self.current_time > 0:
            self.current_time -= 1
            minutes, seconds = divmod(self.current_time, 60)
            self.time_label.config(text=f"{minutes:02d}:{seconds:02d}")
            self.progress["value"] = self.current_time

            max_time = self.work_time if self.is_work else self.break_time
            progress_ratio = self.current_time / max_time
            if self.is_work:
                red = int(255 - (255 - 139) * (1 - progress_ratio))
                green = int(153 - (153 - 0) * (1 - progress_ratio))
                blue = int(153 - (153 - 0) * (1 - progress_ratio))
                color = f"#{red:02x}{green:02x}{blue:02x}"
            else:
                red = int(255 - (255 - 204) * (1 - progress_ratio))
                green = int(204 - (204 - 102) * (1 - progress_ratio))
                blue = 0
                color = f"#{red:02x}{green:02x}{blue:02x}"
            self.style.configure("Custom.Horizontal.TProgressivebar", background=color)

            self.timer_id = self.root.after(1000, self.update_timer)
        elif self.current_time <= 0:
            self.is_running = False
            self.root.attributes("-topmost", True)
            if self.is_minimized:
                self.is_minimized = False
                self.root.deiconify()
            self.root.focus_force()
            self.root.after(100, lambda: self.show_alert("Time to take a break!" if self.is_work else "Time to work!"))
            self.is_work = not self.is_work
            self.current_time = self.work_time if self.is_work else self.break_time
            self.progress["maximum"] = self.current_time
            self.progress["value"] = self.current_time
            self.title_label.config(text="Work Time" if self.is_work else "Break Time")
            self.time_label.config(text=f"{self.current_time // 60:02d}:00")

    def stop_timer(self):
        if self.is_running:
            self.is_running = False
            self.start_button.config(text="Start")
            if self.timer_id:
                self.root.after_cancel(self.timer_id)
                self.timer_id = None
        self.reset_timer()

    def reset_timer(self):
        self.current_time = self.work_time
        self.is_work = True
        self.time_label.config(text="25:00")
        self.title_label.config(text="Work Time")
        self.progress["maximum"] = self.work_time
        self.progress["value"] = self.work_time
        self.style.configure("Custom.Horizontal.TProgressbar", background="#FF9999")

if __name__ == "__main__":
    root = tk.Tk()
    app = PomodoroTimer(root)
    root.mainloop()