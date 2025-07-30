import os
import csv
import threading
import tkinter as tk
from tkinter import ttk, filedialog, messagebox, Menu, simpledialog
import webbrowser
import time
import json
import math
import platform

class ColumnSelectionWindow:
    def __init__(self, parent, columns, selected_columns, column_renames=None):
        self.parent = parent
        self.columns = columns
        self.selected_columns = selected_columns.copy()
        self.column_renames = column_renames.copy() if column_renames else {}
        self.result = None
        self.result_renames = None
        
        # Store original state for reset functionality
        self.original_selected_columns = selected_columns.copy()
        self.original_column_renames = column_renames.copy() if column_renames else {}
        
        # Create window
        self.window = tk.Toplevel(parent)
        self.window.title("Column Filter")
        self.window.geometry("500x370")
        self.window.resizable(True, True)
        self.window.transient(parent)
        self.window.grab_set()
        
        # Center the window
        self.window.update_idletasks()
        x = (self.window.winfo_screenwidth() // 2) - (500 // 2)
        y = (self.window.winfo_screenheight() // 2) - (450 // 2)
        self.window.geometry(f"500x370+{x}+{y}")
        
        self.create_widgets()
        self.populate_lists()
        
    def create_widgets(self):
        main_frame = ttk.Frame(self.window, padding="15")
        main_frame.grid(row=0, column=0, sticky="nsew")
        self.window.columnconfigure(0, weight=1)
        self.window.rowconfigure(0, weight=1)
        
        # Left side - Excluded columns
        excluded_frame = ttk.LabelFrame(main_frame, text="Excluded Columns", padding=10)
        excluded_frame.grid(row=0, column=0, sticky="nsew", padx=(0, 5))
        
        self.excluded_listbox = tk.Listbox(excluded_frame, selectmode=tk.EXTENDED)
        excluded_scrollbar = ttk.Scrollbar(excluded_frame, orient="vertical", command=self.excluded_listbox.yview)
        self.excluded_listbox.configure(yscrollcommand=excluded_scrollbar.set)
        
        self.excluded_listbox.grid(row=0, column=0, sticky="nsew")
        excluded_scrollbar.grid(row=0, column=1, sticky="ns")
        excluded_frame.columnconfigure(0, weight=1)
        excluded_frame.rowconfigure(0, weight=1)
        
        # Center buttons
        button_frame = ttk.Frame(main_frame)
        button_frame.grid(row=0, column=1, sticky="ns", padx=10)
        
        # Add some vertical spacing
        ttk.Label(button_frame, text="").grid(row=0, column=0, pady=20)
        
        self.include_button = ttk.Button(button_frame, text="Include →", command=self.include_selected)
        self.include_button.grid(row=1, column=0, pady=5, sticky="ew")
        
        self.exclude_button = ttk.Button(button_frame, text="← Exclude", command=self.exclude_selected)
        self.exclude_button.grid(row=2, column=0, pady=5, sticky="ew")
        
        ttk.Separator(button_frame, orient="horizontal").grid(row=3, column=0, pady=10, sticky="ew")
        
        self.include_all_button = ttk.Button(button_frame, text="Include All", command=self.include_all)
        self.include_all_button.grid(row=4, column=0, pady=5, sticky="ew")
        
        self.exclude_all_button = ttk.Button(button_frame, text="Exclude All", command=self.exclude_all)
        self.exclude_all_button.grid(row=5, column=0, pady=5, sticky="ew")
        
        ttk.Separator(button_frame, orient="horizontal").grid(row=6, column=0, pady=10, sticky="ew")
        
        # Add rename button
        self.rename_button = ttk.Button(button_frame, text="Rename", command=self.rename_selected, state="disabled")
        self.rename_button.grid(row=7, column=0, pady=5, sticky="ew")
        
        # Right side - Included columns
        included_frame = ttk.LabelFrame(main_frame, text="Included Columns", padding=10)
        included_frame.grid(row=0, column=2, sticky="nsew", padx=(5, 0))
        
        self.included_listbox = tk.Listbox(included_frame, selectmode=tk.EXTENDED)
        included_scrollbar = ttk.Scrollbar(included_frame, orient="vertical", command=self.included_listbox.yview)
        self.included_listbox.configure(yscrollcommand=included_scrollbar.set)
        
        self.included_listbox.grid(row=0, column=0, sticky="nsew")
        included_scrollbar.grid(row=0, column=1, sticky="ns")
        included_frame.columnconfigure(0, weight=1)
        included_frame.rowconfigure(0, weight=1)
        
        # Bind selection event to enable/disable rename button
        self.included_listbox.bind('<<ListboxSelect>>', self.on_included_selection_change)
        
        # Bottom buttons
        bottom_frame = ttk.Frame(main_frame)
        bottom_frame.grid(row=1, column=0, columnspan=3, pady=(15, 0), sticky="ew")
        
        # Reset button on the left
        self.reset_button = ttk.Button(bottom_frame, text="Reset", command=self.reset_to_defaults, state="disabled")
        self.reset_button.pack(side="left")
        
        # Save and Cancel buttons on the right
        right_buttons = ttk.Frame(bottom_frame)
        right_buttons.pack(side="right")
        
        ttk.Button(right_buttons, text="Save", command=self.ok_clicked).pack(side="left", padx=(0, 10))
        ttk.Button(right_buttons, text="Cancel", command=self.cancel_clicked).pack(side="left")
        
        # Configure grid weights
        main_frame.columnconfigure(0, weight=1)
        main_frame.columnconfigure(2, weight=1)
        main_frame.rowconfigure(0, weight=1)
        
    def has_changes(self):
        """Check if any changes have been made from the original state"""
        # Check if selected columns have changed
        if set(self.selected_columns) != set(self.original_selected_columns):
            return True
        
        # Check if any columns have been renamed
        if self.column_renames != self.original_column_renames:
            return True
            
        return False
    
    def update_reset_button_state(self):
        """Enable or disable the reset button based on whether changes have been made"""
        if self.has_changes():
            self.reset_button.config(state="normal")
        else:
            self.reset_button.config(state="disabled")
    
    def reset_to_defaults(self):
        """Reset the dialog to its default state"""
        # Reset selected columns to original state
        self.selected_columns = self.original_selected_columns.copy()
        
        # Clear all column renames
        self.column_renames = self.original_column_renames.copy()
        
        # Refresh the display
        self.populate_lists()
        
        # Update button states
        self.update_reset_button_state()

    def on_included_selection_change(self, event):
        """Handle selection change in the included columns listbox"""
        selected_indices = self.included_listbox.curselection()
        
        # Enable rename button only if exactly one item is selected
        if len(selected_indices) == 1:
            self.rename_button.config(state="normal")
        else:
            self.rename_button.config(state="disabled")
    
    def get_display_name(self, column_name):
        """Get the display name for a column (renamed or original)"""
        return self.column_renames.get(column_name, column_name)
    
    def populate_lists(self):
        """Populate the listboxes with columns"""
        excluded_columns = [col for col in self.columns if col not in self.selected_columns]
        
        self.excluded_listbox.delete(0, tk.END)
        for col in excluded_columns:
            display_name = self.get_display_name(col)
            self.excluded_listbox.insert(tk.END, display_name)
            
        self.included_listbox.delete(0, tk.END)
        for col in self.selected_columns:
            display_name = self.get_display_name(col)
            self.included_listbox.insert(tk.END, display_name)
        
        # Reset rename button state since selection is cleared
        self.rename_button.config(state="disabled")
        
        # Update reset button state
        self.update_reset_button_state()
    
    def get_original_column_name(self, display_name):
        """Get the original column name from a display name"""
        # Find the original name by looking through the renames mapping
        for original, renamed in self.column_renames.items():
            if renamed == display_name:
                return original
        # If not found in renames, it's likely the original name itself
        return display_name
    
    def rename_selected(self):
        """Allow user to rename the selected column in the included list"""
        selected_indices = self.included_listbox.curselection()
        
        if not selected_indices:
            messagebox.showwarning("Warning", "Please select a column from the 'Included Columns' list to rename.")
            return
            
        # Since button is only enabled when exactly one item is selected, this check is redundant now
        # but keeping it for safety
        if len(selected_indices) > 1:
            messagebox.showwarning("Warning", "Please select only one column to rename.")
            return
            
        selected_index = selected_indices[0]
        current_display_name = self.included_listbox.get(selected_index)
        original_name = self.get_original_column_name(current_display_name)
        
        # Create a custom dialog for renaming
        new_name = self.show_rename_dialog(current_display_name)
        
        if new_name and new_name.strip():
            new_name = new_name.strip()
            
            # Check if the new name conflicts with other renamed columns
            existing_renames = set(self.column_renames.values())
            if new_name in existing_renames and new_name != current_display_name:
                messagebox.showwarning("Warning", f"The name '{new_name}' is already used by another column.")
                return
                
            # Update the rename mapping
            if new_name != original_name:
                self.column_renames[original_name] = new_name
            else:
                # If renamed back to original, remove from renames mapping
                if original_name in self.column_renames:
                    del self.column_renames[original_name]
            
            # Refresh the display
            self.populate_lists()
            
            # Re-select the renamed item to keep it selected
            for i in range(self.included_listbox.size()):
                if self.get_original_column_name(self.included_listbox.get(i)) == original_name:
                    self.included_listbox.selection_set(i)
                    self.rename_button.config(state="normal")
                    break
            
            # Update reset button state is called automatically by populate_lists()

    def show_rename_dialog(self, current_name):
        """Show a custom rename dialog with better sizing"""
        # Create the dialog window
        dialog = tk.Toplevel(self.window)
        dialog.title("Rename Column")
        dialog.geometry("400x180")
        dialog.resizable(False, False)
        dialog.transient(self.window)
        dialog.grab_set()
        
        # Center the dialog
        dialog.update_idletasks()
        x = (dialog.winfo_screenwidth() // 2) - (400 // 2)
        y = (dialog.winfo_screenheight() // 2) - (180 // 2)
        dialog.geometry(f"400x180+{x}+{y}")
        
        result = {"value": None}
        
        # Create the content frame
        main_frame = ttk.Frame(dialog, padding="20")
        main_frame.pack(fill="both", expand=True)
        
        # Label
        label = ttk.Label(main_frame, text=f"Enter new name for column:")
        label.pack(pady=(0, 5))
        
        # Current name label (in bold to make it clear)
        current_label = ttk.Label(main_frame, text=current_name, font=("Segoe UI", 11, "bold"))
        current_label.pack(pady=(0, 15))
        
        # Entry field
        entry_var = tk.StringVar(value=current_name)
        entry = ttk.Entry(main_frame, textvariable=entry_var, font=("Segoe UI", 10), width=40)
        entry.pack(pady=(0, 20), ipady=3)
        entry.select_range(0, tk.END)  # Select all text
        entry.focus()
        
        # Button frame
        button_frame = ttk.Frame(main_frame)
        button_frame.pack()
        
        def on_ok():
            result["value"] = entry_var.get()
            dialog.destroy()
            
        def on_cancel():
            result["value"] = None
            dialog.destroy()
            
        def on_enter(event):
            on_ok()
        
        # Bind Enter key to OK
        entry.bind('<Return>', on_enter)
        dialog.bind('<Escape>', lambda e: on_cancel())
        
        # Buttons
        ok_button = ttk.Button(button_frame, text="Save", command=on_ok)
        ok_button.pack(side="left", padx=(0, 10))
        
        cancel_button = ttk.Button(button_frame, text="Cancel", command=on_cancel)
        cancel_button.pack(side="left")
        
        # Wait for dialog to close
        dialog.wait_window()
        
        return result["value"]
    
    def include_selected(self):
        """Move selected columns from excluded to included"""
        selected_indices = self.excluded_listbox.curselection()
        selected_display_names = [self.excluded_listbox.get(i) for i in selected_indices]
        
        for display_name in selected_display_names:
            original_name = self.get_original_column_name(display_name)
            if original_name not in self.selected_columns:
                self.selected_columns.append(original_name)
            
        self.populate_lists()
    
    def exclude_selected(self):
        """Move selected columns from included to excluded"""
        selected_indices = self.included_listbox.curselection()
        selected_display_names = [self.included_listbox.get(i) for i in selected_indices]
        
        for display_name in selected_display_names:
            original_name = self.get_original_column_name(display_name)
            if original_name in self.selected_columns:
                self.selected_columns.remove(original_name)
                
        self.populate_lists()
    
    def include_all(self):
        """Move all columns to included"""
        self.selected_columns = self.columns.copy()
        self.populate_lists()
    
    def exclude_all(self):
        """Move all columns to excluded"""
        self.selected_columns = []
        self.populate_lists()
    
    def ok_clicked(self):
        """User clicked OK"""
        if not self.selected_columns:
            messagebox.showwarning("Warning", "You must include at least one column.")
            return
            
        self.result = self.selected_columns.copy()
        self.result_renames = self.column_renames.copy()
        self.window.destroy()
    
    def cancel_clicked(self):
        """User clicked Cancel"""
        self.result = None
        self.result_renames = None
        self.window.destroy()

class FileSplitterApp:
    def __init__(self, root):
        self.root = root
        self.root.title("File Splitter Pro")

        try:
            icon_path = os.path.join(os.path.dirname(__file__), "filesplit_icon.ico")
            self.root.iconbitmap(default=icon_path)
        except Exception as e:
            print(f"Warning: Could not load icon. {e}")
        
        self.root.geometry("450x700")  # Further reduced height since we removed another checkbox
        self.root.resizable(False, False)
        
        # Configure style
        self.setup_styles()

        # Variables
        self.input_file = tk.StringVar()
        self.split_value = tk.StringVar()  # Single value for both size and rows
        self.file_type = tk.StringVar(value=".csv")
        self.output_dir = tk.StringVar()
        self.split_mode = tk.StringVar(value="Size (MB)")  # Changed to descriptive text
        self.use_custom_delim = tk.BooleanVar(value=False)
        self.custom_delimiter = tk.StringVar(value="")
        self.detected_delimiter = tk.StringVar(value="")
        self.quote_mode = tk.StringVar(value="Standard")  # New: Quote mode selection
        self.open_dir_after_split = tk.BooleanVar(value=False)
        self.create_log = tk.BooleanVar(value=True)
        self.retain_header = tk.BooleanVar(value=True)  # NEW: Default to retaining header

        # Column selection variables
        self.available_columns = []
        self.selected_columns = []
        self.column_renames = {}  # Maps original column names to renamed versions

        # Progress tracking
        self.cancel_event = threading.Event()
        self.is_running = False
        self.start_time = 0
        
        # Stats variables
        self.current_file = tk.StringVar(value="")
        self.rows_processed = tk.StringVar(value="")
        self.total_rows = tk.StringVar(value="")
        self.progress_percentage = tk.StringVar(value="")
        self.output_file_type = tk.StringVar(value="")
        self.file_count = tk.StringVar(value="")

        # Validation tracking
        self.input_row_count = 0
        self.output_row_count = 0
        self.current_part_num = 0

        # Load configuration settings
        self.load_config()

        self.create_menu()
        self.create_widgets()
        self.input_file.trace_add("write", self.on_input_file_change)
        self.file_type.trace_add("write", self.on_file_type_change)
        self.split_value.trace_add("write", self.on_split_value_change)  # Add trace for split value
        
        # Add traces for settings to auto-save config when changed
        self.open_dir_after_split.trace_add("write", self.on_setting_change)
        self.create_log.trace_add("write", self.on_setting_change)
        self.retain_header.trace_add("write", self.on_setting_change)
        
        # Set up keyboard shortcuts
        self.setup_keyboard_shortcuts()

    def get_config_dir(self):
        """Get the appropriate configuration directory for the current OS"""
        system = platform.system()
        
        if system == "Windows":
            # Use %APPDATA% on Windows
            config_dir = os.path.join(os.getenv('APPDATA'), 'FileSplitterPro')
        elif system == "Darwin":  # macOS
            # Use ~/Library/Application Support on macOS
            home_dir = os.path.expanduser("~")
            config_dir = os.path.join(home_dir, "Library", "Application Support", "FileSplitterPro")
        else:  # Linux and other Unix-like systems
            # Use ~/.config on Linux
            home_dir = os.path.expanduser("~")
            config_dir = os.path.join(home_dir, ".config", "FileSplitterPro")
        
        return config_dir

    def get_config_file_path(self):
        """Get the full path to the config.json file"""
        return os.path.join(self.get_config_dir(), "config.json")

    def load_config(self):
        """Load configuration settings from config.json"""
        config_file = self.get_config_file_path()
        
        try:
            if os.path.exists(config_file):
                with open(config_file, 'r', encoding='utf-8') as f:
                    config = json.load(f)
                
                # Load settings with defaults
                self.open_dir_after_split.set(config.get('open_dir_after_split', False))
                self.create_log.set(config.get('create_log', True))
                self.retain_header.set(config.get('retain_header', True))
                
                print(f"Configuration loaded from: {config_file}")
            else:
                print(f"No config file found at: {config_file}. Using defaults.")
                
        except Exception as e:
            print(f"Error loading config: {e}. Using defaults.")
            # Keep default values if loading fails

    def save_config(self):
        """Save current configuration settings to config.json"""
        config_dir = self.get_config_dir()
        config_file = self.get_config_file_path()
        
        try:
            # Create config directory if it doesn't exist
            os.makedirs(config_dir, exist_ok=True)
            
            # Prepare config data
            config = {
                'open_dir_after_split': self.open_dir_after_split.get(),
                'create_log': self.create_log.get(),
                'retain_header': self.retain_header.get()
            }
            
            # Save to file
            with open(config_file, 'w', encoding='utf-8') as f:
                json.dump(config, f, indent=2)
                
            print(f"Configuration saved to: {config_file}")
            
        except Exception as e:
            print(f"Error saving config: {e}")

    def on_setting_change(self, *args):
        """Called whenever a setting changes - saves config automatically"""
        self.save_config()

    def setup_styles(self):
        """Configure clean styling for the application"""
        style = ttk.Style()
        
        # Configure frame title styling
        style.configure("Bold.TLabelframe.Label", 
                       font=("Segoe UI", 9, "bold"))
        
        # Configure stats styling
        style.configure("Stats.TLabel", 
                       font=("Segoe UI", 9),
                       foreground="#34495e")
        style.configure("StatsValue.TLabel", 
                       font=("Segoe UI", 10, "bold"),
                       foreground="#27ae60",
                       background="#ecf0f1",
                       relief="flat",
                       borderwidth=1)
        style.configure("StatsAnalyzing.TLabel", 
                       font=("Segoe UI", 10, "bold"),
                       foreground="#3498db",
                       background="#ecf0f1",
                       relief="flat",
                       borderwidth=1)
        style.configure("StatsFrame.TFrame",
                       background="#f8f9fa",
                       relief="solid",
                       borderwidth=1)
        style.configure("ProgressSuccess.TLabel",
                       font=("Segoe UI", 10, "bold"),
                       foreground="#27ae60")
        style.configure("ProgressFail.TLabel",
                       font=("Segoe UI", 10, "bold"),
                       foreground="#e74c3c")

    def create_menu(self):
        menubar = Menu(self.root)

        # File menu
        file_menu = Menu(menubar, tearoff=0)
        file_menu.add_command(label="Clear Inputs", command=self.reset_stats_and_progress, accelerator="Ctrl+R")
        file_menu.add_separator()
        file_menu.add_command(label="Exit", command=self.root.quit, accelerator="Ctrl+Q")
        menubar.add_cascade(label="File", menu=file_menu)

        # Settings menu (NEW)
        settings_menu = Menu(menubar, tearoff=0)
        settings_menu.add_checkbutton(label="Open Output Directory", 
                                    variable=self.open_dir_after_split)
        settings_menu.add_checkbutton(label="Enable Validation Log", 
                                    variable=self.create_log)
        settings_menu.add_checkbutton(label="Retain Headers", 
                                    variable=self.retain_header)
        menubar.add_cascade(label="Settings", menu=settings_menu)

        # Help menu
        help_menu = Menu(menubar, tearoff=0)
        help_menu.add_command(label="Documentation", command=self.open_help, accelerator="Ctrl+D")
        menubar.add_cascade(label="Help", menu=help_menu)

        self.root.config(menu=menubar)

    def setup_keyboard_shortcuts(self):
        """Set up keyboard shortcuts"""
        self.root.bind('<Control-q>', lambda e: self.root.quit())
        self.root.bind('<Control-Q>', lambda e: self.root.quit())
        self.root.bind('<Control-r>', lambda e: self.reset_stats_and_progress())
        self.root.bind('<Control-R>', lambda e: self.reset_stats_and_progress())
        self.root.bind('<Control-d>', lambda e: self.open_help())
        self.root.bind('<Control-D>', lambda e: self.open_help())

    def open_help(self):
        webbrowser.open("https://github.com/jackworthen/file-splitter")

    def create_widgets(self):
        main_frame = ttk.Frame(self.root, padding="15")
        main_frame.grid(row=0, column=0, sticky="nsew")

        # File Selection Section
        file_frame = ttk.LabelFrame(main_frame, text="Source File", padding=10, style="Bold.TLabelframe")
        file_frame.grid(row=0, column=0, columnspan=3, pady=(0, 10), sticky="ew")
        
        self.input_file_entry = tk.Entry(file_frame, textvariable=self.input_file, width=50)
        self.input_file_entry.grid(row=0, column=0, padx=(0, 10), pady=5, sticky="ew")
        ttk.Button(file_frame, text="Browse", command=self.select_file).grid(row=0, column=1, pady=5)
        file_frame.columnconfigure(0, weight=1)

        # Output Directory Section
        output_frame = ttk.LabelFrame(main_frame, text="Output Directory", padding=10, style="Bold.TLabelframe")
        output_frame.grid(row=1, column=0, columnspan=3, pady=(0, 10), sticky="ew")
        
        self.output_entry = ttk.Entry(output_frame, textvariable=self.output_dir, width=50)
        self.output_entry.grid(row=0, column=0, padx=(0, 10), pady=5, sticky="ew")
        self.output_browse_button = ttk.Button(output_frame, text="Browse", command=self.select_output_directory, state="disabled")
        self.output_browse_button.grid(row=0, column=1, pady=5)
        
        # REMOVED: The two checkbuttons that were here (Open Directory After Split and Enable Validation Log)
        # They are now in the Settings menu
        
        output_frame.columnconfigure(0, weight=1)

        # Split Settings Section
        settings_frame = ttk.LabelFrame(main_frame, text="Split Settings", padding=10, style="Bold.TLabelframe")
        settings_frame.grid(row=2, column=0, columnspan=3, pady=(0, 10), sticky="ew")
        
        # Column Selection Button - row 0
        button_frame = ttk.Frame(settings_frame)
        button_frame.grid(row=0, column=0, columnspan=2, pady=(0, 10), sticky="w")
        
        self.column_select_button = ttk.Button(button_frame, text="Modify Columns...", 
                                             command=self.open_column_selection, state="disabled")
        self.column_select_button.pack(side="left")
        
        # Split mode selection - moved to row 1
        split_mode_frame = ttk.Frame(settings_frame)
        split_mode_frame.grid(row=1, column=0, columnspan=4, sticky="w", pady=(0, 0))
        
        ttk.Label(split_mode_frame, text="Split Mode:").pack(side="left")
        
        self.split_mode_combo = ttk.Combobox(split_mode_frame, textvariable=self.split_mode, 
                                           values=["Size (MB)", "Rows Per File", "Number of Files"], width=15, state="readonly")
        self.split_mode_combo.pack(side="left", padx=(10, 15))
        
        self.split_value_entry = tk.Entry(split_mode_frame, textvariable=self.split_value, width=10, state="disabled")
        self.split_value_entry.pack(side="left")
        
        # File type selection - moved to row 2
        file_type_frame = ttk.Frame(settings_frame)
        file_type_frame.grid(row=2, column=0, columnspan=2, pady=(10, 0), sticky="w")
        
        ttk.Label(file_type_frame, text="Output file type:").pack(side="left")
        ttk.Combobox(file_type_frame, textvariable=self.file_type, values=[".csv", ".txt", ".dat", ".json"], width=10).pack(side="left", padx=(10, 0))

        # Delimiter settings - moved to row 3
        delimiter_frame = ttk.Frame(settings_frame)
        delimiter_frame.grid(row=3, column=0, columnspan=2, pady=(10, 0), sticky="w")
        
        self.delim_checkbox = ttk.Checkbutton(delimiter_frame, text="Custom Delimiter", 
                                            variable=self.use_custom_delim, command=self.toggle_delim_fields)
        self.delim_checkbox.state(["disabled"])
        self.delim_checkbox.pack(side="left")

        self.delimiter_combo = ttk.Combobox(delimiter_frame, textvariable=self.custom_delimiter, 
                                          width=15, state="disabled")
        self.delimiter_combo['values'] = ('comma (,)', 'tab (\\t)', 'semicolon (;)', 'pipe (|)', 'asterisk (*)')
        self.delimiter_combo.pack(side="left", padx=(10, 0))
        
        # Quote mode settings - row 4
        quote_frame = ttk.Frame(settings_frame)
        quote_frame.grid(row=4, column=0, columnspan=2, pady=(10, 0), sticky="w")
        
        ttk.Label(quote_frame, text="Quoted Identifier Handling:").pack(side="left")
        
        self.quote_combo = ttk.Combobox(quote_frame, textvariable=self.quote_mode, 
                                      values=["Standard", 
                                             "All fields", 
                                             "Never quote"], 
                                      width=25, state="disabled")
        self.quote_combo.pack(side="left", padx=(10, 0))
        
        # Configure column weights to maintain stable layout
        settings_frame.columnconfigure(0, weight=1)
        settings_frame.columnconfigure(1, weight=0)

        # Stats Section
        stats_frame_outer = ttk.LabelFrame(main_frame, text="Statistics", padding=10, style="Bold.TLabelframe")
        stats_frame_outer.grid(row=3, column=0, columnspan=3, pady=(0, 10), sticky="ew")
        
        # Stats display
        stats_frame = ttk.Frame(stats_frame_outer, style="StatsFrame.TFrame", padding=10)
        stats_frame.grid(row=0, column=0, columnspan=2, sticky="ew")
        
        # Create a vertical layout for stats
        stats_container = ttk.Frame(stats_frame)
        stats_container.grid(row=0, column=0, sticky="ew")
        stats_frame.columnconfigure(0, weight=1)
        stats_container.columnconfigure(1, weight=1)
        
        # Total Rows (row=0)
        ttk.Label(stats_container, text="Total Rows:", style="Stats.TLabel").grid(row=0, column=0, sticky="w", padx=(0, 5), pady=(0, 5))
        self.total_rows_label = ttk.Label(stats_container, textvariable=self.total_rows, style="StatsAnalyzing.TLabel", width=15, anchor="w")
        self.total_rows_label.grid(row=0, column=1, sticky="ew", padx=(0, 0), pady=(0, 5))
        
        # Rows Processed (row=1)
        ttk.Label(stats_container, text="Rows Processed:", style="Stats.TLabel").grid(row=1, column=0, sticky="w", padx=(0, 5), pady=(0, 5))
        rows_processed_label = ttk.Label(stats_container, textvariable=self.rows_processed, style="StatsAnalyzing.TLabel", width=15, anchor="w")
        rows_processed_label.grid(row=1, column=1, sticky="ew", pady=(0, 5))
        
        # Current File (row=2)
        ttk.Label(stats_container, text="Current File:", style="Stats.TLabel").grid(row=2, column=0, sticky="w", padx=(0, 5), pady=(0, 5))
        current_file_label = ttk.Label(stats_container, textvariable=self.current_file, style="StatsAnalyzing.TLabel", width=15, anchor="w")
        current_file_label.grid(row=2, column=1, sticky="ew", padx=(0, 0), pady=(0, 5))
        
        # File Count (row=3)
        ttk.Label(stats_container, text="File Count:", style="Stats.TLabel").grid(row=3, column=0, sticky="w", padx=(0, 5), pady=(0, 5))
        file_count_label = ttk.Label(stats_container, textvariable=self.file_count, style="StatsAnalyzing.TLabel", width=15, anchor="w")
        file_count_label.grid(row=3, column=1, sticky="ew", pady=(0, 5))
        
        # Output File Type (row=4)
        ttk.Label(stats_container, text="Output File Type:", style="Stats.TLabel").grid(row=4, column=0, sticky="w", padx=(0, 5))
        output_type_label = ttk.Label(stats_container, textvariable=self.output_file_type, style="StatsAnalyzing.TLabel", width=15, anchor="w")
        output_type_label.grid(row=4, column=1, sticky="ew")
        
        stats_frame_outer.columnconfigure(0, weight=1)

        # Progress Section
        progress_frame = ttk.LabelFrame(main_frame, text="Progress", padding=10, style="Bold.TLabelframe")
        progress_frame.grid(row=4, column=0, columnspan=3, pady=(0, 10), sticky="ew")
        
        # Progress bar with percentage
        self.progress = ttk.Progressbar(progress_frame, mode='determinate')
        self.progress.grid(row=0, column=0, sticky="ew", padx=(0, 10), pady=(0, 10))
        
        # Progress percentage label
        self.progress_label = ttk.Label(progress_frame, textvariable=self.progress_percentage, width=10, anchor="center")
        self.progress_label.grid(row=0, column=1, pady=(0, 10), sticky="ew")
        
        # Configure column weights
        progress_frame.columnconfigure(0, weight=1)
        progress_frame.columnconfigure(1, weight=0, minsize=80)

        # Control Buttons
        button_frame = ttk.Frame(main_frame)
        button_frame.grid(row=5, column=0, columnspan=3, pady=(0, 10))
        
        self.button_start = ttk.Button(button_frame, text="Run", command=self.start_threaded_split)
        self.button_start.grid(row=0, column=0, padx=(0, 10))
        
        self.button_cancel = ttk.Button(button_frame, text="Cancel", command=self.cancel_operation, state="disabled")
        self.button_cancel.grid(row=0, column=1, padx=(0, 10))
        
        self.button_reset = ttk.Button(button_frame, text="Reset", command=self.reset_stats_and_progress, state="disabled")
        self.button_reset.grid(row=0, column=2, padx=(0, 10))
        
        self.button_exit = ttk.Button(button_frame, text="Exit", command=self.root.quit)
        self.button_exit.grid(row=0, column=3)

        main_frame.columnconfigure(0, weight=1)
        
        # Initialize delimiter fields to hidden state
        self.toggle_delim_fields()

    def is_supported_input_file_type(self, file_path):
        """Check if the input file type is supported for reading"""
        if not file_path:
            return False
        
        # Get file extension in lowercase
        _, ext = os.path.splitext(file_path.lower())
        
        # Supported input file types
        supported_extensions = {'.csv', '.tsv', '.txt', '.dat', '.json'}
        
        return ext in supported_extensions

    def select_file(self):
        path = filedialog.askopenfilename(
            title="Select File to Split",
            filetypes=[("CSV files", "*.csv"), ("TSV files", "*.tsv"), ("DAT files", "*.dat"), 
                      ("TXT files", "*.txt"), ("JSON files", "*.json"), ("All files", "*.*")]
        )
        if path:
            # Check if the selected file type is supported
            if not self.is_supported_input_file_type(path):
                _, ext = os.path.splitext(path)
                messagebox.showwarning(
                    "Unsupported File Type", 
                    f"The selected file type '{ext}' is not supported as an input file.\n\n"
                    f"Supported input file types are:\n"
                    f"• CSV files (.csv)\n"
                    f"• TSV files (.tsv)\n"
                    f"• Text files (.txt)\n"
                    f"• Data files (.dat)\n"
                    f"• JSON files (.json)\n\n"
                    f"Please select a file with a supported format."
                )
                return
            
            default_out = os.path.join(os.path.dirname(path), 'split_files')
            self.output_dir.set(default_out.replace('\\', '/'))
            self.input_file.set(path)
            self.delim_checkbox.state(["!disabled"])
            
            # Load column headers
            self.load_column_headers()
            
            # Only try to detect delimiter for non-JSON files
            _, ext = os.path.splitext(path.lower())
            if ext != '.json':
                try:
                    with open(path, 'r', encoding='utf-8') as f:
                        sample = f.read(2048)
                        sniffer = csv.Sniffer()
                        dialect = sniffer.sniff(sample)
                        self.detected_delimiter.set(dialect.delimiter)
                except Exception as e:
                    self.detected_delimiter.set(',')
                    print(f"Could not detect delimiter: {e}")
            else:
                self.detected_delimiter.set(',')  # Default delimiter for JSON conversion
                
            if self.use_custom_delim.get():
                self.toggle_delim_fields()

    def load_column_headers(self):
        """Load column headers from the selected file"""
        if not self.input_file.get():
            return
            
        try:
            _, ext = os.path.splitext(self.input_file.get().lower())
            
            if ext == '.json':
                # Handle JSON files
                with open(self.input_file.get(), 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    
                # Handle different JSON structures
                if isinstance(data, list) and data:
                    # Array of objects - most common case
                    ordered_keys = []
                    seen_keys = set()
                    
                    # Get keys from first object to establish order
                    if isinstance(data[0], dict):
                        first_obj_keys = self.flatten_json_keys(data[0])
                        for key in first_obj_keys:
                            if key not in seen_keys:
                                ordered_keys.append(key)
                                seen_keys.add(key)
                    
                    # Collect any additional keys from remaining objects (append to end)
                    for item in data[1:101]:  # Sample up to 100 more items for performance
                        if isinstance(item, dict):
                            item_keys = self.flatten_json_keys(item)
                            for key in item_keys:
                                if key not in seen_keys:
                                    ordered_keys.append(key)
                                    seen_keys.add(key)
                    
                    self.available_columns = ordered_keys
                    self.selected_columns = self.available_columns.copy()
                    
                elif isinstance(data, dict):
                    # Single object - treat keys as columns
                    all_keys = self.flatten_json_keys(data)
                    self.available_columns = all_keys  # No need to sort, already in order
                    self.selected_columns = self.available_columns.copy()
                else:
                    # Unsupported JSON structure
                    self.available_columns = []
                    self.selected_columns = []
                    
            else:
                # Handle CSV/TXT/DAT files
                with open(self.input_file.get(), 'r', encoding='utf-8') as f:
                    sample = f.read(2048)
                    f.seek(0)
                    
                    # Detect delimiter
                    sniffer = csv.Sniffer()
                    try:
                        dialect = sniffer.sniff(sample)
                        delimiter = dialect.delimiter
                    except:
                        delimiter = ','
                    
                    # Read header row
                    reader = csv.reader(f, delimiter=delimiter)
                    header = next(reader)
                    
                    self.available_columns = header
                    self.selected_columns = header.copy()  # By default, include all columns
                
        except Exception as e:
            print(f"Error loading column headers: {e}")
            self.available_columns = []
            self.selected_columns = []

    def flatten_json_keys(self, obj, parent_key='', sep='.'):
        """Flatten nested JSON object keys with dot notation, preserving order"""
        keys = []  # Use list to preserve order
        
        if isinstance(obj, dict):
            for key, value in obj.items():  # dict.items() preserves insertion order in Python 3.7+
                new_key = f"{parent_key}{sep}{key}" if parent_key else key
                keys.append(new_key)
                
                # Recursively flatten nested objects
                if isinstance(value, dict):
                    keys.extend(self.flatten_json_keys(value, new_key, sep))
                elif isinstance(value, list) and value and isinstance(value[0], dict):
                    # Handle arrays of objects by flattening the first object
                    keys.extend(self.flatten_json_keys(value[0], new_key, sep))
        
        return keys

    def flatten_json_object(self, obj, parent_key='', sep='.'):
        """Flatten a nested JSON object into a flat dictionary"""
        flattened = {}
        
        if isinstance(obj, dict):
            for key, value in obj.items():
                new_key = f"{parent_key}{sep}{key}" if parent_key else key
                
                if isinstance(value, dict):
                    flattened.update(self.flatten_json_object(value, new_key, sep))
                elif isinstance(value, list):
                    # Convert lists to string representation
                    flattened[new_key] = json.dumps(value) if value else ''
                else:
                    flattened[new_key] = str(value) if value is not None else ''
        else:
            flattened[parent_key] = str(obj) if obj is not None else ''
        
        return flattened

    def open_column_selection(self):
        """Open the column selection window"""
        if not self.available_columns:
            messagebox.showwarning("Warning", "No columns found in the selected file.")
            return
            
        dialog = ColumnSelectionWindow(self.root, self.available_columns, self.selected_columns, self.column_renames)
        self.root.wait_window(dialog.window)
        
        if dialog.result is not None:
            self.selected_columns = dialog.result
            self.column_renames = dialog.result_renames

    def get_output_column_names(self, original_columns):
        """Get the output column names (renamed if applicable) for the given original columns"""
        return [self.column_renames.get(col, col) for col in original_columns]

    def select_output_directory(self):
        path = filedialog.askdirectory(title="Select Output Directory")
        if path:
            self.output_dir.set(path)

    def get_split_mode_value(self):
        """Get the actual mode value for processing"""
        if self.split_mode.get() == "Size (MB)":
            return "size"
        elif self.split_mode.get() == "Rows Per File":
            return "rows"
        else:  # "Number of Files"
            return "files"

    def on_file_type_change(self, *args):
        """Handle file type changes to enable/disable delimiter and header options"""
        if self.file_type.get() == ".json":
            # Output is JSON - disable delimiter options (JSON doesn't use delimiters)
            self.use_custom_delim.set(False)
            self.delim_checkbox.state(["disabled"])
            self.toggle_delim_fields()
        else:
            # Output is not JSON - enable delimiter options if file is selected
            if self.input_file.get():
                # Enable delimiter options for delimited output formats (CSV, TXT, DAT)
                # regardless of input format (CSV, TXT, DAT, or JSON)
                self.delim_checkbox.state(["!disabled"])
            # If no file selected, keep everything disabled
        
        # Update quote mode state whenever file type changes
        self.update_quote_mode_state()

    def highlight_field_error(self, field_widget):
        """Highlight a field with light red background to indicate error"""
        field_widget.configure(bg="#ffcccc")  # Light red background
    
    def clear_field_error(self, field_widget):
        """Remove error highlighting from a field"""
        field_widget.configure(bg="white")  # Reset to white background
    
    def on_split_value_change(self, *args):
        """Handle changes to split value to clear error highlighting"""
        if self.split_value.get().strip():
            try:
                value = int(self.split_value.get())
                if value > 0:
                    self.clear_field_error(self.split_value_entry)
            except ValueError:
                pass  # Keep highlighting if still invalid

    def get_quote_mode(self):
        """Convert descriptive quote mode to csv module constant"""
        import csv
        mode_map = {
            "Standard": csv.QUOTE_MINIMAL,
            "All fields": csv.QUOTE_ALL,
            "Never quote": csv.QUOTE_NONE
        }
        return mode_map.get(self.quote_mode.get(), csv.QUOTE_MINIMAL)

    def get_delimiter_symbol(self, delimiter_text):
        """Extract the actual delimiter symbol from descriptive text"""
        if not delimiter_text:
            return ','
        
        # Extract symbol from parentheses
        if '(' in delimiter_text and ')' in delimiter_text:
            start = delimiter_text.find('(') + 1
            end = delimiter_text.find(')')
            symbol = delimiter_text[start:end]
            # Handle special case for tab
            if symbol == '\\t':
                return '\t'
            return symbol
        
        # Fallback - if it's just a symbol already
        return delimiter_text

    def toggle_delim_fields(self):
        """Enable/disable the delimiter combobox and filter out detected delimiter"""
        # Enable/disable the delimiter combobox - only relevant for delimited output formats
        if (self.use_custom_delim.get() and 
            self.input_file.get() and 
            self.file_type.get() != ".json"):  # Only check output format
            self.delimiter_combo.config(state="readonly")
            
            # Only filter out detected delimiter for delimited input files (not JSON)
            _, input_ext = os.path.splitext(self.input_file.get().lower())
            is_json_input = input_ext == '.json'
            
            # All available options
            all_options = ['comma (,)', 'tab (\\t)', 'semicolon (;)', 'pipe (|)', 'asterisk (*)']
            
            if not is_json_input:
                # For delimited input files, filter out the detected delimiter
                detected = self.detected_delimiter.get()
                
                # Map detected symbol to descriptive text
                delimiter_map = {
                    ',': 'comma (,)',
                    '\t': 'tab (\\t)',
                    ';': 'semicolon (;)',
                    '|': 'pipe (|)',
                    '*': 'asterisk (*)'
                }
                
                # Remove the detected delimiter from options
                detected_option = delimiter_map.get(detected, None)
                if detected_option and detected_option in all_options:
                    filtered_options = [opt for opt in all_options if opt != detected_option]
                else:
                    filtered_options = all_options
            else:
                # For JSON input files, show all delimiter options (no filtering needed)
                filtered_options = all_options
                
            # Update combo box values
            self.delimiter_combo['values'] = filtered_options
            
            # Clear current selection since we're showing new options
            self.custom_delimiter.set('')
            
        else:
            self.delimiter_combo.config(state="disabled")
            # Reset to all options when disabled
            self.delimiter_combo['values'] = ['comma (,)', 'tab (\\t)', 'semicolon (;)', 'pipe (|)', 'asterisk (*)']
    
    def update_quote_mode_state(self):
        """Enable/disable quote mode dropdown based on file selection and output format"""
        if (self.input_file.get() and self.file_type.get() != ".json"):
            self.quote_combo.config(state="readonly")
        else:
            self.quote_combo.config(state="disabled")

    def start_threaded_split(self):
        file_path = self.input_file.get()
        extension = self.file_type.get().strip().lower()
        out_dir = self.output_dir.get()
        mode = self.get_split_mode_value()

        if not file_path:
            self.highlight_field_error(self.input_file_entry)
            messagebox.showwarning("Warning", "Please select a file to split.")
            return

        # NEW: Validate input file type before proceeding
        if not self.is_supported_input_file_type(file_path):
            _, ext = os.path.splitext(file_path)
            self.highlight_field_error(self.input_file_entry)
            messagebox.showwarning(
                "Unsupported Input File Type", 
                f"The input file type '{ext}' is not supported for reading.\n\n"
                f"Supported input file types are:\n"
                f"• CSV files (.csv)\n"
                f"• TSV files (.tsv)\n"
                f"• Text files (.txt)\n"
                f"• Data files (.dat)\n"
                f"• JSON files (.json)\n\n"
                f"Please select a file with a supported format."
            )
            return

        try:
            value = int(self.split_value.get())
            if value <= 0:
                raise ValueError
        except ValueError:
            self.highlight_field_error(self.split_value_entry)
            messagebox.showwarning("Warning", "Please enter a valid positive number for the split value.")
            return

        if not out_dir:
            out_dir = os.path.join(os.path.dirname(file_path), "split_files")

        # Reset progress tracking
        self.cancel_event.clear()
        self.is_running = True
        self.start_time = time.time()
        
        # Reset validation tracking
        self.input_row_count = 0
        self.output_row_count = 0
        self.current_part_num = 0
        
        # Update UI state
        self.button_start.config(state=tk.DISABLED)
        self.button_cancel.config(state=tk.NORMAL)
        self.progress['value'] = 0
        self.progress_percentage.set("0%")
        self.progress_label.configure(style="TLabel")
        self.total_rows.set("")
        self.current_file.set("Initializing...")
        self.rows_processed.set("0")
        self.file_count.set("0")
        self.output_file_type.set(extension.upper())
        
        # Show percentage label
        self.progress_label.grid()

        delim = self.get_delimiter_symbol(self.custom_delimiter.get()) if self.use_custom_delim.get() else self.detected_delimiter.get() or ','
        quote_mode = self.get_quote_mode()  # Get the selected quote mode
        thread = threading.Thread(target=self.split_file, 
                                args=(file_path, out_dir, mode, value, extension, delim, quote_mode))
        thread.daemon = True
        thread.start()

    def cancel_operation(self):
        if self.is_running:
            self.cancel_event.set()
            self.current_file.set("Cancelling...")
            self.button_cancel.config(state=tk.DISABLED)

    def update_progress(self, current_row, total_rows, current_filename, part_num=1):
        """Update progress from worker thread"""
        if total_rows > 0:
            percentage = min(100, (current_row / total_rows) * 100)
            
            # Schedule UI updates
            self.root.after(0, lambda: self.progress.configure(value=percentage))
            self.root.after(0, lambda: self.progress_percentage.set(f"{percentage:.1f}%"))
            self.root.after(0, lambda: self.current_file.set(os.path.basename(current_filename)))
            self.root.after(0, lambda: self.rows_processed.set(f"{current_row:,}"))
            self.root.after(0, lambda: self.file_count.set(str(part_num)))

    def split_file(self, input_file, output_dir, mode, size_or_rows, file_extension, custom_delimiter, quote_mode):
        cancelled = False
        analysis_rows_counted = 0
        part_num = 1
        base_filename = os.path.splitext(os.path.basename(input_file))[0]
        input_data_row_count = 0
        output_data_row_count = 0
        per_file_row_counts = []
        
        try:
            os.makedirs(output_dir, exist_ok=True)
            
            # Detect input file type
            _, input_ext = os.path.splitext(input_file.lower())
            is_json_input = input_ext == '.json'
            
            # First pass: count total rows for progress tracking
            self.root.after(0, lambda: self.total_rows.set("Analyzing file..."))
            total_rows = 0
            
            if is_json_input:
                # Handle JSON input
                with open(input_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    
                if isinstance(data, list):
                    total_rows = len(data)
                    # Get all possible column keys in order (same logic as load_column_headers)
                    ordered_keys = []
                    seen_keys = set()
                    
                    # Get keys from first object to establish order
                    if data and isinstance(data[0], dict):
                        first_obj_keys = self.flatten_json_keys(data[0])
                        for key in first_obj_keys:
                            if key not in seen_keys:
                                ordered_keys.append(key)
                                seen_keys.add(key)
                    
                    # Collect any additional keys from remaining objects
                    for item in data[1:101]:  # Sample up to 100 more items
                        if isinstance(item, dict):
                            item_keys = self.flatten_json_keys(item)
                            for key in item_keys:
                                if key not in seen_keys:
                                    ordered_keys.append(key)
                                    seen_keys.add(key)
                    
                    header = ordered_keys
                elif isinstance(data, dict):
                    total_rows = 1
                    header = self.flatten_json_keys(data)  # Already in order
                else:
                    raise ValueError("Unsupported JSON structure. Expected array of objects or single object.")
                    
                # Filter header to only include selected columns, preserving order
                if self.selected_columns:
                    filtered_header = [col for col in header if col in self.selected_columns]
                    # Apply column renames to the filtered header for output
                    output_header = self.get_output_column_names(filtered_header)
                else:
                    filtered_header = header
                    output_header = self.get_output_column_names(filtered_header)
                    
            else:
                # Handle CSV/TXT/DAT input
                with open(input_file, 'r', newline='', encoding='utf-8') as infile:
                    detected_delimiter = self.detected_delimiter.get() or ','
                    reader = csv.reader(infile, delimiter=detected_delimiter)
                    header = next(reader)  # Read and store header
                    
                    # Filter header to only include selected columns
                    if self.selected_columns:
                        header_indices = [i for i, col in enumerate(header) if col in self.selected_columns]
                        filtered_header = [header[i] for i in header_indices]
                        # Apply column renames to the filtered header for output
                        output_header = self.get_output_column_names(filtered_header)
                    else:
                        header_indices = list(range(len(header)))
                        filtered_header = header
                        output_header = self.get_output_column_names(filtered_header)
                    
                    # Count only data rows (excluding header)
                    for _ in reader:
                        if self.cancel_event.is_set():
                            cancelled = True
                            analysis_rows_counted = total_rows
                            break
                        total_rows += 1
                        if total_rows % 1000 == 0:
                            self.root.after(0, lambda r=total_rows: self.total_rows.set(f"Analyzing... {r:,} rows"))

            if self.cancel_event.is_set() and not cancelled:
                cancelled = True
                analysis_rows_counted = total_rows

            # Update total rows display
            self.root.after(0, lambda: self.total_rows.set(f"{total_rows:,}"))

            # If cancelled during analysis, still write log
            if cancelled:
                self.write_cancellation_log(input_file, output_dir, file_extension, custom_delimiter, 
                                           analysis_rows_counted, 0, [], "during analysis", part_num)
                self.root.after(0, lambda: self.show_cancelled())
                return

            # NEW: Handle "Number of Files" mode
            if mode == "files":
                # Calculate rows per file for even distribution
                num_files = size_or_rows
                if num_files > total_rows:
                    # If requesting more files than rows, limit to one row per file
                    num_files = total_rows
                    messagebox.showinfo("Info", f"Requested {size_or_rows} files, but only {total_rows} rows available. Creating {num_files} files instead.")
                
                # Calculate rows per file (using ceiling to ensure all rows are included)
                max_rows = math.ceil(total_rows / num_files)
                # Switch to rows mode for the actual splitting
                mode = "rows"
                size_or_rows = max_rows

            # Second pass: actual splitting with progress tracking and column filtering
            max_size_bytes = size_or_rows * 1024 * 1024 if mode == "size" else None
            max_rows = size_or_rows if mode == "rows" else None
            is_json_format = file_extension == ".json"
            include_header = self.retain_header.get()  # NEW: Get header retention setting

            if is_json_input:
                # Process JSON input data
                with open(input_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    
                if isinstance(data, list):
                    json_rows = data
                elif isinstance(data, dict):
                    json_rows = [data]
                else:
                    json_rows = []
                    
                processed_rows = 0
                output_path = os.path.join(output_dir, f"{base_filename}_{part_num}{file_extension}")
                
                if is_json_format:
                    # JSON to JSON splitting
                    current_json_data = []
                    current_rows = 0
                    estimated_size = 2  # Start with "[]"
                    avg_row_size = 0
                else:
                    # JSON to CSV/TXT/DAT conversion
                    outfile = open(output_path, 'w', newline='', encoding='utf-8')
                    writer = csv.writer(outfile, delimiter=custom_delimiter, quoting=quote_mode)
                    if include_header:
                        writer.writerow(output_header)
                    current_size = outfile.tell()
                    current_rows = 0

                # Process JSON data rows
                for json_row in json_rows:
                    if self.cancel_event.is_set():
                        cancelled = True
                        if not is_json_format:
                            outfile.close()
                        # Write partial file counts for logging
                        if current_rows > 0:
                            if is_json_format and current_json_data:
                                with open(output_path, 'w', encoding='utf-8') as json_file:
                                    json.dump(current_json_data, json_file, separators=(',', ':'))
                            per_file_row_counts.append(current_rows)
                            output_data_row_count += current_rows
                        break

                    input_data_row_count += 1
                    processed_rows += 1
                    
                    # Convert JSON object to flat row
                    if isinstance(json_row, dict):
                        flattened_row = self.flatten_json_object(json_row)
                        # Create filtered row based on selected columns
                        filtered_row = [flattened_row.get(col, '') for col in filtered_header]
                    else:
                        # Handle non-dict items
                        filtered_row = [str(json_row)]
                    
                    # Update progress every 100 rows
                    if processed_rows % 100 == 0:
                        self.update_progress(processed_rows, total_rows, output_path, part_num)
                    
                    if is_json_format:
                        # JSON to JSON - recreate object with selected columns only using renamed headers
                        if isinstance(json_row, dict):
                            filtered_obj = {}
                            for i, col in enumerate(filtered_header):
                                output_name = output_header[i]
                                filtered_obj[output_name] = flattened_row.get(col, '')
                        else:
                            filtered_obj = json_row
                            
                        current_json_data.append(filtered_obj)
                        current_rows += 1
                        
                        # Size estimation for JSON
                        if mode == "size":
                            if current_rows <= 10:
                                row_json_size = len(json.dumps(filtered_obj, separators=(',', ':')))
                                estimated_size += row_json_size + (1 if current_rows > 1 else 0)
                                avg_row_size = estimated_size / current_rows if current_rows > 0 else 0
                            else:
                                estimated_size += avg_row_size + 1
                        
                        # Check if we need to split
                        split_needed = False
                        if mode == "size":
                            split_needed = estimated_size >= max_size_bytes
                        else:
                            split_needed = current_rows >= max_rows
                            
                        if split_needed:
                            with open(output_path, 'w', encoding='utf-8') as json_file:
                                json.dump(current_json_data, json_file, separators=(',', ':'))
                            
                            per_file_row_counts.append(current_rows)
                            output_data_row_count += current_rows
                            part_num += 1
                            output_path = os.path.join(output_dir, f"{base_filename}_{part_num}{file_extension}")
                            current_json_data = []
                            current_rows = 0
                            estimated_size = 2
                    else:
                        # JSON to CSV/TXT/DAT conversion
                        # Check if we need to split before writing this row
                        outfile.flush()
                        if (
                            (mode == "size" and current_size >= max_size_bytes) or
                            (mode == "rows" and current_rows >= max_rows)
                        ):
                            outfile.close()
                            per_file_row_counts.append(current_rows)
                            output_data_row_count += current_rows
                            part_num += 1
                            output_path = os.path.join(output_dir, f"{base_filename}_{part_num}{file_extension}")
                            outfile = open(output_path, 'w', newline='', encoding='utf-8')
                            writer = csv.writer(outfile, delimiter=custom_delimiter, quoting=quote_mode)
                            if include_header:
                                writer.writerow(output_header)
                            current_size = outfile.tell()
                            current_rows = 0

                        # Write the converted row
                        writer.writerow(filtered_row)
                        current_size = outfile.tell()
                        current_rows += 1

                # Handle the last file for JSON input
                if cancelled:
                    self.write_cancellation_log(input_file, output_dir, file_extension, custom_delimiter, 
                                               input_data_row_count, output_data_row_count, per_file_row_counts, 
                                               "during file splitting", part_num)
                    self.root.after(0, lambda: self.show_cancelled())
                    return

                if is_json_format:
                    if current_json_data:
                        with open(output_path, 'w', encoding='utf-8') as json_file:
                            json.dump(current_json_data, json_file, separators=(',', ':'))
                        per_file_row_counts.append(current_rows)
                        output_data_row_count += current_rows
                else:
                    outfile.close()
                    per_file_row_counts.append(current_rows)
                    output_data_row_count += current_rows
                    
            else:
                # Handle CSV/TXT/DAT input (existing logic)
                with open(input_file, 'r', newline='', encoding='utf-8') as infile:
                    detected_delimiter = self.detected_delimiter.get() or ','
                    reader = csv.reader(infile, delimiter=detected_delimiter)
                    header = next(reader)  # Read and consume header row
                    
                    # Filter header to only include selected columns
                    if self.selected_columns:
                        header_indices = [i for i, col in enumerate(header) if col in self.selected_columns]
                        filtered_header = [header[i] for i in header_indices]
                        # Apply column renames to the filtered header for output
                        output_header = self.get_output_column_names(filtered_header)
                    else:
                        header_indices = list(range(len(header)))
                        filtered_header = header
                        output_header = self.get_output_column_names(filtered_header)

                    processed_rows = 0
                    output_path = os.path.join(output_dir, f"{base_filename}_{part_num}{file_extension}")
                    
                    if is_json_format:
                        # CSV to JSON conversion
                        current_json_data = []
                        current_rows = 0
                        estimated_size = 2  # Start with "[]" 
                        avg_row_size = 0  # Track average row size for better estimation
                    else:
                        # CSV to CSV/TXT/DAT
                        outfile = open(output_path, 'w', newline='', encoding='utf-8')
                        writer = csv.writer(outfile, delimiter=custom_delimiter, quoting=quote_mode)
                        if include_header:  # NEW: Conditionally write header
                            writer.writerow(output_header)  # Write renamed header
                        current_size = outfile.tell()
                        current_rows = 0

                    # Process all data rows (header was already consumed by next(reader))
                    for row in reader:
                        if self.cancel_event.is_set():
                            cancelled = True
                            if not is_json_format:
                                outfile.close()
                            # Write partial file counts for logging
                            if current_rows > 0:
                                if is_json_format and current_json_data:
                                    # Write remaining JSON data before cancelling
                                    with open(output_path, 'w', encoding='utf-8') as json_file:
                                        json.dump(current_json_data, json_file, separators=(',', ':'))
                                per_file_row_counts.append(current_rows)
                                output_data_row_count += current_rows
                            break

                        # Count this as a data row (not header)
                        input_data_row_count += 1
                        processed_rows += 1
                        
                        # Filter row to only include selected columns
                        filtered_row = [row[i] if i < len(row) else '' for i in header_indices]
                        
                        # Update progress every 100 rows
                        if processed_rows % 100 == 0:
                            self.update_progress(processed_rows, total_rows, output_path, part_num)
                        
                        if is_json_format:
                            # Convert row to JSON object using renamed header and row
                            row_dict = dict(zip(output_header, filtered_row))
                            current_json_data.append(row_dict)
                            current_rows += 1
                            
                            # Efficient size estimation for JSON
                            if mode == "size":
                                if current_rows <= 10:
                                    # For first 10 rows, calculate actual size to get better average
                                    row_json_size = len(json.dumps(row_dict, separators=(',', ':')))
                                    estimated_size += row_json_size + (1 if current_rows > 1 else 0)  # +1 for comma
                                    avg_row_size = estimated_size / current_rows if current_rows > 0 else 0
                                else:
                                    # Use average size estimation for subsequent rows
                                    estimated_size += avg_row_size + 1  # +1 for comma
                            
                            # Check if we need to split
                            split_needed = False
                            if mode == "size":
                                split_needed = estimated_size >= max_size_bytes
                            else:  # mode == "rows"
                                split_needed = current_rows >= max_rows
                                
                            if split_needed:
                                # Write JSON file (compact format for better performance)
                                with open(output_path, 'w', encoding='utf-8') as json_file:
                                    json.dump(current_json_data, json_file, separators=(',', ':'))
                                
                                per_file_row_counts.append(current_rows)
                                output_data_row_count += current_rows
                                part_num += 1
                                output_path = os.path.join(output_dir, f"{base_filename}_{part_num}{file_extension}")
                                current_json_data = []
                                current_rows = 0
                                estimated_size = 2  # Reset to "[]"
                        else:
                            # Check if we need to split before writing this row
                            outfile.flush()
                            if (
                                (mode == "size" and current_size >= max_size_bytes) or
                                (mode == "rows" and current_rows >= max_rows)
                            ):
                                outfile.close()
                                per_file_row_counts.append(current_rows)
                                output_data_row_count += current_rows
                                part_num += 1
                                output_path = os.path.join(output_dir, f"{base_filename}_{part_num}{file_extension}")
                                outfile = open(output_path, 'w', newline='', encoding='utf-8')
                                writer = csv.writer(outfile, delimiter=custom_delimiter, quoting=quote_mode)
                                if include_header:  # NEW: Conditionally write header for new files
                                    writer.writerow(output_header)  # Write renamed header
                                current_size = outfile.tell()
                                current_rows = 0

                            # Write the current data row
                            writer.writerow(filtered_row)  # Write filtered row
                            current_size = outfile.tell()
                            current_rows += 1

                    # If cancelled during splitting, write cancellation log
                    if cancelled:
                        self.write_cancellation_log(input_file, output_dir, file_extension, custom_delimiter, 
                                                   input_data_row_count, output_data_row_count, per_file_row_counts, 
                                                   "during file splitting", part_num)
                        self.root.after(0, lambda: self.show_cancelled())
                        return

                    # Handle the last file (normal completion)
                    if is_json_format:
                        if current_json_data:  # Write remaining data
                            with open(output_path, 'w', encoding='utf-8') as json_file:
                                json.dump(current_json_data, json_file, separators=(',', ':'))
                            per_file_row_counts.append(current_rows)
                            output_data_row_count += current_rows
                    else:
                        outfile.close()
                        per_file_row_counts.append(current_rows)
                        output_data_row_count += current_rows

            # Store row counts for validation
            self.input_row_count = input_data_row_count
            self.output_row_count = output_data_row_count

            # Final progress update
            self.update_progress(total_rows, total_rows, output_path, part_num)

            # Create log file for successful completion
            if self.create_log.get():
                self.write_completion_log(input_file, output_dir, file_extension, custom_delimiter,
                                        input_data_row_count, output_data_row_count, per_file_row_counts, part_num)
            
            self.root.after(0, lambda: self.show_success(part_num, output_dir))
            
        except Exception as e:
            self.root.after(0, lambda: messagebox.showerror("Error", f"An error occurred: {e}"))
        finally:
            self.root.after(0, self.reset_ui)

    def write_cancellation_log(self, input_file, output_dir, file_extension, custom_delimiter, 
                              input_rows, output_rows, per_file_row_counts, cancel_phase, parts_created):
        """Write log entry for cancelled operations"""
        if not self.create_log.get():
            return
            
        log_path = os.path.join(output_dir, "log.txt")
        timestamp = time.strftime("%Y-%m-%d %H:%M:%S")
        input_file_size = os.path.getsize(input_file)
        base_filename = os.path.splitext(os.path.basename(input_file))[0]

        with open(log_path, 'a', encoding='utf-8') as log_file:
            log_file.write(f"\n")
            log_file.write(f"File Splitter Log - CANCELLED\n")
            log_file.write(f"Timestamp: {timestamp}\n")
            log_file.write(f"Input File: {input_file}\n")
            log_file.write(f"Input File Size: {input_file_size:,} bytes\n")
            log_file.write(f"Operation cancelled {cancel_phase}\n")
            log_file.write(f"Total Data Rows Processed: {input_rows:,}\n")
            log_file.write(f"Partial Files Created: {len(per_file_row_counts)}\n")
            log_file.write(f"Output Format: {file_extension}\n")
            if file_extension != ".json":
                log_file.write(f"Delimiter Used: '{custom_delimiter}'\n")
                log_file.write(f"Quote Mode: {self.quote_mode.get()}\n")
                log_file.write(f"Header Row Included: {'Yes' if self.retain_header.get() else 'No'}\n")  # NEW
            
            # Log column filtering information
            if len(self.selected_columns) < len(self.available_columns):
                excluded_columns = [col for col in self.available_columns if col not in self.selected_columns]
                log_file.write(f"Columns Included: {len(self.selected_columns)} of {len(self.available_columns)}\n")
                log_file.write(f"Included Columns: {', '.join(self.selected_columns)}\n")
                log_file.write(f"Excluded Columns: {', '.join(excluded_columns)}\n")
            else:
                log_file.write(f"All Columns Included: {len(self.available_columns)}\n")
            log_file.write(f"\n")

            # Log any partial files that were created
            for i, row_count in enumerate(per_file_row_counts):
                part_filename = os.path.join(output_dir, f"{base_filename}_{i+1}{file_extension}")
                if os.path.exists(part_filename):
                    part_size = os.path.getsize(part_filename)
                    log_file.write(f"Partial File {i+1}: {row_count} data rows, {part_size:,} bytes\n")

            log_file.write(f"\nTotal Data Rows in Partial Files: {output_rows:,}\n")
            log_file.write("Validation: FAIL ❌ (Operation Cancelled)\n")
            log_file.write(f"\n============================================================\n")

    def write_completion_log(self, input_file, output_dir, file_extension, custom_delimiter,
                           input_data_row_count, output_data_row_count, per_file_row_counts, part_num):
        """Write log entry for successful completion"""
        log_path = os.path.join(output_dir, "log.txt")
        timestamp = time.strftime("%Y-%m-%d %H:%M:%S")
        input_file_size = os.path.getsize(input_file)
        base_filename = os.path.splitext(os.path.basename(input_file))[0]

        with open(log_path, 'a', encoding='utf-8') as log_file:
            log_file.write(f"\n")
            log_file.write(f"File Splitter Log\n")
            log_file.write(f"Timestamp: {timestamp}\n")
            log_file.write(f"Input File: {input_file}\n")
            log_file.write(f"Input File Size: {input_file_size:,} bytes\n")
            log_file.write(f"Total Data Rows in Input File: {input_data_row_count:,}\n")
            log_file.write(f"Total Files Created: {len(per_file_row_counts)}\n")  # FIXED: Use actual count
            log_file.write(f"Output Format: {file_extension}\n")
            if file_extension != ".json":
                log_file.write(f"Delimiter Used: '{custom_delimiter}'\n")
                log_file.write(f"Quote Mode: {self.quote_mode.get()}\n")
                log_file.write(f"Header Row Included: {'Yes' if self.retain_header.get() else 'No'}\n")  # NEW
            
            # Log column filtering information
            if len(self.selected_columns) < len(self.available_columns):
                excluded_columns = [col for col in self.available_columns if col not in self.selected_columns]
                log_file.write(f"Columns Included: {len(self.selected_columns)} of {len(self.available_columns)}\n")
                log_file.write(f"Included Columns: {', '.join(self.selected_columns)}\n")
                log_file.write(f"Excluded Columns: {', '.join(excluded_columns)}\n")
            else:
                log_file.write(f"All Columns Included: {len(self.available_columns)}\n")
            log_file.write(f"\n")

            # FIXED: Use len(per_file_row_counts) instead of part_num
            for i in range(len(per_file_row_counts)):
                part_filename = os.path.join(output_dir, f"{base_filename}_{i+1}{file_extension}")
                part_size = os.path.getsize(part_filename)
                row_count = per_file_row_counts[i]
                log_file.write(f"File {i+1}: {row_count} data rows, {part_size:,} bytes\n")

            log_file.write(f"\nTotal Data Rows in Split Files: {output_data_row_count:,}\n")
            if input_data_row_count == output_data_row_count:
                log_file.write("Validation: PASS ✅\n")
            else:
                log_file.write("Validation: FAIL ❌\n")
            log_file.write(f"\n============================================================\n")

    def show_success(self, parts, directory):
        elapsed_time = time.time() - self.start_time
        time_str = f"{elapsed_time:.1f} seconds"
        if elapsed_time >= 60:
            time_str = f"{elapsed_time/60:.1f} minutes"
        
        # Change percentage color based on validation result
        if self.input_row_count == self.output_row_count:
            # Success - show percentage in green
            self.progress_label.configure(style="ProgressSuccess.TLabel")
        else:
            # Validation failed - show percentage in red
            self.progress_label.configure(style="ProgressFail.TLabel")
        
        # Enable Reset button after completion
        self.button_reset.config(state="normal")
        
        # Open directory if requested (no popup message)
        if self.open_dir_after_split.get():
            try:
                os.startfile(directory)
            except AttributeError:
                import subprocess
                import platform
                if platform.system() == "Darwin":
                    subprocess.call(["open", directory])
                elif platform.system() == "Linux":
                    subprocess.call(["xdg-open", directory])

    def show_cancelled(self):
        # Show percentage in red for cancelled operation
        self.progress_label.configure(style="ProgressFail.TLabel")
        
        # Enable Reset button after cancellation
        self.button_reset.config(state="normal")
        
        messagebox.showinfo("Cancelled", "❌ Operation was cancelled by user.")

    def reset_ui(self):
        self.is_running = False
        self.button_start.config(state=tk.NORMAL)
        self.button_cancel.config(state=tk.DISABLED)
        # Keep progress bar and percentage visible after completion

    def reset_stats_and_progress(self):
        """Reset statistics, progress, split settings, source file, and output directory"""
        # Reset progress bar and percentage
        self.progress['value'] = 0
        self.progress_percentage.set("")
        self.progress_label.configure(style="TLabel")  # Reset to default style
        
        # Clear all statistics
        self.total_rows.set("")
        self.current_file.set("")
        self.rows_processed.set("")
        self.file_count.set("")
        self.output_file_type.set("")
        
        # Reset validation tracking
        self.input_row_count = 0
        self.output_row_count = 0
        self.current_part_num = 0
        
        # Clear source file and output directory
        self.input_file.set("")  # Clear source file
        self.output_dir.set("")  # Clear output directory
        
        # Reset Split Settings
        self.split_mode.set("Size (MB)")  # Reset to default split mode
        self.split_value.set("")  # Clear split value
        self.file_type.set(".csv")  # Reset to default file type
        self.use_custom_delim.set(False)  # Reset custom delimiter checkbox
        self.custom_delimiter.set("")  # Clear custom delimiter value
        self.quote_mode.set("Standard")  # Reset quote mode
        
        # NOTE: We don't reset Settings menu options (open_dir_after_split, create_log, retain_header)
        # because they are persistent user preferences
        
        # Clear error highlighting
        self.clear_field_error(self.input_file_entry)
        self.clear_field_error(self.split_value_entry)
        
        # Clear column data
        self.available_columns = []
        self.selected_columns = []
        self.column_renames = {}
        
        # Update UI states (this will trigger on_input_file_change which disables buttons appropriately)
        self.toggle_delim_fields()  # Update delimiter field states
        
        # Disable Reset button again
        self.button_reset.config(state="disabled")

    def on_input_file_change(self, *args):
        if not self.input_file.get():
            # Disable buttons when no file selected
            self.output_browse_button.config(state="disabled")
            self.column_select_button.config(state="disabled")
            self.split_value_entry.config(state="disabled")  # Disable split value input
            self.output_dir.set("")  # Clear output directory
            
            self.delim_checkbox.state(["disabled"])
            self.use_custom_delim.set(False)
            self.toggle_delim_fields()
            # Clear stats when no file selected
            self.total_rows.set("")
            self.current_file.set("")
            self.rows_processed.set("")
            self.file_count.set("")
            self.output_file_type.set("")
            
            # Clear column data
            self.available_columns = []
            self.selected_columns = []
            self.column_renames = {}
            
            # Update quote mode state when no file is selected
            self.update_quote_mode_state()
        else:
            # Clear error highlighting when a file is selected
            self.clear_field_error(self.input_file_entry)
            
            # Enable buttons when file is selected
            self.output_browse_button.config(state="normal")
            self.column_select_button.config(state="normal")
            self.split_value_entry.config(state="normal")  # Enable split value input
            
            # Enable delimiter options based on OUTPUT format
            if self.file_type.get() != ".json":
                # Output format uses delimiters - enable delimiter options regardless of input format
                self.delim_checkbox.state(["!disabled"])
            else:
                # Output is JSON - disable delimiter options
                self.delim_checkbox.state(["disabled"])
                    
            # Clear previous stats when new file selected
            self.total_rows.set("")
            self.current_file.set("")
            self.rows_processed.set("")
            self.file_count.set("")
            self.output_file_type.set("")
            
            # Update quote mode state when file is selected
            self.update_quote_mode_state()

if __name__ == "__main__":
    root = tk.Tk()
    app = FileSplitterApp(root)
    root.mainloop()