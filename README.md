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
- **🔧 Smart Delimiter Detection**: Automatically detects CSV delimiters
- **⚙️ Custom Delimiters**: Use your own delimiter for maximum flexibility
- **🎛️ Column Selection**: Choose which columns to include or exclude from split files
- **✅ Row Count Validation**: Automatic verification that input and output row counts match
- **🛑 Cancellation Support**: Stop operations mid-process with partial file preservation
- **📋 Header Row Control**: Option to include or exclude header rows in split files
- **🎯 Quoted Identifier Handling**: Control how fields are quoted in CSV output

### 🎨 **User Experience**
- **🖥️ Beautiful GUI**: Clean, modern interface built with tkinter
- **📂 Easy File Selection**: Drag, drop, or browse for files
- **📁 Custom Output Directory**: Choose where your split files go
- **🎛️ Interactive Column Selector**: Intuitive two-panel interface for column management
- **📋 Menu System**: File and Help menus with keyboard shortcuts
- **🚀 Threaded Processing**: Non-blocking UI during file operations
- **📊 Real-time Statistics**: Live dashboard showing progress, file count, and processing stats
- **🎯 Progress Tracking**: Visual progress bar with percentage completion
- **🔄 Reset Functionality**: Clear all statistics and Split Settings to start fresh
- **⌨️ Enhanced Keyboard Shortcuts**: Ctrl+Q to quit, Ctrl+D for help
- **🎨 Visual Feedback**: Color-coded progress indicators for success/failure
- **📋 Enhanced Logging**: Comprehensive logs with file details, column selection, and validation results

### 🛠️ **File Support**
- **📄 CSV Files** (`.csv`) - with intelligent delimiter handling
- **📝 Text Files** (`.txt`) - preserving original formatting
- **💾 Data Files** (`.dat`) - for specialized data formats
- **🗂️ JSON Files** (`.json`) - with memory-efficient processing and flattening support

### 🌍 **Cross-Platform**
- ✅ **Windows** (with automatic folder opening)
- ✅ **macOS** (native support)
- ✅ **Linux** (full compatibility)

### 🔧 **Advanced Features**
- **🧠 Memory Efficient**: Processes files line-by-line for large datasets
- **📋 Header Preservation**: Maintains headers in all split files (CSV/TXT/DAT)
- **🎛️ Smart Column Filtering**: Remove unwanted columns to reduce file sizes
- **🌐 UTF-8 Support**: Full Unicode character support
- **⚡ Smart JSON Processing**: Efficient size estimation for JSON files with nested object flattening
- **📊 Detailed Statistics**: Track total rows, processed rows, current file, and file count
- **🛡️ Safe Processing**: Preserves original files during splitting
- **📝 Operation Logging**: Optional detailed logs with timestamps, column selection, and validation
- **🎯 Precise Splitting**: Accurate size and row count splitting algorithms
- **🔄 Format Conversion**: Convert between different file formats during splitting (e.g., JSON to CSV)

---

## 🎯 Quoted Identifier Handling

When outputting to CSV, TXT, or DAT formats, you can control how fields are quoted:

### 📋 **Quote Mode Options**

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

### Step 4: 🎛️ Select Columns (Optional)
Click **Select Columns...** to choose which columns to include in your split files:
- **🔄 Two-Panel Interface**: Move columns between "Excluded" and "Included" lists
- **➡️ Individual Control**: Use arrow buttons to move selected columns
- **🔄 Bulk Actions**: Include All or Exclude All with one click
- **💡 Smart Defaults**: All columns are included by default

### Step 5: 🔧 Fine-tune (Optional)
- **📋 Header Control**: Toggle "Retain Header" to include/exclude header rows
- **Delimiter Settings**: Let the app auto-detect or specify your own (CSV/TXT/DAT only)
- **Output Format**: Choose between CSV, TXT, DAT, or JSON output
- **🎯 Quote Mode**: Control field quoting behavior for CSV output
- **📝 Logging**: Enable/disable detailed operation logs

### Step 6: ✂️ Split!
Click **Run** and watch the real-time progress! ✨

### Step 7: 📊 Monitor Progress
- **Live Statistics**: Watch total rows, processed rows, current file, and file count
- **Progress Bar**: Visual indicator with percentage completion
- **Cancel Anytime**: Stop the operation if needed - partial files are preserved
- **Reset**: Clear all statistics and Split Settings

---

### Keyboard Shortcuts
- **Ctrl+Q**: Quick exit
- **Ctrl+D**: Open documentation/help

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

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

## 👨‍💻 Author

- 🐙 Developed by [Jack Worthen](https://github.com/jackworthen)
