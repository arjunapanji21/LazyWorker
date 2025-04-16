import json
import os

class ConfigManager:
    def __init__(self):
        self.config_file = "automatask_config.json"
    
    def save_config(self, config):
        with open(self.config_file, 'w') as f:
            json.dump(config, f, indent=4)
    
    def load_config(self):
        if not os.path.exists(self.config_file):
            return None
        
        with open(self.config_file, 'r') as f:
            return json.load(f)
    
    def apply_config(self, gui, config):
        gui.url_entry.delete(0, 'end')
        gui.url_entry.insert(0, config['url'])
        
        gui.form_url_entry.delete(0, 'end')
        gui.form_url_entry.insert(0, config.get('form_url', ''))
        
        gui.username_entry.delete(0, 'end')
        gui.username_entry.insert(0, config['username'])
        
        gui.password_entry.delete(0, 'end')
        gui.password_entry.insert(0, config['password'])
        
        gui.file_path.set(config['excel_file'])
        
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
        if 'post_submit_actions' in config:
            for action in sorted(config['post_submit_actions'], key=lambda x: x['order']):
                gui.actions_tree.insert("", "end", values=(
                    action['order'],
                    action['action'],
                    action['selector_type'],
                    action['selector'],
                    action['delay']
                ))
