import tkinter as tk
from tkinter import ttk
import time

class SplashScreen:
    def __init__(self, duration=2):
        self.duration = duration
        self.root = tk.Tk()
        self.root.overrideredirect(True)
        self.root.attributes('-alpha', 0.9)
        
        # Center splash screen
        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()
        width = 400
        height = 300
        x = (screen_width - width) // 2
        y = (screen_height - height) // 2
        self.root.geometry(f'{width}x{height}+{x}+{y}')
        
        # Add content
        frame = ttk.Frame(self.root, padding="20")
        frame.pack(fill="both", expand=True)
        
        # Logo/Title
        title = ttk.Label(
            frame, 
            text="LazyWorker",
            font=("Segoe UI", 24, "bold")
        )
        title.pack(pady=(20, 10))
        
        # Version
        version = ttk.Label(
            frame,
            text="Version 1.0.0",
            font=("Segoe UI", 10)
        )
        version.pack()
        
        # Loading bar
        self.progress = ttk.Progressbar(
            frame,
            mode='determinate',
            length=300
        )
        self.progress.pack(pady=20)
        
        # Loading text
        self.status = ttk.Label(
            frame,
            text="Loading...",
            font=("Segoe UI", 9)
        )
        self.status.pack()
        
        # Copyright
        copyright = ttk.Label(
            frame,
            text="© 2024 Arjuna Panji Prakarsa",
            font=("Segoe UI", 8)
        )
        copyright.pack(side="bottom", pady=10)

    def show(self):
        for i in range(100):
            self.progress['value'] = i
            if i < 30:
                self.status['text'] = "Initializing..."
            elif i < 60:
                self.status['text'] = "Loading components..."
            elif i < 90:
                self.status['text'] = "Starting application..."
            else:
                self.status['text'] = "Ready!"
            self.root.update()
            time.sleep(self.duration/100)
        self.root.destroy()
