import os
import json
import tkinter as tk
from tkinter import ttk

class ConfigManager:
    def __init__(self):
        self.config_file = "settings.json"
        self.default_settings = {
            "open_dir_after_split": False,
            "enable_logging": True,
            "default_output_file_type": ".csv",
            "retain_header": True
        }
        self.settings = self.load_settings()
    
    def load_settings(self):
        """Load settings from config file or use defaults"""
        try:
            if os.path.exists(self.config_file):
                with open(self.config_file, 'r') as f:
                    loaded_settings = json.load(f)
                # Merge with defaults to ensure all keys exist
                settings = self.default_settings.copy()
                settings.update(loaded_settings)
                return settings
        except Exception as e:
            print(f"Error loading settings: {e}")
        
        return self.default_settings.copy()
    
    def save_settings(self):
        """Save current settings to config file"""
        try:
            with open(self.config_file, 'w') as f:
                json.dump(self.settings, f, indent=2)
        except Exception as e:
            print(f"Error saving settings: {e}")
    
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
        self.window.geometry("330x300")
        self.window.resizable(False, False)
        self.window.transient(parent)
        self.window.grab_set()
        
        # Center the window
        self.window.update_idletasks()
        x = (self.window.winfo_screenwidth() // 2) - (450 // 2)
        y = (self.window.winfo_screenheight() // 2) - (300 // 2)
        self.window.geometry(f"330x300+{x}+{y}")
        
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
        
        # Settings frame
        settings_frame = ttk.LabelFrame(main_frame, text="General Settings", padding=15)
        settings_frame.grid(row=1, column=0, columnspan=2, sticky="ew", pady=(0, 20))
        
        # Open Directory After Split
        ttk.Checkbutton(settings_frame, text="Open Directory After Split", 
                       variable=self.open_dir_after_split).grid(row=0, column=0, columnspan=2, sticky="w", pady=(0, 12))
        
        # Enable Logging
        ttk.Checkbutton(settings_frame, text="Enable Logging", 
                       variable=self.enable_logging).grid(row=1, column=0, columnspan=2, sticky="w", pady=(0, 12))
        
        # Retain Header Row
        ttk.Checkbutton(settings_frame, text="Retain Header Row (Default)", 
                       variable=self.retain_header).grid(row=2, column=0, columnspan=2, sticky="w", pady=(0, 15))
        
        # Default Output File Type
        file_type_frame = ttk.Frame(settings_frame)
        file_type_frame.grid(row=3, column=0, columnspan=2, sticky="w", pady=(0, 0))
        
        ttk.Label(file_type_frame, text="Default Output File Type:").pack(side="left")
        file_type_combo = ttk.Combobox(file_type_frame, textvariable=self.default_output_file_type, 
                                      values=[".csv", ".txt", ".dat", ".json"], width=10, state="readonly")
        file_type_combo.pack(side="left", padx=(5, 0))
        
        # Configure grid weights
        settings_frame.columnconfigure(0, weight=1)
        main_frame.columnconfigure(0, weight=1)
        
        # Bottom buttons
        button_frame = ttk.Frame(main_frame)
        button_frame.grid(row=2, column=0, columnspan=2, sticky="ew")
        
        ttk.Button(button_frame, text="OK", command=self.ok_clicked).grid(row=0, column=0, padx=(0, 10))
        ttk.Button(button_frame, text="Cancel", command=self.cancel_clicked).grid(row=0, column=1, padx=(0, 10))
        ttk.Button(button_frame, text="Reset to Defaults", command=self.reset_defaults).grid(row=0, column=2)
        
    def reset_defaults(self):
        """Reset all settings to defaults"""
        self.open_dir_after_split.set(self.config_manager.default_settings["open_dir_after_split"])
        self.enable_logging.set(self.config_manager.default_settings["enable_logging"])
        self.default_output_file_type.set(self.config_manager.default_settings["default_output_file_type"])
        self.retain_header.set(self.config_manager.default_settings["retain_header"])
        
    def ok_clicked(self):
        """User clicked OK - save settings"""
        # Update config manager with new values
        self.config_manager.set("open_dir_after_split", self.open_dir_after_split.get())
        self.config_manager.set("enable_logging", self.enable_logging.get())
        self.config_manager.set("default_output_file_type", self.default_output_file_type.get())
        self.config_manager.set("retain_header", self.retain_header.get())
        
        # Save to file
        self.config_manager.save_settings()
        
        self.result = True
        self.window.destroy()
    
    def cancel_clicked(self):
        """User clicked Cancel"""
        self.result = False
        self.window.destroy()