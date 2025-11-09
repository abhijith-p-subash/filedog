import sys
from pathlib import Path
from PySide6.QtWidgets import QApplication
from PySide6.QtGui import QIcon, QPixmap, QPainter, QBrush, QColor
from ui.main_window import MainWindow

def load_application_icon():
    """Load the application icon for the QApplication"""
    # Try to load the existing icon files
    icon_paths = [
        Path("../assets/filedog.svg"),
        Path("../assets/filedog_24x24.png"),
        Path("../filedog.ico"),
        Path("../filedog.svg"),
        Path("assets/filedog.svg"),
        Path("assets/filedog_24x24.png"),
        Path("filedog.ico"),
        Path("filedog.svg")
    ]
    
    for icon_path in icon_paths:
        if icon_path.exists():
            try:
                icon = QIcon(str(icon_path))
                if not icon.isNull():
                    return icon
            except Exception as e:
                print(f"Failed to load app icon from {icon_path}: {e}")
    
    # Fallback: create a simple programmatic icon
    pixmap = QPixmap(32, 32)
    pixmap.fill(QColor(0, 0, 0, 0))  # Transparent background
    
    painter = QPainter(pixmap)
    painter.setRenderHint(QPainter.RenderHint.Antialiasing)
    
    # Draw a simple folder-like icon with dog elements (based on SVG colors)
    painter.setBrush(QBrush(QColor(217, 158, 130)))  # Light brown from SVG
    painter.setPen(QColor(217, 158, 130))
    
    # Draw dog face
    painter.drawEllipse(4, 8, 24, 20)
    
    # Draw ears
    painter.setBrush(QBrush(QColor(102, 33, 19)))  # Dark brown
    painter.drawEllipse(2, 6, 8, 8)
    painter.drawEllipse(22, 6, 8, 8)
    
    # Draw folder element
    painter.setBrush(QBrush(QColor(0, 122, 204, 180)))  # Blue with transparency
    painter.drawRect(6, 24, 20, 6)
    painter.drawRect(6, 22, 8, 2)
    
    painter.end()
    return QIcon(pixmap)

def main():
    app = QApplication(sys.argv)
    
    # Load application icon first
    app_icon = load_application_icon()
    
    # Set application properties
    app.setApplicationName("FileDog")
    app.setApplicationVersion("1.0.0")
    app.setOrganizationName("FileDog")
    app.setApplicationDisplayName("FileDog - File Organizer")
    
    # Set application icon for all operating systems
    app.setWindowIcon(app_icon)
    
    # For Windows: Set the application user model ID to ensure proper taskbar grouping
    import platform
    if platform.system() == "Windows":
        try:
            import ctypes
            # Set application ID for Windows taskbar grouping with custom icon
            ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID("FileDog.FileOrganizer.GUI.1.0")
        except:
            pass  # Ignore if ctypes not available or fails
    
    # Create and show main window
    window = MainWindow()
    window.show()
    
    sys.exit(app.exec())

if __name__ == "__main__":
    main()
