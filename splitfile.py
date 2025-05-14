import os
import csv
import threading
import tkinter as tk
from tkinter import ttk, filedialog, messagebox, Menu
import webbrowser
import time

class FileSplitterApp:
    def __init__(self, root):
        self.root = root
        self.root.title("File Splitter Pro")

        try:
            icon_path = os.path.join(os.path.dirname(__file__), "filesplit_icon.ico")
            self.root.iconbitmap(default=icon_path)
        except Exception as e:
            print(f"Warning: Could not load icon. {e}")
        self.root.geometry("475x520")
        self.root.resizable(False, False)

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

        self.create_menu()
        self.create_widgets()
        self.input_file.trace_add("write", self.on_input_file_change)


    def create_menu(self):
        menubar = Menu(self.root)

        file_menu = Menu(menubar, tearoff=0)
        file_menu.add_command(label="⏻ Exit", command=self.root.quit)
        menubar.add_cascade(label="File", menu=file_menu)

        help_menu = Menu(menubar, tearoff=0)
        help_menu.add_command(label="📘 Documentation", command=self.open_help)
        help_menu.add_separator()
        help_menu.add_command(label="🛈 About", command=self.show_about)
        menubar.add_cascade(label="Help", menu=help_menu)

        self.root.config(menu=menubar)

    def open_help(self):
        help_path = os.path.join(os.path.dirname(__file__), "help.html")
        webbrowser.open(f"file://{help_path}")

    def create_widgets(self):
        file_frame = ttk.LabelFrame(self.root, text="File Selection", padding=10)
        file_frame.grid(row=0, column=0, columnspan=3, padx=15, pady=10, sticky="ew")
        ttk.Entry(file_frame, textvariable=self.input_file, width=50).grid(row=1, column=0, padx=(0, 10), pady=5, sticky="ew")
        ttk.Button(file_frame, text="Browse", command=self.select_file).grid(row=1, column=1, pady=5)

        output_frame = ttk.LabelFrame(self.root, text="Output Directory", padding=10)
        output_frame.grid(row=1, column=0, columnspan=3, padx=15, pady=10, sticky="ew")
        ttk.Entry(output_frame, textvariable=self.output_dir, width=50).grid(row=0, column=0, padx=(0, 10), pady=5, sticky="ew")
        ttk.Button(output_frame, text="Browse", command=self.select_output_directory).grid(row=0, column=1)

        ttk.Checkbutton(output_frame, text="Enable Logging", variable=self.create_log).grid(row=1, column=0, columnspan=2, pady=(5, 0), sticky="w")
        ttk.Checkbutton(output_frame, text="Open Output Directory", variable=self.open_dir_after_split).grid(row=2, column=0, columnspan=2, pady=5, sticky="w")

        settings_frame = ttk.LabelFrame(self.root, text="Split Settings", padding=10)
        settings_frame.grid(row=2, column=0, columnspan=3, padx=15, pady=10, sticky="ew")
        ttk.Radiobutton(settings_frame, text="Split by Size (MB):", variable=self.split_mode, value="size", command=self.toggle_mode).grid(row=0, column=0, sticky="w")
        self.size_entry = ttk.Entry(settings_frame, textvariable=self.max_size, width=10)
        self.size_entry.grid(row=0, column=1, sticky="w", padx=(5, 20))
        ttk.Radiobutton(settings_frame, text="Split by Rows:", variable=self.split_mode, value="rows", command=self.toggle_mode).grid(row=0, column=2, sticky="w")
        self.row_entry = ttk.Entry(settings_frame, textvariable=self.max_rows, width=10, state="disabled")
        self.row_entry.grid(row=0, column=3, sticky="w", padx=(5, 0))
        ttk.Label(settings_frame, text="Output file type:").grid(row=1, column=0, pady=(10, 0), sticky="w")
        ttk.Combobox(settings_frame, textvariable=self.file_type, values=[".csv", ".txt", ".dat"], width=10).grid(row=1, column=1, pady=(10, 0), sticky="w")

        self.delim_checkbox = ttk.Checkbutton(settings_frame, text="Custom Delimiter", variable=self.use_custom_delim, command=self.toggle_delim_fields)
        self.delim_checkbox.state(["disabled"])
        self.delim_checkbox.grid(row=2, column=0, columnspan=2, pady=(10, 0), sticky="w")

        self.delim_label = ttk.Label(settings_frame, text="Current Delimiter:")
        self.delim_display = ttk.Label(settings_frame, textvariable=self.detected_delimiter)
        self.set_delim_label = ttk.Label(settings_frame, text="New Delimiter:")
        self.set_delim_entry = ttk.Entry(settings_frame, textvariable=self.custom_delimiter, width=5)
        self.set_delim_entry.config(validate="key", validatecommand=(self.root.register(self.validate_delimiter), "%P"))

        self.delim_label.grid(row=3, column=0, sticky="w")
        self.delim_display.grid(row=3, column=1, sticky="w")
        self.set_delim_label.grid(row=4, column=0, sticky="w")
        self.set_delim_entry.grid(row=4, column=1, sticky="w")
        self.delim_label.grid_remove()
        self.delim_display.grid_remove()
        self.set_delim_label.grid_remove()
        self.set_delim_entry.grid_remove()

        self.button_start = ttk.Button(self.root, text="Start Splitting", width=25, command=self.start_threaded_split)
        self.button_start.grid(row=3, column=0, columnspan=3, pady=(15, 5))

        self.progress = ttk.Progressbar(self.root, mode='indeterminate')
        self.progress.grid(row=4, column=0, columnspan=3, padx=15, pady=(5, 10), sticky="ew")

    def select_file(self):
        path = filedialog.askopenfilename(filetypes=[("CSV files", "*.csv"), ("DAT files", "*.dat"), ("TXT files", "*.txt"), ("All files", "*.*")])
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
        path = filedialog.askdirectory()
        if path:
            self.output_dir.set(path)

    def toggle_mode(self):
        if self.split_mode.get() == "size":
            self.size_entry.config(state="normal")
            self.row_entry.config(state="disabled")
        else:
            self.size_entry.config(state="disabled")
            self.row_entry.config(state="normal")

    def toggle_delim_fields(self):
        show = self.use_custom_delim.get() and self.input_file.get()
        for widget in [self.delim_label, self.delim_display, self.set_delim_label, self.set_delim_entry]:
            widget.grid() if show else widget.grid_remove()

    def start_threaded_split(self):
        file_path = self.input_file.get()
        extension = self.file_type.get().strip().lower()
        out_dir = self.output_dir.get()
        mode = self.split_mode.get()

        if not file_path:
            messagebox.showwarning("Warning", "Select a file to split.")
            return

        try:
            value = int(self.max_size.get() if mode == "size" else self.max_rows.get())
            if value <= 0:
                raise ValueError
        except ValueError:
            messagebox.showwarning("Warning", "Enter a valid number for size or rows.")
            return

        if not out_dir:
            out_dir = os.path.join(os.path.dirname(file_path), "split_files")

        self.button_start.config(state=tk.DISABLED)
        self.progress.start()
        self.root.update_idletasks()

        delim = self.custom_delimiter.get() if self.use_custom_delim.get() else self.detected_delimiter.get() or ','
        thread = threading.Thread(target=self.split_file, args=(file_path, out_dir, mode, value, extension, delim))
        thread.start()

    def split_file(self, input_file, output_dir, mode, size_or_rows, file_extension, custom_delimiter):
        try:
            os.makedirs(output_dir, exist_ok=True)
            part_num = 1
            base_filename = os.path.splitext(os.path.basename(input_file))[0]
            max_size_bytes = size_or_rows * 1024 * 1024 if mode == "size" else None
            max_rows = size_or_rows if mode == "rows" else None

            with open(input_file, 'r', newline='', encoding='utf-8') as infile:
                detected_delimiter = self.detected_delimiter.get() or ','
                reader = csv.reader(infile, delimiter=detected_delimiter)
                header = next(reader)

                input_data_row_count = 0
                output_data_row_count = 0
                per_file_row_counts = []

                output_path = os.path.join(output_dir, f"{base_filename}_{part_num}{file_extension}")
                outfile = open(output_path, 'w', newline='', encoding='utf-8')
                writer = csv.writer(outfile, delimiter=custom_delimiter)
                writer.writerow(header)
                current_size = outfile.tell()
                current_rows = 0

                for row in reader:
                    input_data_row_count += 1
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

                outfile.close()
                per_file_row_counts.append(current_rows)
                output_data_row_count += current_rows

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
                    log_file.write(f"Total Parts Created: {part_num}\n\n")

                    for i in range(part_num):
                        part_filename = os.path.join(output_dir, f"{base_filename}_{i+1}{file_extension}")
                        part_size = os.path.getsize(part_filename)
                        row_count = per_file_row_counts[i]
                        log_file.write(f"Part {i+1}: {row_count} data rows, {part_size:,} bytes\n")

                    log_file.write(f"\nTotal Data Rows in Split Files: {output_data_row_count:,}\n")
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
        messagebox.showinfo("Success", f"File split into {parts} parts and saved in:\n{directory}")
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

    def reset_ui(self):
        self.button_start.config(state=tk.NORMAL)
        self.progress.stop()
        self.root.update_idletasks()

    def show_about(self):
        messagebox.showinfo("About", "File Splitter Pro\nVersion: 1.3\nLast Updated: 5/13/2025\n\nDeveloped by Jack Worthen")

    def validate_delimiter(self, text):
        return len(text) <= 1 and (text == '' or text.isprintable())


    def on_input_file_change(self, *args):
        if not self.input_file.get():
            self.delim_checkbox.state(["disabled"])
            self.use_custom_delim.set(False)
            self.toggle_delim_fields()
        else:
            self.delim_checkbox.state(["!disabled"])

if __name__ == "__main__":
    root = tk.Tk()
    app = FileSplitterApp(root)
    root.mainloop()
