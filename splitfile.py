import os
import csv
import threading
import tkinter as tk
from tkinter import ttk, filedialog, messagebox, Menu
import webbrowser
import time
import json

class FileSplitterApp:
    def __init__(self, root):
        self.root = root
        self.root.title("File Splitter Pro")

        try:
            icon_path = os.path.join(os.path.dirname(__file__), "filesplit_icon.ico")
            self.root.iconbitmap(default=icon_path)
        except Exception as e:
            print(f"Warning: Could not load icon. {e}")
        
        self.root.geometry("450x680")
        self.root.resizable(False, False)
        
        # Configure style
        self.setup_styles()

        # Variables
        self.input_file = tk.StringVar()
        self.max_size = tk.StringVar()
        self.max_rows = tk.StringVar()
        self.file_type = tk.StringVar(value=".csv")
        self.output_dir = tk.StringVar()
        self.split_mode = tk.StringVar(value="size")
        self.use_custom_delim = tk.BooleanVar(value=False)
        self.custom_delimiter = tk.StringVar(value="")
        self.detected_delimiter = tk.StringVar(value="")
        self.open_dir_after_split = tk.BooleanVar(value=False)
        self.create_log = tk.BooleanVar(value=True)

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

        self.create_menu()
        self.create_widgets()
        self.input_file.trace_add("write", self.on_input_file_change)
        self.file_type.trace_add("write", self.on_file_type_change)
        
        # Set up keyboard shortcuts
        self.setup_keyboard_shortcuts()

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
                       foreground="#3498db",  # Blue color for analyzing
                       background="#ecf0f1",
                       relief="flat",
                       borderwidth=1)
        style.configure("StatsFrame.TFrame",
                       background="#f8f9fa",
                       relief="solid",
                       borderwidth=1)

    def create_menu(self):
        menubar = Menu(self.root)

        file_menu = Menu(menubar, tearoff=0)
        file_menu.add_command(label="Exit", command=self.root.quit, accelerator="Ctrl+Q")
        menubar.add_cascade(label="File", menu=file_menu)

        help_menu = Menu(menubar, tearoff=0)
        help_menu.add_command(label="Documentation", command=self.open_help, accelerator="Ctrl+D")
        menubar.add_cascade(label="Help", menu=help_menu)

        self.root.config(menu=menubar)

    def setup_keyboard_shortcuts(self):
        """Set up keyboard shortcuts"""
        self.root.bind('<Control-q>', lambda e: self.root.quit())
        self.root.bind('<Control-Q>', lambda e: self.root.quit())
        self.root.bind('<Control-d>', lambda e: self.open_help())
        self.root.bind('<Control-D>', lambda e: self.open_help())

    def open_help(self):
        webbrowser.open("https://github.com/jackworthen/file-splitter")

    def create_widgets(self):
        main_frame = ttk.Frame(self.root, padding="15")
        main_frame.grid(row=0, column=0, sticky="nsew")

        # File Selection Section
        file_frame = ttk.LabelFrame(main_frame, text="File Selection", padding=10, style="Bold.TLabelframe")
        file_frame.grid(row=0, column=0, columnspan=3, pady=(0, 10), sticky="ew")
        
        ttk.Entry(file_frame, textvariable=self.input_file, width=50).grid(row=0, column=0, padx=(0, 10), pady=5, sticky="ew")
        ttk.Button(file_frame, text="Browse", command=self.select_file).grid(row=0, column=1, pady=5)
        file_frame.columnconfigure(0, weight=1)

        # Output Directory Section
        output_frame = ttk.LabelFrame(main_frame, text="Output Directory", padding=10, style="Bold.TLabelframe")
        output_frame.grid(row=1, column=0, columnspan=3, pady=(0, 10), sticky="ew")
        
        ttk.Entry(output_frame, textvariable=self.output_dir, width=50).grid(row=0, column=0, padx=(0, 10), pady=5, sticky="ew")
        ttk.Button(output_frame, text="Browse", command=self.select_output_directory).grid(row=0, column=1, pady=5)
        
        ttk.Checkbutton(output_frame, text="Enable Logging", variable=self.create_log).grid(row=1, column=0, columnspan=2, pady=(5, 0), sticky="w")
        ttk.Checkbutton(output_frame, text="Open Directory After Split", variable=self.open_dir_after_split).grid(row=2, column=0, columnspan=2, pady=5, sticky="w")
        output_frame.columnconfigure(0, weight=1)

        # Split Settings Section
        settings_frame = ttk.LabelFrame(main_frame, text="Split Settings", padding=10, style="Bold.TLabelframe")
        settings_frame.grid(row=2, column=0, columnspan=3, pady=(0, 10), sticky="ew")
        
        # Split mode selection
        ttk.Radiobutton(settings_frame, text="Split by Size (MB):", variable=self.split_mode, 
                       value="size", command=self.toggle_mode).grid(row=0, column=0, sticky="w")
        self.size_entry = ttk.Entry(settings_frame, textvariable=self.max_size, width=10)
        self.size_entry.grid(row=0, column=1, sticky="w", padx=(5, 20))
        
        ttk.Radiobutton(settings_frame, text="Split by Rows:", variable=self.split_mode, 
                       value="rows", command=self.toggle_mode).grid(row=0, column=2, sticky="w")
        self.row_entry = ttk.Entry(settings_frame, textvariable=self.max_rows, width=10, state="disabled")
        self.row_entry.grid(row=0, column=3, sticky="w", padx=(5, 0))
        
        # File type selection
        ttk.Label(settings_frame, text="Output file type:").grid(row=1, column=0, pady=(10, 0), sticky="w")
        ttk.Combobox(settings_frame, textvariable=self.file_type, values=[".csv", ".txt", ".dat", ".json"], width=10).grid(row=1, column=1, pady=(10, 0), sticky="w")

        # Delimiter settings
        self.delim_checkbox = ttk.Checkbutton(settings_frame, text="Custom Delimiter", 
                                            variable=self.use_custom_delim, command=self.toggle_delim_fields)
        self.delim_checkbox.state(["disabled"])
        self.delim_checkbox.grid(row=2, column=0, columnspan=2, pady=(10, 0), sticky="w")

        self.delim_label = ttk.Label(settings_frame, text="Current Delimiter:")
        self.delim_display = ttk.Label(settings_frame, textvariable=self.detected_delimiter)
        self.set_delim_label = ttk.Label(settings_frame, text="New Delimiter:")
        self.set_delim_entry = ttk.Entry(settings_frame, textvariable=self.custom_delimiter, width=5)
        self.set_delim_entry.config(validate="key", 
                                  validatecommand=(self.root.register(self.validate_delimiter), "%P"))

        self.delim_label.grid(row=3, column=0, sticky="w")
        self.delim_display.grid(row=3, column=1, sticky="w")
        self.set_delim_label.grid(row=4, column=0, sticky="w")
        self.set_delim_entry.grid(row=4, column=1, sticky="w")
        
        # Initially hide delimiter fields
        self.delim_label.grid_remove()
        self.delim_display.grid_remove()
        self.set_delim_label.grid_remove()
        self.set_delim_entry.grid_remove()
        settings_frame.columnconfigure(0, weight=1)

        # Progress Section
        progress_frame = ttk.LabelFrame(main_frame, text="Progress", padding=10, style="Bold.TLabelframe")
        progress_frame.grid(row=3, column=0, columnspan=3, pady=(0, 10), sticky="ew")
        
        # Progress bar with percentage
        self.progress = ttk.Progressbar(progress_frame, mode='determinate')
        self.progress.grid(row=0, column=0, sticky="ew", padx=(0, 10), pady=(0, 10))
        
        self.progress_label = ttk.Label(progress_frame, textvariable=self.progress_percentage, width=8)
        self.progress_label.grid(row=0, column=1, pady=(0, 10))
        
        # Stats display
        stats_frame = ttk.Frame(progress_frame, style="StatsFrame.TFrame", padding=10)
        stats_frame.grid(row=1, column=0, columnspan=2, sticky="ew", pady=(5, 0))
        
        # Create a vertical layout for stats
        stats_container = ttk.Frame(stats_frame)
        stats_container.grid(row=0, column=0, sticky="ew")
        stats_frame.columnconfigure(0, weight=1)
        stats_container.columnconfigure(1, weight=1)
        
        # Total Rows
        ttk.Label(stats_container, text="Total Rows:", style="Stats.TLabel").grid(row=0, column=0, sticky="w", padx=(0, 5), pady=(0, 5))
        self.total_rows_label = ttk.Label(stats_container, textvariable=self.total_rows, style="StatsAnalyzing.TLabel", width=15, anchor="w")
        self.total_rows_label.grid(row=0, column=1, sticky="ew", padx=(0, 0), pady=(0, 5))
        
        # Current File  
        ttk.Label(stats_container, text="Current File:", style="Stats.TLabel").grid(row=1, column=0, sticky="w", padx=(0, 5), pady=(0, 5))
        current_file_label = ttk.Label(stats_container, textvariable=self.current_file, style="StatsAnalyzing.TLabel", width=15, anchor="w")
        current_file_label.grid(row=1, column=1, sticky="ew", padx=(0, 0), pady=(0, 5))
        
        # Rows Processed
        ttk.Label(stats_container, text="Rows Processed:", style="Stats.TLabel").grid(row=2, column=0, sticky="w", padx=(0, 5), pady=(0, 5))
        rows_processed_label = ttk.Label(stats_container, textvariable=self.rows_processed, style="StatsAnalyzing.TLabel", width=15, anchor="w")
        rows_processed_label.grid(row=2, column=1, sticky="ew", pady=(0, 5))
        
        # Output File Type
        ttk.Label(stats_container, text="Output File Type:", style="Stats.TLabel").grid(row=3, column=0, sticky="w", padx=(0, 5))
        output_type_label = ttk.Label(stats_container, textvariable=self.output_file_type, style="StatsAnalyzing.TLabel", width=15, anchor="w")
        output_type_label.grid(row=3, column=1, sticky="ew")
        
        progress_frame.columnconfigure(0, weight=1)

        # Control Buttons
        button_frame = ttk.Frame(main_frame)
        button_frame.grid(row=4, column=0, columnspan=3, pady=(0, 10))
        
        self.button_start = ttk.Button(button_frame, text="Run", command=self.start_threaded_split)
        self.button_start.grid(row=0, column=0, padx=(0, 10))
        
        self.button_cancel = ttk.Button(button_frame, text="Cancel", command=self.cancel_operation, state="disabled")
        self.button_cancel.grid(row=0, column=1)

        main_frame.columnconfigure(0, weight=1)

    def select_file(self):
        path = filedialog.askopenfilename(
            title="Select File to Split",
            filetypes=[("CSV files", "*.csv"), ("DAT files", "*.dat"), 
                      ("TXT files", "*.txt"), ("All files", "*.*")]
        )
        if path:
            default_out = os.path.join(os.path.dirname(path), 'split_files')
            self.output_dir.set(default_out.replace('\\', '/'))
            self.input_file.set(path)
            self.delim_checkbox.state(["!disabled"])
            try:
                with open(path, 'r', encoding='utf-8') as f:
                    sample = f.read(2048)
                    sniffer = csv.Sniffer()
                    dialect = sniffer.sniff(sample)
                    self.detected_delimiter.set(dialect.delimiter)
            except Exception as e:
                self.detected_delimiter.set(',')
                print(f"Could not detect delimiter: {e}")
            if self.use_custom_delim.get():
                self.toggle_delim_fields()

    def select_output_directory(self):
        path = filedialog.askdirectory(title="Select Output Directory")
        if path:
            self.output_dir.set(path)

    def toggle_mode(self):
        if self.split_mode.get() == "size":
            self.size_entry.config(state="normal")
            self.row_entry.config(state="disabled")
        else:
            self.size_entry.config(state="disabled")
            self.row_entry.config(state="normal")

    def on_file_type_change(self, *args):
        """Handle file type changes to enable/disable delimiter options"""
        if self.file_type.get() == ".json":
            # Disable delimiter options for JSON
            self.use_custom_delim.set(False)
            self.delim_checkbox.state(["disabled"])
            self.toggle_delim_fields()
        else:
            # Enable delimiter options for other formats if file is selected
            if self.input_file.get():
                self.delim_checkbox.state(["!disabled"])

    def toggle_delim_fields(self):
        show = (self.use_custom_delim.get() and 
                self.input_file.get() and 
                self.file_type.get() != ".json")
        for widget in [self.delim_label, self.delim_display, self.set_delim_label, self.set_delim_entry]:
            widget.grid() if show else widget.grid_remove()

    def start_threaded_split(self):
        file_path = self.input_file.get()
        extension = self.file_type.get().strip().lower()
        out_dir = self.output_dir.get()
        mode = self.split_mode.get()

        if not file_path:
            messagebox.showwarning("Warning", "Please select a file to split.")
            return

        try:
            value = int(self.max_size.get() if mode == "size" else self.max_rows.get())
            if value <= 0:
                raise ValueError
        except ValueError:
            messagebox.showwarning("Warning", "Please enter a valid positive number for size or rows.")
            return

        if not out_dir:
            out_dir = os.path.join(os.path.dirname(file_path), "split_files")

        # Reset progress tracking
        self.cancel_event.clear()
        self.is_running = True
        self.start_time = time.time()
        
        # Update UI state
        self.button_start.config(state=tk.DISABLED)
        self.button_cancel.config(state=tk.NORMAL)
        self.progress['value'] = 0
        self.progress_percentage.set("0%")
        self.total_rows.set("")
        self.current_file.set("Initializing...")
        self.rows_processed.set("0")
        self.output_file_type.set(extension.upper())

        delim = self.custom_delimiter.get() if self.use_custom_delim.get() else self.detected_delimiter.get() or ','
        thread = threading.Thread(target=self.split_file, 
                                args=(file_path, out_dir, mode, value, extension, delim))
        thread.daemon = True
        thread.start()

    def cancel_operation(self):
        if self.is_running:
            self.cancel_event.set()
            self.current_file.set("Cancelling...")
            self.button_cancel.config(state=tk.DISABLED)

    def update_progress(self, current_row, total_rows, current_filename):
        """Update progress from worker thread"""
        if total_rows > 0:
            percentage = min(100, (current_row / total_rows) * 100)
            
            # Schedule UI updates
            self.root.after(0, lambda: self.progress.configure(value=percentage))
            self.root.after(0, lambda: self.progress_percentage.set(f"{percentage:.1f}%"))
            self.root.after(0, lambda: self.current_file.set(os.path.basename(current_filename)))
            self.root.after(0, lambda: self.rows_processed.set(f"{current_row:,}"))

    def split_file(self, input_file, output_dir, mode, size_or_rows, file_extension, custom_delimiter):
        try:
            os.makedirs(output_dir, exist_ok=True)
            
            # First pass: count total rows for progress tracking
            self.root.after(0, lambda: self.total_rows.set("Analyzing file..."))
            total_rows = 0
            with open(input_file, 'r', newline='', encoding='utf-8') as infile:
                detected_delimiter = self.detected_delimiter.get() or ','
                reader = csv.reader(infile, delimiter=detected_delimiter)
                next(reader)  # Skip header
                for _ in reader:
                    if self.cancel_event.is_set():
                        return
                    total_rows += 1
                    if total_rows % 1000 == 0:  # Update every 1000 rows during analysis
                        self.root.after(0, lambda r=total_rows: self.total_rows.set(f"Analyzing... {r:,} rows"))

            if self.cancel_event.is_set():
                return

            # Update total rows display
            self.root.after(0, lambda: self.total_rows.set(f"{total_rows:,}"))

            # Second pass: actual splitting with progress tracking
            part_num = 1
            base_filename = os.path.splitext(os.path.basename(input_file))[0]
            max_size_bytes = size_or_rows * 1024 * 1024 if mode == "size" else None
            max_rows = size_or_rows if mode == "rows" else None
            is_json_format = file_extension == ".json"

            with open(input_file, 'r', newline='', encoding='utf-8') as infile:
                detected_delimiter = self.detected_delimiter.get() or ','
                reader = csv.reader(infile, delimiter=detected_delimiter)
                header = next(reader)

                input_data_row_count = 0
                output_data_row_count = 0
                per_file_row_counts = []
                processed_rows = 0

                output_path = os.path.join(output_dir, f"{base_filename}_{part_num}{file_extension}")
                
                if is_json_format:
                    # For JSON, we'll collect rows in memory and write them all at once
                    current_json_data = []
                    current_rows = 0
                    estimated_size = 2  # Start with "[]" 
                    avg_row_size = 0  # Track average row size for better estimation
                else:
                    # For CSV/TXT/DAT, use the original method
                    outfile = open(output_path, 'w', newline='', encoding='utf-8')
                    writer = csv.writer(outfile, delimiter=custom_delimiter)
                    writer.writerow(header)
                    current_size = outfile.tell()
                    current_rows = 0

                for row in reader:
                    if self.cancel_event.is_set():
                        if not is_json_format:
                            outfile.close()
                        self.root.after(0, lambda: self.show_cancelled())
                        return

                    input_data_row_count += 1
                    processed_rows += 1
                    
                    # Update progress every 100 rows
                    if processed_rows % 100 == 0:
                        self.update_progress(processed_rows, total_rows, output_path)
                    
                    if is_json_format:
                        # Convert row to JSON object
                        row_dict = dict(zip(header, row))
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
                        # Original CSV/TXT/DAT logic
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
                            writer = csv.writer(outfile, delimiter=custom_delimiter)
                            writer.writerow(header)
                            current_size = outfile.tell()
                            current_rows = 0

                        writer.writerow(row)
                        current_size = outfile.tell()
                        current_rows += 1

                # Handle the last file
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

                # Final progress update
                self.update_progress(total_rows, total_rows, output_path)

            if self.cancel_event.is_set():
                self.root.after(0, lambda: self.show_cancelled())
                return

            # Create log file
            if self.create_log.get():
                log_path = os.path.join(output_dir, "log.txt")
                timestamp = time.strftime("%Y-%m-%d %H:%M:%S")
                input_file_size = os.path.getsize(input_file)

                with open(log_path, 'a', encoding='utf-8') as log_file:
                    log_file.write(f"\n")
                    log_file.write(f"File Splitter Log\n")
                    log_file.write(f"Timestamp: {timestamp}\n")
                    log_file.write(f"Input File: {input_file}\n")
                    log_file.write(f"Input File Size: {input_file_size:,} bytes\n")
                    log_file.write(f"Total Data Rows in Input File: {input_data_row_count:,}\n")
                    log_file.write(f"Total Parts Created: {part_num}\n")
                    log_file.write(f"Output Format: {file_extension}\n\n")

                    for i in range(part_num):
                        part_filename = os.path.join(output_dir, f"{base_filename}_{i+1}{file_extension}")
                        part_size = os.path.getsize(part_filename)
                        row_count = per_file_row_counts[i]
                        log_file.write(f"Part {i+1}: {row_count} data rows, {part_size:,} bytes\n")

                    log_file.write(f"\nTotal Data Rows in Split Files: {output_data_row_count:,}\n")
                    if not is_json_format:
                        log_file.write(f"Delimiter Used: '{custom_delimiter}'\n")
                    if input_data_row_count == output_data_row_count:
                        log_file.write("Validation: PASS ✅\n")
                    else:
                        log_file.write("Validation: FAIL ❌\n")
                    log_file.write(f"\n============================================================\n")
            
            self.root.after(0, lambda: self.show_success(part_num, output_dir))
            
        except Exception as e:
            self.root.after(0, lambda: messagebox.showerror("Error", f"An error occurred: {e}"))
        finally:
            self.root.after(0, self.reset_ui)

    def show_success(self, parts, directory):
        elapsed_time = time.time() - self.start_time
        time_str = f"{elapsed_time:.1f} seconds"
        if elapsed_time >= 60:
            time_str = f"{elapsed_time/60:.1f} minutes"
        
        messagebox.showinfo("Success", 
                          f"✅ File successfully split into {parts} parts!\n\n"
                          f"Time taken: {time_str}\n"
                          f"Output location:\n{directory}")
        
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
        messagebox.showinfo("Cancelled", "❌ Operation was cancelled by user.")

    def reset_ui(self):
        self.is_running = False
        self.button_start.config(state=tk.NORMAL)
        self.button_cancel.config(state=tk.DISABLED)
        self.progress['value'] = 0
        self.progress_percentage.set("")
        # Keep stats values visible after completion for user validation

    def validate_delimiter(self, text):
        return len(text) <= 1 and (text == '' or text.isprintable())

    def on_input_file_change(self, *args):
        if not self.input_file.get():
            self.delim_checkbox.state(["disabled"])
            self.use_custom_delim.set(False)
            self.toggle_delim_fields()
            # Clear stats when no file selected
            self.total_rows.set("")
            self.current_file.set("")
            self.rows_processed.set("")
            self.output_file_type.set("")
        else:
            # Enable delimiter checkbox only if not JSON format
            if self.file_type.get() != ".json":
                self.delim_checkbox.state(["!disabled"])
            # Clear previous stats when new file selected
            self.total_rows.set("")
            self.current_file.set("")
            self.rows_processed.set("")
            self.output_file_type.set("")

if __name__ == "__main__":
    root = tk.Tk()
    app = FileSplitterApp(root)
    root.mainloop()