# FileDog - Cross-Platform File Organizer

FileDog is a powerful, cross-platform file organization tool that automatically sorts your files by type. It features both manual organization and automatic file watching capabilities, making it perfect for keeping your Downloads folder, Desktop, and other directories clean and organized.

## ✨ Features

- **Manual File Organization**: Organize existing files in any directory with a single click
- **Automatic File Watching**: Monitor directories and automatically organize new files as they arrive
- **Background Service**: Run file watching in the background even when the main app is closed
- **Cross-Platform**: Works on Windows, macOS, and Linux

##  Quick Start

### Installation

exe
.dmg
package for linux




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

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🙏 Acknowledgments

- Uses `python-magic` for file type detection
- Uses `watchdog` for filesystem monitoring
- Uses `PySide6` for the GUI interface
