# FileDog Setup Instructions

## Quick Start

### 1. Activate Virtual Environment

**Windows (Command Prompt):**
```cmd
venv\Scripts\activate
```

**Windows (PowerShell):**
```powershell
venv\Scripts\Activate.ps1
```

**Windows (Git Bash/MINGW64):**
```bash
source venv/Scripts/activate
```

**Linux/macOS:**
```bash
source venv/bin/activate
```

### 2. Install Dependencies (if not already installed)

```bash
pip install -r requirements.txt
pip install python-magic-bin  # Windows only
```

### 3. Launch FileDog

**GUI Application:**
```bash
python filedog.py
# or
python filedog.py gui
```

**Command Line:**
```bash
python filedog.py cli /path/to/organize
```

**Background Service:**
```bash
python filedog.py service status
python filedog.py service start
```

## Alternative Launch Methods

### Using Cross-Platform Scripts

**Windows:**
```cmd
filedog.bat
filedog.bat cli C:\Users\%USERNAME%\Downloads
```

**Linux/macOS:**
```bash
chmod +x filedog.sh
./filedog.sh
./filedog.sh cli ~/Downloads
```

### Direct Python Execution

If you're in the `src/` directory:
```bash
cd src
python main.py  # GUI only
python cli.py --help  # CLI help
python background_service.py status  # Service status
```

## Troubleshooting

### "ModuleNotFoundError: No module named 'PySide6'"

This means you're not running Python from the virtual environment. Make sure to:

1. **Activate the virtual environment first:**
   ```bash
   # Windows Git Bash/MINGW64
   source venv/Scripts/activate
   
   # Windows CMD
   venv\Scripts\activate
   ```

2. **Verify activation:**
   ```bash
   which python  # Should show path to venv/Scripts/python
   python -c "import PySide6; print('PySide6 available')"
   ```

3. **Then run FileDog:**
   ```bash
   python filedog.py
   ```

### Virtual Environment Setup (if needed)

If you don't have a virtual environment yet:
```bash
python -m venv venv
source venv/Scripts/activate  # Windows Git Bash
pip install -r requirements.txt
pip install python-magic-bin  # Windows only
```

## Features

- **Manual Organization**: Select folder → Organize files by type
- **Auto Watching**: Monitor directories for new files
- **Background Service**: Run file watching even when GUI is closed
- **Cross-Platform**: Works on Windows, macOS, Linux
- **CLI Interface**: Command-line tools for automation

## File Organization

Files are organized into folders based on type:
- Images → `Images/`
- Videos → `Videos/`
- Audio → `Audios/`
- Documents → `PDFs/`, `WordDocs/`, `Excels/`
- Code → `Python/`, `JavaScript/`
- Archives → `Archives/`
- And many more...
