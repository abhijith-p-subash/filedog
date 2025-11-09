import sys
from pathlib import Path
from PySide6.QtWidgets import (
    QApplication, QSystemTrayIcon, QMenu, QMessageBox
)
from PySide6.QtCore import QTimer, Signal, QObject
from PySide6.QtGui import QAction, QIcon, QPixmap, QPainter, QBrush, QColor
from .main_window import MainWindow
from core.file_watcher import FileWatcherService

class TrayApplication(QObject):
    """System tray application for FileDog with background monitoring"""
    
    def __init__(self):
        super().__init__()
        
        # Initialize services
        self.watcher_service = FileWatcherService(logger=self.log_to_tray)
        self.main_window = None
        self.is_organizing_paused = False
        
        # Setup tray icon
        self.setup_tray_icon()
        
        # Setup background monitoring
        self.setup_background_monitoring()
        
        # Show initial notification
        self.show_tray_message("FileDog Started", 
                             "FileDog is now monitoring your directories in the background.")

    def create_icon(self):
        """Load the FileDog icon"""
        # Try to load the existing icon files
        icon_paths = [
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
                    print(f"Failed to load icon from {icon_path}: {e}")
        
        # Fallback: create a simple programmatic icon if no files found
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

    def setup_tray_icon(self):
        """Setup the system tray icon and menu"""
        if not QSystemTrayIcon.isSystemTrayAvailable():
            QMessageBox.critical(None, "FileDog", 
                               "System tray is not available on this system.")
            sys.exit(1)
        
        # Create tray icon
        self.tray_icon = QSystemTrayIcon()
        self.tray_icon.setIcon(self.create_icon())
        self.tray_icon.setToolTip("FileDog - File Organizer")
        
        # Create tray menu
        self.tray_menu = QMenu()
        
        # Show main window action
        show_action = QAction("Show FileDog", self)
        show_action.triggered.connect(self.show_main_window)
        self.tray_menu.addAction(show_action)
        
        self.tray_menu.addSeparator()
        
        # Pause/Resume organizing
        self.pause_action = QAction("Pause Organizing", self)
        self.pause_action.triggered.connect(self.toggle_organizing)
        self.tray_menu.addAction(self.pause_action)
        
        # Status action (read-only)
        self.status_action = QAction("Status: Starting...", self)
        self.status_action.setEnabled(False)
        self.tray_menu.addAction(self.status_action)
        
        self.tray_menu.addSeparator()
        
        # Quit action
        quit_action = QAction("Quit FileDog", self)
        quit_action.triggered.connect(self.quit_application)
        self.tray_menu.addAction(quit_action)
        
        # Set menu and show tray icon
        self.tray_icon.setContextMenu(self.tray_menu)
        self.tray_icon.activated.connect(self.tray_icon_activated)
        self.tray_icon.show()

    def setup_background_monitoring(self):
        """Setup background file monitoring"""
        # Start file watcher if enabled
        if self.watcher_service.is_watcher_enabled():
            self.watcher_service.start_watching()
        
        # Setup status update timer
        self.status_timer = QTimer()
        self.status_timer.timeout.connect(self.update_status)
        self.status_timer.start(5000)  # Update every 5 seconds

    def log_to_tray(self, message):
        """Log messages to system tray notifications"""
        # Only show important messages in tray
        if any(keyword in message.lower() for keyword in 
               ['auto-organizing', 'successfully processed', 'error', 'failed']):
            # Extract just the filename for cleaner notifications
            if 'auto-organizing:' in message:
                filename = message.split('auto-organizing:')[-1].strip()
                self.show_tray_message("File Organized", f"Organized: {filename}")
            elif 'error' in message.lower() or 'failed' in message.lower():
                self.show_tray_message("FileDog Error", message)

    def show_tray_message(self, title, message, icon=QSystemTrayIcon.MessageIcon.Information):
        """Show system tray notification"""
        if self.tray_icon.supportsMessages():
            self.tray_icon.showMessage(title, message, icon, 3000)

    def tray_icon_activated(self, reason):
        """Handle tray icon activation"""
        if reason == QSystemTrayIcon.ActivationReason.DoubleClick:
            self.show_main_window()

    def show_main_window(self):
        """Show the main FileDog window"""
        if self.main_window is None:
            self.main_window = MainWindow()
        
        self.main_window.show()
        self.main_window.raise_()
        self.main_window.activateWindow()

    def toggle_organizing(self):
        """Toggle pause/resume organizing"""
        if self.is_organizing_paused:
            # Resume organizing
            if self.watcher_service.is_watcher_enabled():
                self.watcher_service.start_watching()
            self.is_organizing_paused = False
            self.pause_action.setText("Pause Organizing")
            self.show_tray_message("FileDog Resumed", "File organizing has been resumed.")
        else:
            # Pause organizing
            if self.watcher_service.is_running:
                self.watcher_service.stop_watching()
            self.is_organizing_paused = True
            self.pause_action.setText("Resume Organizing")
            self.show_tray_message("FileDog Paused", "File organizing has been paused.")

    def update_status(self):
        """Update the status in tray menu"""
        status = self.watcher_service.get_status()
        
        if self.is_organizing_paused:
            status_text = "Status: Paused"
        elif status["is_running"]:
            status_text = f"Status: Active ({status['active_watches']} dirs)"
        elif status["is_enabled"]:
            dirs_count = len(status['watched_directories'])
            status_text = f"Status: Ready ({dirs_count} dirs configured)"
        else:
            status_text = "Status: Disabled"
        
        self.status_action.setText(status_text)
        
        # Update tooltip
        tooltip = f"FileDog - {status_text}"
        self.tray_icon.setToolTip(tooltip)

    def quit_application(self):
        """Quit the FileDog application"""
        # Stop file watcher
        if self.watcher_service and self.watcher_service.is_running:
            self.watcher_service.stop_watching()
        
        # Close main window if open
        if self.main_window:
            self.main_window.close()
        
        # Hide tray icon
        self.tray_icon.hide()
        
        # Show goodbye message
        self.show_tray_message("FileDog", "FileDog has been stopped.")
        
        # Quit application
        QApplication.quit()

class FileDogTrayApp:
    """Main application class that manages the tray application"""
    
    def __init__(self):
        # Create QApplication
        self.app = QApplication.instance()
        if self.app is None:
            self.app = QApplication(sys.argv)
        
        # Load application icon first
        app_icon = self.load_application_icon()
        
        # Set application properties
        self.app.setApplicationName("FileDog")
        self.app.setApplicationVersion("1.0.0")
        self.app.setOrganizationName("FileDog")
        self.app.setApplicationDisplayName("FileDog - File Organizer")
        
        # Set application icon globally for all OS (taskbar, dock, etc.)
        self.app.setWindowIcon(app_icon)
        
        # For Windows: Set the application user model ID to ensure proper taskbar grouping
        import platform
        if platform.system() == "Windows":
            try:
                import ctypes
                # Set application ID for Windows taskbar grouping
                ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID("FileDog.FileOrganizer.1.0")
            except:
                pass  # Ignore if ctypes not available or fails
        
        # Prevent app from quitting when last window is closed
        self.app.setQuitOnLastWindowClosed(False)
        
        # Create tray application
        self.tray_app = TrayApplication()

    def load_application_icon(self):
        """Load the application icon for taskbar display"""
        # Try to load the existing icon files
        icon_paths = [
            Path("assets/filedog.ico"),
            Path("assets/filedog.svg"),
            Path("assets/filedog_32x32.png"),
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

    def run(self):
        """Run the application"""
        return self.app.exec()

def main():
    """Entry point for tray application"""
    try:
        app = FileDogTrayApp()
        return app.run()
    except Exception as e:
        print(f"Error starting FileDog: {e}")
        return 1

if __name__ == "__main__":
    sys.exit(main())
