# FileDog 🐕 - Cross-Platform File Organizer

FileDog is a powerful, cross-platform file organization tool that automatically sorts your files by type. It features both manual organization and automatic file watching capabilities, making it perfect for keeping your Downloads folder, Desktop, and other directories clean and organized.

## ✨ Features

- **Manual File Organization**: Organize existing files in any directory with a single click
- **Automatic File Watching**: Monitor directories and automatically organize new files as they arrive
- **Background Service**: Run file watching in the background even when the main app is closed
- **Cross-Platform**: Works on Windows, macOS, and Linux
- **GUI & CLI Interface**: Use the graphical interface or command-line tools
- **Customizable**: Configure file type mappings and organization rules
- **MIME Type Detection**: Accurate file type detection using python-magic
- **Safe Operations**: Handles file conflicts and provides dry-run mode

## 🚀 Quick Start

### Installation

1. **Clone the repository**:
   ```bash
   git clone https://github.com/abhijith-p-subash/filedog.git
   cd filedog
   ```

2. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

3. **Windows users also need**:
   ```bash
   pip install python-magic-bin
   ```

### Launch FileDog

**System Tray (Recommended - Background Monitoring)**:
```bash
python filedog.py
# Runs in background with system tray icon
```

**GUI Application Window**:
```bash
python filedog.py gui
```

**Command Line Interface**:
```bash
python filedog.py cli /path/to/organize
```

**Background Service**:
```bash
python filedog.py service status
python filedog.py service start
```

### Setup Automatic Startup

**Install to startup (runs automatically when system starts)**:
```bash
python setup_startup.py install
```

**Remove from startup**:
```bash
python setup_startup.py remove
```

**Check startup status**:
```bash
python setup_startup.py status
```

## 📖 Usage Modes

### 1. GUI Application

The GUI provides an intuitive interface with two main tabs:

#### Manual Organize Tab
- Select any folder you want to organize
- Click "Organize Files" to sort all files by type
- View real-time progress and logs
- Perfect for one-time organization tasks

#### Auto Watcher Tab
- Add directories you want to monitor (e.g., Downloads, Desktop)
- Enable the File Watcher to start automatic monitoring
- Files added to watched directories are automatically organized
- Works in the background even when the app is minimized

### 2. Command Line Interface

Organize files directly from the command line:

```bash
# Organize a directory
python filedog.py cli /path/to/directory

# Preview what would be organized (dry run)
python filedog.py cli /path/to/directory --dry-run

# Verbose output showing each file
python filedog.py cli /path/to/directory --verbose

# Use custom configuration
python filedog.py cli /path/to/directory --config custom_config.json
```

### 3. Background Service

Run file watching as a background service:

```bash
# Check service status
python filedog.py service status

# Start background monitoring
python filedog.py service start
```

**Note**: Configure watched directories and enable the watcher using the GUI first, then the service will monitor those directories automatically.

## 🛠️ File Organization

FileDog organizes files based on their MIME types into appropriate folders:

- **Images** → `Images/` (jpg, png, gif, svg, etc.)
- **Videos** → `Videos/` (mp4, avi, mov, mkv, etc.)
- **Audio** → `Audios/` (mp3, wav, flac, etc.)
- **Documents** → `PDFs/`, `WordDocs/`, `Excels/`, etc.
- **Code Files** → `Python/`, `JavaScript/`, etc.
- **Archives** → `Archives/` (zip, rar, tar, etc.)
- **And many more...**

### Custom Configuration

You can customize file type mappings by editing `src/config/folder_config.json`:

```json
{
  "file_type": {
    "image/": "Images",
    "video/": "Videos",
    "audio/": "Audios",
    "application/pdf": "PDFs",
    "text/plain": "TextFiles"
  },
  "default": "Others"
}
```

## 🔧 Advanced Usage

### Cross-Platform Launchers

**Windows**:
```cmd
filedog.bat
filedog.bat cli C:\Users\%USERNAME%\Downloads
filedog.bat service start
```

**Linux/macOS**:
```bash
chmod +x filedog.sh
./filedog.sh
./filedog.sh cli ~/Downloads
./filedog.sh service start
```

### Running in Background

1. **Setup**: Use the GUI to add directories and enable the watcher
2. **Background Service**: Run `python filedog.py service start`
3. **Verification**: Check status with `python filedog.py service status`

The background service will continue monitoring even after you close the GUI application.

### Testing File Watcher

Test the file watcher functionality:
```bash
python filedog.py test
```

This creates a test directory and demonstrates the automatic file organization feature.

## 📁 Project Structure

```
filedog/
├── filedog.py              # Main launcher script
├── filedog.bat             # Windows launcher
├── filedog.sh              # Unix/Linux launcher
├── requirements.txt        # Python dependencies
├── src/
│   ├── main.py            # GUI application entry point
│   ├── cli.py             # Command-line interface
│   ├── background_service.py  # Background service
│   ├── test_watcher.py    # Test script
│   ├── core/
│   │   ├── organizer.py   # File organization logic
│   │   └── file_watcher.py # File watching service
│   ├── ui/
│   │   └── main_window.py # GUI interface
│   └── config/
│       ├── folder_config.json    # File type mappings
│       └── watcher_config.json   # Watcher configuration
```

## 🔍 How It Works

1. **File Detection**: Uses `python-magic` for accurate MIME type detection
2. **Organization**: Creates folders based on file types and moves files accordingly
3. **Conflict Resolution**: Handles duplicate filenames by appending numbers
4. **Watching**: Uses `watchdog` library to monitor filesystem events
5. **Safety**: Includes delay mechanism to ensure files are fully downloaded before organizing

## 🛡️ Safety Features

- **Dry Run Mode**: Preview changes before applying them
- **Conflict Handling**: Automatically renames files to prevent overwrites
- **Error Recovery**: Graceful error handling with detailed logging
- **File Completion Check**: Waits for files to finish downloading before organizing

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🙏 Acknowledgments

- Uses `python-magic` for file type detection
- Uses `watchdog` for filesystem monitoring
- Uses `PySide6` for the GUI interface
