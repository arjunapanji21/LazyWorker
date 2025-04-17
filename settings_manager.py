import json
import os

class SettingsManager:
    DEFAULT_SETTINGS = {
        "wait_timeout": 10,
        "page_load_timeout": 30,
        "implicit_wait": 5,
        "max_retries": 3,
        "action_delay": 0.2
    }
    
    def __init__(self):
        self.settings_file = "configs/settings.json"
        self.settings = self.load_settings()
    
    def load_settings(self):
        try:
            if os.path.exists(self.settings_file):
                with open(self.settings_file, 'r') as f:
                    return {**self.DEFAULT_SETTINGS, **json.load(f)}
            return self.DEFAULT_SETTINGS.copy()
        except:
            return self.DEFAULT_SETTINGS.copy()
    
    def save_settings(self, settings):
        os.makedirs(os.path.dirname(self.settings_file), exist_ok=True)
        with open(self.settings_file, 'w') as f:
            json.dump(settings, f, indent=4)
        self.settings = settings
