import sys
from pathlib import Path
from PySide6.QtWidgets import QApplication
from PySide6.QtGui import QIcon, QPixmap, QPainter, QBrush, QColor
from ui.main_window import MainWindow
import platform

def load_application_icon():
    """Load the application icon for the QApplication"""
    
    # Platform-specific icon preference
    if platform.system() == "Darwin":  # macOS
        # Prioritize .icns for macOS
        mac_icon_paths = [
            Path("assets/filedog.icns"),
            Path("../assets/filedog.icns"),
            Path("filedog.icns"),
        ]
        for icon_path in mac_icon_paths:
            if icon_path.exists():
                try:
                    icon = QIcon(str(icon_path))
                    if not icon.isNull():
                        # Verify the icon has high-res versions
                        sizes = icon.availableSizes()
                        print(f"Loaded icon from {icon_path} with sizes: {sizes}")
                        return icon
                except Exception as e:
                    print(f"Failed to load app icon from {icon_path}: {e}")
    
    # Try to load other formats (SVG is best for cross-platform)
    icon_paths = [
        Path("assets/filedog.svg"),
        Path("../assets/filedog.svg"),
        Path("filedog.svg"),
        Path("assets/filedog_24x24.png"),
        Path("../assets/filedog_24x24.png"),
        Path("filedog.ico"),
        Path("../filedog.ico"),
    ]
    
    for icon_path in icon_paths:
        if icon_path.exists():
            try:
                icon = QIcon(str(icon_path))
                if not icon.isNull():
                    print(f"Loaded icon from {icon_path}")
                    return icon
            except Exception as e:
                print(f"Failed to load app icon from {icon_path}: {e}")
    
    # Fallback: create a simple programmatic icon
    return create_fallback_icon()

def create_fallback_icon():
    """Create a programmatic fallback icon"""
    # Create multiple sizes for better scaling
    icon = QIcon()
    for size in [16, 32, 64, 128, 256, 512]:
        pixmap = create_icon_pixmap(size)
        icon.addPixmap(pixmap)
    return icon

def create_icon_pixmap(size):
    """Create a single pixmap of the specified size"""
    pixmap = QPixmap(size, size)
    pixmap.fill(QColor(0, 0, 0, 0))  # Transparent background
    
    painter = QPainter(pixmap)
    painter.setRenderHint(QPainter.RenderHint.Antialiasing)
    
    # Scale proportionally
    scale = size / 32.0
    
    # Draw dog face
    painter.setBrush(QBrush(QColor(217, 158, 130)))
    painter.setPen(QColor(217, 158, 130))
    painter.drawEllipse(int(4*scale), int(8*scale), int(24*scale), int(20*scale))
    
    # Draw ears
    painter.setBrush(QBrush(QColor(102, 33, 19)))
    painter.drawEllipse(int(2*scale), int(6*scale), int(8*scale), int(8*scale))
    painter.drawEllipse(int(22*scale), int(6*scale), int(8*scale), int(8*scale))
    
    # Draw folder element
    painter.setBrush(QBrush(QColor(0, 122, 204, 180)))
    painter.drawRect(int(6*scale), int(24*scale), int(20*scale), int(6*scale))
    painter.drawRect(int(6*scale), int(22*scale), int(8*scale), int(2*scale))
    
    painter.end()
    return pixmap

def main():
    app = QApplication(sys.argv)
    
    # Load application icon first
    # Use SVG for perfect scaling on all displays
    svg_path = Path("assets/filedog.svg")
    if svg_path.exists():
        app_icon = QIcon(str(svg_path))
        print(f"✓ Using SVG icon: {svg_path}")
    else:
        app_icon = load_application_icon()
    # app_icon = load_application_icon()
    # # app_icon = QIcon("assets/filedog.svg")
    
    # Set application properties
    app.setApplicationName("FileDog")
    app.setApplicationVersion("1.0.0")
    app.setOrganizationName("FileDog")
    app.setApplicationDisplayName("FileDog - File Organizer")
    
    # Set application icon for all operating systems
    app.setWindowIcon(app_icon)
    
    # Platform-specific setup
    if platform.system() == "Windows":
        try:
            import ctypes
            ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(
                "FileDog.FileOrganizer.GUI.1.0"
            )
        except:
            pass
    
    # Create and show main window
    window = MainWindow()
    window.show()
    
    sys.exit(app.exec())

if __name__ == "__main__":
    main()