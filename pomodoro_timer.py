import tkinter as tk
import tkinter.ttk as ttk
import time
import pyperclip
from PIL import Image, ImageTk, ImageDraw
import os
import sys
import pystray
from pystray import MenuItem as item
import threading

class PomodoroTimer:
    def __init__(self, root):
        """
        Initialize the Pomodoro Timer application.
        Sets up the main window, default values, styles, and UI widgets.
        """
        self.root = root
        self.root.title("Pomodoro Timer")          # Window title
        self.root.geometry("400x400")              # Fixed window size
        self.root.resizable(False, False)          # Disable resizing
        self.root.configure(bg="#FF6347")          # Background color
        self.root.overrideredirect(True)          # Remove default OS title bar

        # Default timer settings (25 minutes work, 5 minutes break)
        self.work_time = 25 * 60
        self.break_time = 5 * 60
        self.current_time = self.work_time
        self.is_running = False
        self.is_work = True                        # Work session flag
        self.timer_id = None
        self.is_minimized = False
        self.records = []                          # Stores recorded times

        self.setup_styles()                        # Configure widget styles
        self.create_titlebar()                     # Create custom title bar
        self.create_widgets()                      # Create main UI elements

    def setup_styles(self):
        """Configure custom styles for progress bars, buttons, and labels."""
        self.style = ttk.Style()
        self.style.theme_use("clam")
        self.style.configure("Custom.Horizontal.TProgressbar", 
                             troughcolor="#FFDAB9", background="#FF9999", thickness=20)
        self.style.configure("TButton", font=("Helvetica", 12), 
                             background="#FFDAB9", foreground="#8B0000")
        self.style.configure("TLabel", background="#FF6347", foreground="#FFFFFF")
        self.style.configure("TFrame", background="#FF6347")

    def create_titlebar(self):
        """
        Create a custom title bar with:
        - App title label
        - Minimize button
        - Close button
        - Drag functionality
        """
        titlebar = tk.Frame(self.root, bg="#FFDAB9", relief="raised", bd=0)
        titlebar.pack(side="top", fill="x")

        title_label = tk.Label(titlebar, text="Pomodoro Timer", bg="#FFDAB9", 
                               fg="#8B0000", font=("Helvetica", 10))
        title_label.pack(side="left", padx=10)

        close_button = tk.Button(titlebar, text="×", command=self.root.quit, bg="#FFDAB9", 
                                 fg="#8B0000", font=("Helvetica", 12), bd=0, activebackground="#FF9999")
        close_button.pack(side="right", padx=5)

        minimize_button = tk.Button(titlebar, text="–", command=self.minimize_window, bg="#FFDAB9", 
                                    fg="#8B0000", font=("Helvetica", 12), bd=0, activebackground="#FF9999")
        minimize_button.pack(side="right", padx=5)

        # Enable window dragging by binding mouse events
        titlebar.bind("<Button-1>", self.start_move)
        titlebar.bind("<B1-Motion>", self.on_motion)
        title_label.bind("<Button-1>", self.start_move)
        title_label.bind("<B1-Motion>", self.on_motion)

    def start_move(self, event):
        """Store the initial mouse position for dragging."""
        self.x = event.x
        self.y = event.y

    def on_motion(self, event):
        """Reposition the window based on mouse movement."""
        deltax = event.x - self.x
        deltay = event.y - self.y
        x = self.root.winfo_x() + deltax
        y = self.root.winfo_y() + deltay
        self.root.geometry(f"+{x}+{y}")

    def minimize_window(self):
        """Minimize the application window (hide it and add system tray icon)."""
        self.is_minimized = True
        self.root.withdraw()

        # Stop existing tray icon if present
        if getattr(self, "tray_icon", None):
            try:
                self.tray_icon.stop()
            except Exception:
                pass
            self.tray_icon = None

        if pystray:
            # Menu actions
            def on_restore(icon, item):
                self.is_minimized = False
                self.root.after(0, self.root.deiconify)  # Ensure thread-safe GUI restore
                icon.stop()
                self.tray_icon = None

            def on_quit(icon, item):
                self.root.after(0, self.root.quit)
                icon.stop()
                self.tray_icon = None

            # Load icon image
            try:
                base_path = sys._MEIPASS if getattr(sys, 'frozen', False) else os.path.dirname(__file__)
                icon_image = Image.open(os.path.join(base_path, "imgs/tomato.ico"))
            except Exception:
                # Fallback: simple red square icon
                icon_image = Image.new("RGBA", (16, 16), (255, 0, 0, 0))
                draw = ImageDraw.Draw(icon_image)
                draw.rectangle([0, 0, 15, 15], fill=(255, 0, 0, 255), outline=(0, 0, 0, 255))

            # Create tray icon
            menu = pystray.Menu(item("Restore", on_restore), item("Quit", on_quit))
            self.tray_icon = pystray.Icon("Pomodoro Timer", icon_image, "Pomodoro Timer", menu)

            # Run tray in background (single method, not duplicated)
            threading.Thread(target=self.tray_icon.run, daemon=True).start()
        else:
            print("pystray module not found. Cannot minimize to system tray.")

    def create_widgets(self):
        """Create the main UI components (labels, buttons, progress bar, text area)."""
        # Session label ("Work Time" / "Break Time")
        self.title_label = ttk.Label(self.root, text="Work Time", font=("Helvetica", 16))
        self.title_label.pack(pady=10)

        # Frame for timer + switch icon
        time_frame = ttk.Frame(self.root)
        time_frame.pack(pady=10)

        # Timer display
        minutes, seconds = divmod(self.work_time, 60)
        self.time_label = ttk.Label(time_frame, text=f"{minutes:02d}:{seconds:02d}", font=("Helvetica", 40))
        self.time_label.pack(side="left", padx=10)

        # Load switch icon
        try:
            if getattr(sys, 'frozen', False):  # Running in a packaged exe
                base_path = sys._MEIPASS
            else:
                base_path = os.path.dirname(__file__)
            icon_path = os.path.join(base_path, "imgs/switch.png") 
            switch_img = Image.open(icon_path).resize((32, 32), Image.LANCZOS)
            self.switch_icon = ImageTk.PhotoImage(switch_img)

            # Switch button (beside time display)
            self.switch_button = tk.Label(time_frame, image=self.switch_icon, bg="#FF6347", cursor="hand2")
            self.switch_button.pack(side="left", padx=10)
            self.switch_button.bind("<Button-1>", lambda event: self.switch_mode())
        except Exception as e:
            print(f"Failed to load switch icon: {e}")


        # Progress bar
        self.progress = ttk.Progressbar(self.root, length=360, mode="determinate", 
                                        maximum=self.work_time, style="Custom.Horizontal.TProgressbar")
        self.progress.pack(pady=10, padx=20)

        # Buttons (Start/Pause, Record, Reset)
        button_frame = ttk.Frame(self.root)
        button_frame.pack(pady=10)

        self.start_button = ttk.Button(button_frame, text="Start", command=self.start_timer)
        self.start_button.grid(row=0, column=0, padx=5)
        self.record_button = ttk.Button(button_frame, text="Record", command=self.record_time)
        self.record_button.grid(row=0, column=1, padx=5)
        self.reset_button = ttk.Button(button_frame, text="Reset", command=self.reset_timer)
        self.reset_button.grid(row=0, column=2, padx=5)

        # Record list with scrollbar
        self.record_frame = ttk.Frame(self.root)
        self.record_frame.pack(pady=10, fill="both", padx=20)

        self.scrollbar = ttk.Scrollbar(self.record_frame)
        self.scrollbar.pack(side="right", fill="y")

        self.record_text = tk.Text(self.record_frame, height=5, width=30, font=("Helvetica", 10),
                                   yscrollcommand=self.scrollbar.set, bg="#FFDAB9", fg="#8B0000")
        self.record_text.pack(side="left", fill="both", expand=True)
        self.record_text.config(state="disabled")
        self.scrollbar.config(command=self.record_text.yview)

        # Load and display copy-to-clipboard icon
        try:
            if getattr(sys, 'frozen', False):  # Running in a packaged exe
                base_path = sys._MEIPASS
            else:
                base_path = os.path.dirname(__file__)
            icon_path = os.path.join(base_path, "imgs/copy.png")
            image = Image.open(icon_path).resize((32, 32), Image.LANCZOS)
            self.icon_image = ImageTk.PhotoImage(image)
            self.icon_label = tk.Label(self.record_frame, image=self.icon_image, 
                                       bg="#FFDAB9", cursor="hand2")
            self.icon_label.place(relx=1.0, rely=0.0, x=-20, y=5, anchor="ne")
            self.icon_label.lift()
            self.icon_label.bind("<Button-1>", lambda event: self.copy_records())
        except Exception as e:
            print(f"Failed to load icon: {e}")

        # Bind mouse wheel scrolling
        self.record_text.bind("<MouseWheel>", self.on_mouse_wheel)
        self.record_text.bind("<Button-4>", self.on_mouse_wheel)
        self.record_text.bind("<Button-5>", self.on_mouse_wheel)
        self.record_frame.bind("<MouseWheel>", self.on_mouse_wheel)
        self.record_frame.bind("<Button-4>", self.on_mouse_wheel)
        self.record_frame.bind("<Button-5>", self.on_mouse_wheel)

        # Load and display settings icon at bottom-left
        try:
            if getattr(sys, 'frozen', False):  # Running in a packaged exe
                base_path = sys._MEIPASS
            else:
                base_path = os.path.dirname(__file__)
            setting_path = os.path.join(base_path, "imgs/setting.png")
            setting_img = Image.open(setting_path).resize((24, 24), Image.LANCZOS)
            self.setting_image = ImageTk.PhotoImage(setting_img)

            self.setting_label = tk.Label(self.root, image=self.setting_image,
                                          bg="#FF6347", cursor="hand2")
            self.setting_label.place(relx=0.0, rely=1.0, x=10, y=-10, anchor="sw")
            self.setting_label.bind("<Button-1>", lambda e: self.open_settings())
        except Exception as e:
            print(f"Failed to load setting icon: {e}")

    def on_mouse_wheel(self, event):
        """Enable scrolling inside the record text widget with the mouse wheel."""
        if self.record_text.yview() != (0.0, 1.0):
            delta = -1 if (event.num == 4 or event.delta > 0) else 1
            self.record_text.yview_scroll(delta, "units")
        return "break"

    def copy_records(self):
        """Copy recorded times to the clipboard."""
        records_text = "\n".join(self.records)
        pyperclip.copy(records_text)

    def start_timer(self):
        """Toggle timer start/pause functionality."""
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
        """Record the current timer value and display it in the record text area."""
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
        """
        Display a custom alert window (centered) when a session ends.
        Used to notify the user to switch between work/break.
        """
        self.root.attributes("-topmost", False)
        alert = tk.Toplevel(self.root)
        alert.title("Pomodoro Timer")
        alert.geometry("300x150")
        alert.resizable(False, False)
        alert.configure(bg="#FF6347")
        alert.transient(self.root)
        alert.grab_set()
        alert.overrideredirect(True)

        # Center the alert window on screen
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
        """Close the alert window and resume the timer."""
        alert.destroy()
        self.is_running = True
        self.start_button.config(text="Pause")
        self.update_timer()

    def update_timer(self):
        """Update the timer countdown, progress bar, and handle session switching."""
        if self.is_running and self.current_time > 0:
            self.current_time -= 1
            minutes, seconds = divmod(self.current_time, 60)
            self.time_label.config(text=f"{minutes:02d}:{seconds:02d}")
            self.progress["value"] = self.current_time

            # Dynamically change progress bar color depending on session and progress
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

            # Continue updating every 1 second
            self.timer_id = self.root.after(1000, self.update_timer)
        elif self.current_time <= 0:
            # Session finished → switch work/break
            self.is_running = False
            self.root.attributes("-topmost", True)
            if self.is_minimized:
                self.is_minimized = False
                self.root.deiconify()
            self.root.focus_force()

            # Clear records when a session ends
            self.records.clear()
            self.record_text.config(state="normal")
            self.record_text.delete(1.0, tk.END)
            self.record_text.config(state="disabled")

            # Show alert and switch session type
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
        """Reset the timer back to the initial work session state."""
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

    def open_settings(self):
        """
        Open a settings window to adjust work and break durations.
        More work is on the way.
        """
        setting_win = tk.Toplevel(self.root)
        setting_win.title("Settings")
        setting_win.geometry("300x200")
        setting_win.resizable(False, True)
        setting_win.configure(bg="#FF6347")
        setting_win.transient(self.root)
        setting_win.grab_set()

        frame = tk.Frame(setting_win, bg="#FF6347")
        frame.pack(expand=True, fill="both", padx=20, pady=20)

        # Work time
        ttk.Label(frame, text="Work (min):").grid(row=0, column=0, padx=5, pady=5)
        work_var = tk.IntVar(value=self.work_time // 60)
        work_spin = ttk.Spinbox(frame, from_=1, to=180, textvariable=work_var, width=5)
        work_spin.grid(row=0, column=1, padx=5)
        ttk.Button(frame, text="Default", command=lambda: work_var.set(25)).grid(row=0, column=2, padx=5)

        # Break time
        ttk.Label(frame, text="Break (min):").grid(row=1, column=0, padx=5, pady=5)
        break_var = tk.IntVar(value=self.break_time // 60)
        break_spin = ttk.Spinbox(frame, from_=1, to=60, textvariable=break_var, width=5)
        break_spin.grid(row=1, column=1, padx=5)
        ttk.Button(frame, text="Default", command=lambda: break_var.set(5)).grid(row=1, column=2, padx=5)

        # Save button
        def save_settings():
            try:
                self.work_time = int(work_var.get()) * 60
                self.break_time = int(break_var.get()) * 60
                # Reset to apply immediately
                self.reset_timer()
                setting_win.destroy()
            except ValueError:
                pass

        save_btn = ttk.Button(setting_win, text="Save", command=save_settings)
        save_btn.pack(pady=10)

    def switch_mode(self):
        """Manually switch between work and break modes."""
        self.is_running = False
        self.start_button.config(text="Start")
        if self.is_work:
            # Switch to break mode
            self.is_work = False
            self.current_time = self.break_time
            self.title_label.config(text="Break Time")
        else:
            # Switch to work mode
            self.is_work = True
            self.current_time = self.work_time
            self.title_label.config(text="Work Time")

        # Update UI
        minutes, seconds = divmod(self.current_time, 60)
        self.time_label.config(text=f"{minutes:02d}:{seconds:02d}")
        self.progress["maximum"] = self.current_time
        self.progress["value"] = self.current_time
        self.style.configure("Custom.Horizontal.TProgressbar", background="#FF9999")

if __name__ == "__main__":
    # Entry point of the program
    root = tk.Tk()
    app = PomodoroTimer(root)
    root.mainloop()
