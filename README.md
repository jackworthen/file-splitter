# 📁✂️ File Splitter Pro
> 🚀 **Split large files with ease!** A powerful, user-friendly GUI application for splitting CSV, TXT, and DAT files by size or row count.

---

## 🌟 Why File Splitter Pro?

Ever had a massive CSV file that's too big to open in Excel? 📊 Or needed to break down large datasets for processing? **File Splitter Pro** is here to save the day! With its intuitive interface and powerful features, splitting files has never been easier.

## ✨ Features

### 🎯 **Core Functionality**
- **📏 Split by Size**: Break files into chunks of specified megabytes
- **📊 Split by Rows**: Divide files by exact row count
- **🔧 Smart Delimiter Detection**: Automatically detects CSV delimiters
- **⚙️ Custom Delimiters**: Use your own delimiter for maximum flexibility

### 🎨 **User Experience**
- **🖥️ Beautiful GUI**: Clean, modern interface built with tkinter
- **📂 Easy File Selection**: Drag, drop, or browse for files
- **📁 Custom Output Directory**: Choose where your split files go
- **🚀 Threaded Processing**: Non-blocking UI during file operations
- **📋 Detailed Logging**: Track every split operation with comprehensive logs

### 🛠️ **File Support**
- **📄 CSV Files** (`.csv`)
- **📝 Text Files** (`.txt`)
- **💾 Data Files** (`.dat`)

### 🌍 **Cross-Platform**
- ✅ **Windows** (with automatic folder opening)
- ✅ **macOS** (native support)
- ✅ **Linux** (full compatibility)

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
Click **Browse** to select the file you want to split. The app supports CSV, TXT, and DAT files.

### Step 2: 📂 Choose Output Location
Pick where you want your split files to be saved. By default, it creates a `split_files` folder next to your original file.

### Step 3: ⚙️ Configure Split Settings
Choose your splitting method:
- **📏 By Size**: Enter the maximum size in MB per file
- **📊 By Rows**: Enter the maximum number of rows per file

### Step 4: 🔧 Fine-tune (Optional)
- **Delimiter Settings**: Let the app auto-detect or specify your own
- **Output Format**: Choose between CSV, TXT, or DAT output
- **Logging**: Keep detailed logs of your operations (recommended!)

### Step 5: ✂️ Split!
Click **Start Splitting** and watch the magic happen! ✨

---

## 🏗️ Technical Details

### Architecture
- **🧵 Multi-threaded**: File operations run in background threads
- **🔍 Smart Detection**: CSV sniffer for automatic delimiter detection
- **💾 Memory Efficient**: Processes files line-by-line for large datasets
- **📊 Validation**: Automatic row count verification

### File Handling
- **🔒 Safe Processing**: Preserves original files
- **📋 Header Preservation**: Maintains CSV headers in all split files
- **🎯 Precise Splitting**: Accurate size and row count splitting
- **📝 UTF-8 Support**: Full Unicode character support

### Logging Features
- **⏰ Timestamps**: Every operation is timestamped
- **📊 Statistics**: Input/output file sizes and row counts
- **✅ Validation**: Automatic verification of split accuracy
- **📁 Part Details**: Size and row count for each generated file

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

- 🐙 Developed by Jack Worthen [@jackworthen](https://github.com/jackworthen)

---

### 🌟 If this project helped you, give it a star! ⭐
