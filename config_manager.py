import json
import os
from datetime import datetime

class ConfigManager:
    def __init__(self):
        self.config_dir = "configs"
        if not os.path.exists(self.config_dir):
            os.makedirs(self.config_dir)
    
    def save_config(self, config, name=None):
        if name is None:
            # Generate default name using timestamp
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            name = f"config_{timestamp}"
        
        # Ensure .json extension
        if not name.endswith('.json'):
            name += '.json'
        
        filepath = os.path.join(self.config_dir, name)
        with open(filepath, 'w') as f:
            json.dump(config, f, indent=4)
        return name
    
    def load_config(self, filename=None):
        if filename is None:
            return None
        
        filepath = os.path.join(self.config_dir, filename)
        if not os.path.exists(filepath):
            return None
        
        with open(filepath, 'r') as f:
            return json.load(f)
    
    def get_config_list(self):
        """Get list of available configurations"""
        configs = []
        for file in os.listdir(self.config_dir):
            if file.endswith('.json'):
                configs.append(file)
        return sorted(configs)
    
    def apply_config(self, gui, config):
        gui.url_entry.delete(0, 'end')
        gui.url_entry.insert(0, config['url'])
        
        gui.form_url_entry.delete(0, 'end')
        gui.form_url_entry.insert(0, config.get('form_url', ''))
        
        gui.username_entry.delete(0, 'end')
        gui.username_entry.insert(0, config['username'])
        
        gui.password_entry.delete(0, 'end')
        gui.password_entry.insert(0, config['password'])
        
        # Handle Excel file path
        excel_path = config.get('excel_file', '')
        if excel_path:
            # Update display path
            display_path = excel_path
            if len(display_path) > 40:
                display_path = "..." + display_path[-37:]
            gui.file_path.set(display_path)
            # Store full path
            gui.file_path_label.full_path = excel_path
        
        # Clear existing mappings in tree
        for item in gui.mapping_tree.get_children():
            gui.mapping_tree.delete(item)
        
        # Add loaded mappings
        for mapping in config['field_mappings']:
            gui.mapping_tree.insert("", "end", values=(
                mapping['excel_column'],
                mapping.get('selector_type', 'CSS'),  # Default to CSS for backward compatibility
                mapping['web_selector']
            ))
            
        # Clear existing actions in tree
        for item in gui.actions_tree.get_children():
            gui.actions_tree.delete(item)
            
        # Add loaded actions
        for action in config.get('post_submit_actions', []):
            gui.actions_tree.insert("", "end", values=(
                action.get('order', ''),
                action.get('action', ''),
                action.get('selector_type', ''),
                action.get('selector', ''),
                action.get('condition', ''), # Add condition field
                action.get('delay', '')
            ))
        
        # Update auto confirm setting if present
        if 'auto_confirm' in config:
            gui.auto_confirm.set(config['auto_confirm'])
