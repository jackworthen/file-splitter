# 📁✂️ File Splitter Pro
> 🚀 **Split large files with ease!** A powerful, user-friendly GUI application for splitting CSV, TXT, DAT and JSON files by size or row count.

🚀[Quick Start](#-quick-start) • 🎮 [How to Use](#-how-to-use) • ✨ [Features](#-features) • 🎯 [Quoted Identifier Handling](#-quoted-identifier-handling) 

---

## 🌟 Why File Splitter Pro?

Ever had a massive CSV file that's too big to open in Excel? 📊 Or needed to break down large datasets for processing? **File Splitter Pro** is here to save the day! With its intuitive interface and powerful features, splitting files has never been easier.

## ✨ Features

### 🎯 **Core Functionality**
- **📏 Split by Size**: Break files into chunks of specified megabytes
- **📊 Split by Rows**: Divide files by exact row count
- **📂 Split by Number of Files**: Split data into a certain number of files
- **🔧 Smart Delimiter Detection**: Automatically detects CSV delimiters
- **⚙️ Custom Delimiters**: Use your own delimiter for maximum flexibility
- **🎛️ Column Selection & Renaming**: Choose which columns to include/exclude and rename them for better output
- **✅ Row Count Validation**: Automatic verification that input and output row counts match
- **🛑 Cancellation Support**: Stop operations mid-process with partial file preservation
- **📋 Header Row Control**: Option to include or exclude header rows in split files
- **🎯 Quoted Identifier Handling**: Control how fields are quoted in CSV output
- **💾 Persistent Settings**: User preferences automatically saved and restored between sessions

### 🎨 **User Experience**
- **🖥️ Beautiful GUI**: Clean, modern interface built with tkinter
- **📂 Easy File Selection**: Drag, drop, or browse for files
- **📁 Custom Output Directory**: Choose where your split files go
- **🎛️ Interactive Column Manager**: Intuitive two-panel interface for column selection, exclusion, and renaming with reset functionality
- **⚙️ Settings Menu**: Persistent user preferences for directory opening, logging, and header retention
- **📋 Menu System**: File, Settings, and Help menus with keyboard shortcuts
- **🚀 Threaded Processing**: Non-blocking UI during file operations
- **📊 Real-time Statistics**: Live dashboard showing progress, file count, and processing stats
- **🎯 Progress Tracking**: Visual progress bar with percentage completion
- **🔄 Reset Functionality**: Clear all statistics and Split Settings to start fresh with one-click reset
- **⌨️ Enhanced Keyboard Shortcuts**: Ctrl+Q to quit, Ctrl+D for help, Ctrl+R to clear inputs
- **🎨 Visual Feedback**: Color-coded progress indicators for success/failure
- **📋 Enhanced Logging**: Comprehensive logs with file details, column selection, and validation results

### 🛠️ **File Support**
- **📄 CSV Files** (`.csv`) - with intelligent delimiter handling
- **📝 Text Files** (`.txt`) - preserving original formatting
- **💾 Data Files** (`.dat`) - for specialized data formats
- **🗂️ JSON Files** (`.json`) - with memory-efficient processing and flattening support

### 🌍 **Cross-Platform**
- ✅ **Windows** (with automatic folder opening and AppData config storage)
- ✅ **macOS** (native support with Application Support config storage)
- ✅ **Linux** (full compatibility with ~/.config storage)

### 🔧 **Advanced Features**
- **🧠 Memory Efficient**: Processes files line-by-line for large datasets
- **📋 Header Preservation**: Maintains headers in all split files (CSV/TXT/DAT)
- **🎛️ Smart Column Filtering & Renaming**: Remove unwanted columns and rename them for cleaner output
- **🌐 UTF-8 Support**: Full Unicode character support
- **⚡ Smart JSON Processing**: Efficient size estimation for JSON files with nested object flattening
- **📊 Detailed Statistics**: Track total rows, processed rows, current file, and file count
- **🛡️ Safe Processing**: Preserves original files during splitting
- **📝 Operation Logging**: Optional detailed logs with timestamps, column selection, and validation
- **🎯 Precise Splitting**: Accurate size and row count splitting algorithms
- **🔄 Format Conversion**: Convert between different file formats during splitting (e.g., JSON to CSV)
- **💾 Configuration Persistence**: Settings automatically saved to OS-appropriate locations (config.json)

---

## 🎯 Quoted Identifier Handling

When outputting to CSV, TXT, or DAT formats, you can control how fields are quoted:

### 📋 **Quoted Identifier Handling Options**

- **🔧 Standard** (Default): Uses minimal quoting - only quotes fields that contain special characters like commas, quotes, or newlines. This is the most common and compatible option.

- **📝 All Fields**: Quotes every single field in the output, regardless of content. Useful when you need consistent formatting or when working with systems that expect all fields to be quoted.

- **🚫 Never Quote**: Never adds quotes around fields, even if they contain special characters. Use with caution as this can create invalid CSV files if fields contain delimiter characters.

### 💡 **When to Use Each Mode**
- **Standard**: Best for most use cases and maximum compatibility
- **All Fields**: When you need consistent formatting or target system expects quoted fields
- **Never Quote**: Only when you're certain your data doesn't contain delimiter characters

---

## 🚀 Quick Start

### Prerequisites
- 🐍 Python 3.7 or higher
- 📦 Standard library only (no external dependencies!)

### Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/jackworthen/file-splitter.git
   cd file-splitter
   ```

2. **Run the application**
   ```bash
   python splitfile.py
   ```

---

## 🎮 How to Use

### Step 1: 📁 Select Your File
Click **Browse** to select the file you want to split. The app supports CSV, TXT, DAT, and JSON files.

### Step 2: 📂 Choose Output Location
Pick where you want your split files to be saved. By default, it creates a `split_files` folder next to your original file.

### Step 3: ⚙️ Configure Split Settings
Choose your splitting method:
- **📏 By Size**: Enter the maximum size in MB per file
- **📊 By Rows**: Enter the maximum number of rows per file
- **📂 By Number of Files**: Enter the maximum number files for split

### Step 4: 🎛️ Modify Columns (Optional)
Click **Modify Columns...** to customize your output:
- **🔄 Two-Panel Interface**: Move columns between "Excluded" and "Included" lists
- **✏️ Column Renaming**: Select any included column and click "Rename" to change its output name
- **➡️ Individual Control**: Use arrow buttons to move selected columns
- **🔄 Bulk Actions**: Include All or Exclude All with one click
- **🔄 Reset Option**: One-click reset to restore all columns and original names
- **💡 Smart Defaults**: All columns are included by default

### Step 5: 🔧 Fine-tune (Optional)
- **⚙️ Settings Menu**: Access persistent preferences for directory opening, logging, and header retention
- **Delimiter Settings**: Let the app auto-detect or specify your own (CSV/TXT/DAT only)
- **Output Format**: Choose between CSV, TXT, DAT, or JSON output
- **🎯 Quoted Identifier Handling**: Control field quoting behavior for CSV output

### Step 6: ✂️ Split!
Click **Run** and watch the real-time progress! ✨

### Step 7: 📊 Monitor Progress
- **Live Statistics**: Watch total rows, processed rows, current file, and file count
- **Progress Bar**: Visual indicator with percentage completion
- **Cancel Anytime**: Stop the operation if needed - partial files are preserved
- **Reset**: Clear all statistics and Split Settings with **File → Clear Inputs**

---

### Keyboard Shortcuts
- **Ctrl+Q**: Quick exit
- **Ctrl+D**: Open documentation/help
- **Ctrl+R**: Clear inputs and reset

---

## 🤝 Contributing

### 🐛 Found a Bug?
Open an issue with:
- 📝 Clear description of the problem
- 🔄 Steps to reproduce
- 💻 Your operating system and Python version
- 📁 Sample file (if applicable)

---

## 📜 License

This project is licensed under GNU GENERAL PUBLIC LICENSE - see the LICENSE file for details.

---

## 👨‍💻 Author

- 🐙 Developed by [Jack Worthen](https://github.com/jackworthen)
