import tkinter as tk
from tkinter import ttk
import webbrowser

class WelcomeScreen:
    def __init__(self):
        self.setup_window()
        self.main_window = None

    def setup_window(self):
        self.root = tk.Tk()
        self.root.title("Welcome to LazyWorker")
        self.root.geometry("800x600")
        
        # Add window close handler
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)
        
        # Main frame
        main_frame = ttk.Frame(self.root, padding="20")
        main_frame.pack(fill="both", expand=True)
        
        # Header
        header_frame = ttk.Frame(main_frame)
        header_frame.pack(fill="x", pady=(0, 20))
        
        title = ttk.Label(
            header_frame,
            text="LazyWorker",
            font=("Segoe UI", 28, "bold")
        )
        title.pack()
        
        subtitle = ttk.Label(
            header_frame,
            text="Web Automation Made Easy",
            font=("Segoe UI", 14)
        )
        subtitle.pack()
        
        # Features frame
        features_frame = ttk.LabelFrame(main_frame, text="Features", padding="10")
        features_frame.pack(fill="both", expand=True)
        
        # Feature buttons
        features = [
            ("New Automation", "Start a new automation project", self.new_automation),
            ("Load Configuration", "Load an existing configuration", self.load_config),
            ("Documentation", "View documentation and help", self.open_docs),
            ("Settings", "Configure application settings", self.open_settings)
        ]
        
        for text, desc, command in features:
            feature_frame = ttk.Frame(features_frame)
            feature_frame.pack(fill="x", pady=5)
            
            btn = ttk.Button(
                feature_frame,
                text=text,
                command=command,
                width=20
            )
            btn.pack(side="left", padx=(0, 10))
            
            desc_label = ttk.Label(
                feature_frame,
                text=desc,
                font=("Segoe UI", 9)
            )
            desc_label.pack(side="left")
        
        # Footer
        footer_frame = ttk.Frame(main_frame)
        footer_frame.pack(fill="x", pady=(20, 0))
        
        version = ttk.Label(
            footer_frame,
            text="Version 1.0.0",
            font=("Segoe UI", 8)
        )
        version.pack(side="left")
        
        website = ttk.Label(
            footer_frame,
            text="arjunaprakarsa.com",
            font=("Segoe UI", 8, "underline"),
            foreground="blue",
            cursor="hand2"
        )
        website.pack(side="right")
        website.bind("<Button-1>", lambda e: webbrowser.open("https://arjunaprakarsa.com"))
    
    def on_closing(self):
        """Exit application when welcome screen is closed"""
        self.root.quit()
        self.root.destroy()
        import sys
        sys.exit(0)
    
    def new_automation(self):
        from main import LazyWorkerGUI
        self.main_window = LazyWorkerGUI(welcome_screen=self)
        self.root.withdraw()
        self.main_window.run()
        self.root.destroy()
        self.setup_window()  # Recreate window for next time
    
    def load_config(self):
        from main import LazyWorkerGUI
        self.main_window = LazyWorkerGUI(welcome_screen=self)
        self.main_window.load_config()
        self.root.withdraw()
        self.main_window.run()
        self.root.destroy()
        self.setup_window()  # Recreate window for next time
    
    def open_docs(self):
        # Open documentation in browser
        webbrowser.open("https://github.com/yourusername/LazyWorker/wiki")
    
    def open_settings(self):
        # TODO: Implement settings dialog
        pass
    
    def show(self):
        self.root.deiconify()
        self.root.lift()
    
    def run(self):
        self.root.mainloop()
