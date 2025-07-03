import os
import json
import platform
import tkinter as tk
from tkinter import ttk, messagebox

class ConfigManager:
    def __init__(self):
        self.config_filename = "config.json"
        self.default_settings = {
            "open_dir_after_split": False,
            "enable_logging": True,
            "default_output_file_type": ".csv",
            "retain_header": True
        }
        self.settings = self.load_settings()
    
    def get_config_path(self):
        """Get the OS-appropriate configuration file path"""
        app_name = "FileSplitterPro"
        
        system = platform.system()
        
        try:
            if system == "Windows":
                # Windows: %APPDATA%\FileSplitterPro\config.json
                config_dir = os.path.join(os.environ.get('APPDATA', ''), app_name)
            elif system == "Darwin":  # macOS
                # macOS: ~/Library/Application Support/FileSplitterPro/config.json
                home = os.path.expanduser("~")
                config_dir = os.path.join(home, "Library", "Application Support", app_name)
            else:  # Linux and others
                # Linux: ~/.config/FileSplitterPro/config.json (respects XDG_CONFIG_HOME)
                xdg_config = os.environ.get('XDG_CONFIG_HOME')
                if xdg_config:
                    config_dir = os.path.join(xdg_config, app_name)
                else:
                    home = os.path.expanduser("~")
                    config_dir = os.path.join(home, ".config", app_name)
            
            # Create directory if it doesn't exist
            os.makedirs(config_dir, exist_ok=True)
            return os.path.join(config_dir, self.config_filename)
            
        except (OSError, KeyError, TypeError) as e:
            print(f"Warning: Could not access system config directory: {e}")
            # Fallback to current directory
            return self.config_filename
    
    def migrate_old_config(self, new_path):
        """Migrate old settings.json from current directory to new location"""
        old_config = "settings.json"
        if os.path.exists(old_config) and not os.path.exists(new_path):
            try:
                with open(old_config, 'r') as f:
                    old_settings = json.load(f)
                
                # Save to new location
                with open(new_path, 'w') as f:
                    json.dump(old_settings, f, indent=2)
                
                print(f"Migrated settings from {old_config} to {new_path}")
                
                # Optionally remove old file (commented out for safety)
                # os.remove(old_config)
                
                return old_settings
            except Exception as e:
                print(f"Warning: Could not migrate old config: {e}")
        
        return None
    
    def load_settings(self):
        """Load settings from config file or use defaults"""
        config_path = self.get_config_path()
        
        # Try to migrate from old location first
        migrated_settings = self.migrate_old_config(config_path)
        if migrated_settings:
            # Merge with defaults to ensure all keys exist
            settings = self.default_settings.copy()
            settings.update(migrated_settings)
            return settings
        
        # Load from new location
        try:
            if os.path.exists(config_path):
                with open(config_path, 'r') as f:
                    loaded_settings = json.load(f)
                # Merge with defaults to ensure all keys exist
                settings = self.default_settings.copy()
                settings.update(loaded_settings)
                return settings
        except Exception as e:
            print(f"Error loading settings from {config_path}: {e}")
        
        return self.default_settings.copy()
    
    def save_settings(self):
        """Save current settings to config file"""
        config_path = self.get_config_path()
        try:
            with open(config_path, 'w') as f:
                json.dump(self.settings, f, indent=2)
            return True
        except Exception as e:
            print(f"Error saving settings to {config_path}: {e}")
            return False
    
    def get(self, key):
        """Get a setting value"""
        return self.settings.get(key, self.default_settings.get(key))
    
    def set(self, key, value):
        """Set a setting value"""
        self.settings[key] = value
    
    def open_settings_window(self, parent):
        """Open the settings configuration window"""
        return SettingsWindow(parent, self)

class SettingsWindow:
    def __init__(self, parent, config_manager):
        self.parent = parent
        self.config_manager = config_manager
        self.result = None
        
        # Create window
        self.window = tk.Toplevel(parent)
        self.window.title("Settings")
        self.window.geometry("340x280")
        self.window.resizable(False, False)
        self.window.transient(parent)
        self.window.grab_set()
        
        # Center the window
        self.window.update_idletasks()
        x = (self.window.winfo_screenwidth() // 2) - (380 // 2)
        y = (self.window.winfo_screenheight() // 2) - (350 // 2)
        self.window.geometry(f"340x280+{x}+{y}")
        
        # Initialize variables with current settings
        self.open_dir_after_split = tk.BooleanVar(value=self.config_manager.get("open_dir_after_split"))
        self.enable_logging = tk.BooleanVar(value=self.config_manager.get("enable_logging"))
        self.default_output_file_type = tk.StringVar(value=self.config_manager.get("default_output_file_type"))
        self.retain_header = tk.BooleanVar(value=self.config_manager.get("retain_header"))
        
        self.create_widgets()
        
    def create_widgets(self):
        main_frame = ttk.Frame(self.window, padding="20")
        main_frame.grid(row=0, column=0, sticky="nsew")
        self.window.columnconfigure(0, weight=1)
        self.window.rowconfigure(0, weight=1)
        
        # Title
        title_label = ttk.Label(main_frame, text="Application Settings", 
                               font=("Segoe UI", 12, "bold"))
        title_label.grid(row=0, column=0, columnspan=2, pady=(0, 20), sticky="w")
        
        # Create notebook for tabs
        notebook = ttk.Notebook(main_frame)
        notebook.grid(row=1, column=0, columnspan=2, sticky="ew", pady=(0, 20))
        
        # General Tab
        general_frame = ttk.Frame(notebook, padding=20)
        notebook.add(general_frame, text="General")
        
        # Open Output Directory
        ttk.Checkbutton(general_frame, text="Open Output Directory", 
                       variable=self.open_dir_after_split).grid(row=0, column=0, sticky="w", pady=(0, 15))
        
        # Split Tab
        split_frame = ttk.Frame(notebook, padding=20)
        notebook.add(split_frame, text="Split")
        
        # Retain Header Row
        ttk.Checkbutton(split_frame, text="Retain Header Row (Default)", 
                       variable=self.retain_header).grid(row=0, column=0, columnspan=2, sticky="w", pady=(0, 15))
        
        # Default Output File Type
        file_type_frame = ttk.Frame(split_frame)
        file_type_frame.grid(row=1, column=0, columnspan=2, sticky="w", pady=(0, 15))
        
        ttk.Label(file_type_frame, text="Default Output File Type:").pack(side="left")
        file_type_combo = ttk.Combobox(file_type_frame, textvariable=self.default_output_file_type, 
                                      values=[".csv", ".txt", ".dat", ".json"], width=10, state="readonly")
        file_type_combo.pack(side="left", padx=(10, 0))
        
        # Logging Tab
        logging_frame = ttk.Frame(notebook, padding=20)
        notebook.add(logging_frame, text="Logging")
        
        # Enable Logging
        ttk.Checkbutton(logging_frame, text="Enable Logging", 
                       variable=self.enable_logging).grid(row=0, column=0, sticky="w", pady=(0, 15))
        
        # Configure grid weights
        main_frame.columnconfigure(0, weight=1)
        
        # Bottom buttons
        button_frame = ttk.Frame(main_frame)
        button_frame.grid(row=2, column=0, columnspan=2, sticky="ew")
        
        ttk.Button(button_frame, text="Save", command=self.ok_clicked).grid(row=0, column=0, padx=(0, 10))
        ttk.Button(button_frame, text="Cancel", command=self.cancel_clicked).grid(row=0, column=1, padx=(0, 10))
        ttk.Button(button_frame, text="Reset to Defaults", command=self.reset_defaults, width=18).grid(row=0, column=2)
        
    def reset_defaults(self):
        """Reset all settings to defaults"""
        self.open_dir_after_split.set(self.config_manager.default_settings["open_dir_after_split"])
        self.enable_logging.set(self.config_manager.default_settings["enable_logging"])
        self.default_output_file_type.set(self.config_manager.default_settings["default_output_file_type"])
        self.retain_header.set(self.config_manager.default_settings["retain_header"])
        
    def ok_clicked(self):
        """User clicked OK - update settings and attempt to save"""
        # Update config manager with new values
        self.config_manager.set("open_dir_after_split", self.open_dir_after_split.get())
        self.config_manager.set("enable_logging", self.enable_logging.get())
        self.config_manager.set("default_output_file_type", self.default_output_file_type.get())
        self.config_manager.set("retain_header", self.retain_header.get())
        
        # Attempt to save to file
        save_success = self.config_manager.save_settings()
        if not save_success:
            messagebox.showwarning(
                "Save Warning", 
                "Settings were updated but could not be saved to disk. "
                "They will be lost when the application closes."
            )
        
        self.result = True
        self.window.destroy()
    
    def cancel_clicked(self):
        """User clicked Cancel"""
        self.result = False
        self.window.destroy()