import tkinter as tk
import tkinter.ttk as ttk
import time
import pyperclip
from PIL import Image, ImageTk
import os
import sys

class PomodoroTimer:
    def __init__(self, root):
        self.root = root
        self.root.title("Pomodoro Timer")
        self.root.geometry("400x400")
        self.root.resizable(False, False)
        self.root.configure(bg="#FF6347")
        self.root.overrideredirect(True)

        self.work_time = 25 * 60
        self.break_time = 5 * 60
        self.current_time = self.work_time
        self.is_running = False
        self.is_work = True
        self.timer_id = None
        self.is_minimized = False
        self.records = []

        self.setup_styles()
        self.create_titlebar()
        self.create_widgets()

    def setup_styles(self):
        self.style = ttk.Style()
        self.style.theme_use("clam")
        self.style.configure("Custom.Horizontal.TProgressbar", troughcolor="#FFDAB9", background="#FF9999", thickness=20)
        self.style.configure("TButton", font=("Helvetica", 12), background="#FFDAB9", foreground="#8B0000")
        self.style.configure("TLabel", background="#FF6347", foreground="#FFFFFF")
        self.style.configure("TFrame", background="#FF6347")

    def create_titlebar(self):
        titlebar = tk.Frame(self.root, bg="#FFDAB9", relief="raised", bd=0)
        titlebar.pack(side="top", fill="x")

        title_label = tk.Label(titlebar, text="Pomodoro Timer", bg="#FFDAB9", fg="#8B0000", font=("Helvetica", 10))
        title_label.pack(side="left", padx=10)

        close_button = tk.Button(titlebar, text="×", command=self.root.quit, bg="#FFDAB9", fg="#8B0000", 
                                font=("Helvetica", 12), bd=0, activebackground="#FF9999")
        close_button.pack(side="right", padx=5)

        minimize_button = tk.Button(titlebar, text="–", command=self.minimize_window, bg="#FFDAB9", fg="#8B0000", 
                                  font=("Helvetica", 12), bd=0, activebackground="#FF9999")
        minimize_button.pack(side="right", padx=5)

        titlebar.bind("<Button-1>", self.start_move)
        titlebar.bind("<B1-Motion>", self.on_motion)
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

        minutes, seconds = divmod(self.work_time, 60)
        self.time_label = ttk.Label(self.root, text=f"{minutes:02d}:{seconds:02d}", font=("Helvetica", 40))
        self.time_label.pack(pady=10)

        self.progress = ttk.Progressbar(self.root, length=360, mode="determinate", maximum=self.work_time, 
                                      style="Custom.Horizontal.TProgressbar")
        self.progress.pack(pady=10, padx=20)

        button_frame = ttk.Frame(self.root)
        button_frame.pack(pady=10)

        self.start_button = ttk.Button(button_frame, text="Start", command=self.start_timer)
        self.start_button.grid(row=0, column=0, padx=5)
        self.record_button = ttk.Button(button_frame, text="Record", command=self.record_time)
        self.record_button.grid(row=0, column=1, padx=5)
        self.reset_button = ttk.Button(button_frame, text="Reset", command=self.reset_timer)
        self.reset_button.grid(row=0, column=2, padx=5)

        self.record_frame = ttk.Frame(self.root)
        self.record_frame.pack(pady=10, fill="both", padx=20)

        self.scrollbar = ttk.Scrollbar(self.record_frame)
        self.scrollbar.pack(side="right", fill="y")

        self.record_text = tk.Text(self.record_frame, height=5, width=30, font=("Helvetica", 10),
                                 yscrollcommand=self.scrollbar.set, bg="#FFDAB9", fg="#8B0000")
        self.record_text.pack(side="left", fill="both", expand=True)
        self.record_text.config(state="disabled")

        self.scrollbar.config(command=self.record_text.yview)

        try:
            if getattr(sys, 'frozen', False):
                base_path = sys._MEIPASS
            else:
                base_path = os.path.dirname(__file__)
            icon_path = os.path.join(base_path, "copy.png")
            image = Image.open(icon_path)
            image = image.resize((32, 32), Image.LANCZOS)
            self.icon_image = ImageTk.PhotoImage(image)
            self.icon_label = tk.Label(self.record_frame, image=self.icon_image, bg="#FFDAB9", cursor="hand2")
            self.icon_label.place(relx=1.0, rely=0.0, x=-20, y=5, anchor="ne")  # 左移 5 像素
            self.icon_label.lift()
            self.icon_label.bind("<Button-1>", lambda event: self.copy_records())  # 点击触发复制
        except Exception as e:
            print(f"Failed to load icon: {e}")

        self.record_text.bind("<MouseWheel>", self.on_mouse_wheel)
        self.record_text.bind("<Button-4>", self.on_mouse_wheel)
        self.record_text.bind("<Button-5>", self.on_mouse_wheel)
        self.record_frame.bind("<MouseWheel>", self.on_mouse_wheel)
        self.record_frame.bind("<Button-4>", self.on_mouse_wheel)
        self.record_frame.bind("<Button-5>", self.on_mouse_wheel)

    def on_mouse_wheel(self, event):
        if self.record_text.yview() != (0.0, 1.0):
            delta = -1 if (event.num == 4 or event.delta > 0) else 1
            self.record_text.yview_scroll(delta, "units")
        return "break"

    def copy_records(self):
        records_text = "\n".join(self.records)
        pyperclip.copy(records_text)

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

    def record_time(self):
        minutes, seconds = divmod(self.current_time, 60)
        time_str = f"{minutes:02d}:{seconds:02d}"
        self.records.append(time_str)

        self.record_text.config(state="normal")
        self.record_text.delete(1.0, tk.END)
        for record in self.records:
            self.record_text.insert(tk.END, f"{record}\n")
        self.record_text.config(state="disabled")
        self.record_text.see(tk.END)

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

        label = ttk.Label(frame, text=message, font=("Helvetica", 14))
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
            else:
                red = int(255 - (255 - 204) * (1 - progress_ratio))
                green = int(204 - (204 - 102) * (1 - progress_ratio))
                blue = 0
            color = f"#{red:02x}{green:02x}{blue:02x}"
            self.style.configure("Custom.Horizontal.TProgressbar", background=color)

            self.timer_id = self.root.after(1000, self.update_timer)
        elif self.current_time <= 0:
            self.is_running = False
            self.root.attributes("-topmost", True)
            if self.is_minimized:
                self.is_minimized = False
                self.root.deiconify()
            self.root.focus_force()

            self.records.clear()
            self.record_text.config(state="normal")
            self.record_text.delete(1.0, tk.END)
            self.record_text.config(state="disabled")

            message = "Time to take a break!" if self.is_work else "Time to work!"
            self.root.after(100, lambda: self.show_alert(message))
            self.is_work = not self.is_work
            self.current_time = self.work_time if self.is_work else self.break_time
            self.progress["maximum"] = self.current_time
            self.progress["value"] = self.current_time
            self.title_label.config(text="Work Time" if self.is_work else "Break Time")
            minutes, seconds = divmod(self.current_time, 60)
            self.time_label.config(text=f"{minutes:02d}:{seconds:02d}")

    def reset_timer(self):
        self.is_running = False
        self.current_time = self.work_time
        self.start_button.config(text="Start")
        self.is_work = True
        self.title_label.config(text="Work Time")
        minutes, seconds = divmod(self.work_time, 60)
        self.time_label.config(text=f"{minutes:02d}:{seconds:02d}")
        self.progress["maximum"] = self.work_time
        self.progress["value"] = self.work_time
        self.style.configure("Custom.Horizontal.TProgressbar", background="#FF9999")

if __name__ == "__main__":
    root = tk.Tk()
    app = PomodoroTimer(root)
    root.mainloop()