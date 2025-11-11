from PySide6.QtWidgets import (
    QMainWindow,
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QPushButton,
    QProgressBar,
    QFileDialog,
    QLabel,
    QListWidget,
    QListWidgetItem,
    QGroupBox,
    QCheckBox,
    QMessageBox,
    QTabWidget,
    QMenuBar,
    QStatusBar,
    QFrame,
    QSizePolicy,
    QSpacerItem,
    QSystemTrayIcon,
    QMenu
)
from PySide6.QtCore import Qt, QThread, Signal, QTimer
from PySide6.QtGui import QAction, QFont, QIcon, QPixmap, QPainter, QBrush, QColor
from pathlib import Path
from core.organizer import FileOrganizer
from core.file_watcher import FileWatcherService

class OrganizerThread(QThread):
    progress_signal = Signal(int)
    finished_signal = Signal(str)
    error_signal = Signal(str)

    def __init__(self, folder_path):
        super().__init__()
        self.folder_path = Path(folder_path)
        self.organizer = FileOrganizer()

    def run(self):
        try:
            self.organizer.organize(self.folder_path)
            self.progress_signal.emit(100)
            self.finished_signal.emit("Organization completed successfully")
        except Exception as e:
            self.error_signal.emit(f"Error: {str(e)}")

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("FileDog - File Organizer")
        self.setMinimumSize(800, 600)
        self.resize(900, 650)
        
        # Set window icon
        self.setWindowIcon(self.load_icon())
        
        # Initialize services
        self.watcher_service = FileWatcherService()
        self.folder_path = Path.home() / 'Downloads'
        self.thread = None
        
        # Tray icon management
        self.tray_icon = None
        self.is_tray_active = False
        
        # Setup UI components
        self.setup_menu_bar()
        self.setup_ui()
        self.setup_status_bar()
        
        # Setup timers
        self.status_timer = QTimer()
        self.status_timer.timeout.connect(self.update_watcher_status)
        self.status_timer.start(3000)  # Update every 3 seconds
        
        # Initial updates
        self.update_watcher_status()
        self.load_watched_directories()
        
        # Apply modern styling
        self.apply_styles()

    def load_icon(self):
        """Load the FileDog icon for the main window"""
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
                    print(f"Failed to load window icon from {icon_path}: {e}")
        
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

    def setup_menu_bar(self):
        """Setup the menu bar"""
        menubar = self.menuBar()
        
        # File menu
        file_menu = menubar.addMenu("File")
        
        select_folder_action = QAction("Select Folder...", self)
        select_folder_action.setShortcut("Ctrl+O")
        select_folder_action.triggered.connect(self.select_folder)
        file_menu.addAction(select_folder_action)
        
        file_menu.addSeparator()
        
        exit_action = QAction("Exit", self)
        exit_action.setShortcut("Ctrl+Q")
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)
        
        # Edit menu
        edit_menu = menubar.addMenu("Edit")
        
        preferences_action = QAction("Preferences...", self)
        preferences_action.triggered.connect(self.show_preferences)
        edit_menu.addAction(preferences_action)
        
        # Help menu
        help_menu = menubar.addMenu("Help")
        
        about_action = QAction("About FileDog", self)
        about_action.triggered.connect(self.show_about)
        help_menu.addAction(about_action)
        
        help_action = QAction("Help", self)
        help_action.setShortcut("F1")
        help_action.triggered.connect(self.show_help)
        help_menu.addAction(help_action)

    def setup_ui(self):
        """Setup the main user interface"""
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        main_layout = QVBoxLayout(central_widget)
        main_layout.setSpacing(15)
        main_layout.setContentsMargins(15, 10, 15, 10)
        
        # Create tab widget
        self.tab_widget = QTabWidget()
        self.tab_widget.setTabPosition(QTabWidget.TabPosition.North)
        main_layout.addWidget(self.tab_widget)
        
        # Create tabs
        self.create_organizer_tab()
        self.create_watcher_tab()

    def create_organizer_tab(self):
        """Create the manual file organizer tab"""
        organizer_widget = QWidget()
        layout = QVBoxLayout(organizer_widget)
        layout.setSpacing(20)
        
        # Header
        header_label = QLabel("Manual File Organization")
        header_font = QFont()
        header_font.setPointSize(14)
        header_font.setBold(True)
        header_label.setFont(header_font)
        layout.addWidget(header_label)
        
        # Folder selection group
        folder_group = QGroupBox("Target Folder")
        folder_layout = QVBoxLayout(folder_group)
        
        # Folder display
        folder_container = QHBoxLayout()
        self.folder_label = QLabel(str(self.folder_path))
        self.folder_label.setStyleSheet("QLabel { padding: 6px; background: #2d2d2d; border: 1px solid #3a3a3a; border-radius: 3px; }")
        self.select_btn = QPushButton("Browse...")
        self.select_btn.clicked.connect(self.select_folder)
        self.select_btn.setMaximumWidth(100)
        
        folder_container.addWidget(self.folder_label)
        folder_container.addWidget(self.select_btn)
        folder_layout.addLayout(folder_container)
        
        layout.addWidget(folder_group)
        
        # Progress section
        progress_group = QGroupBox("Progress")
        progress_layout = QVBoxLayout(progress_group)
        
        self.progress = QProgressBar()
        self.progress.setVisible(False)
        progress_layout.addWidget(self.progress)
        
        # Action buttons
        button_layout = QHBoxLayout()
        button_layout.addStretch()
        
        self.start_btn = QPushButton("Organize Files")
        self.start_btn.clicked.connect(self.start_organizing)
        self.start_btn.setMinimumHeight(35)
        self.start_btn.setStyleSheet("""
            QPushButton {
                background-color: #007ACC;
                color: white;
                border: none;
                border-radius: 5px;
                padding: 8px 16px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #005a9e;
            }
            QPushButton:pressed {
                background-color: #004578;
            }
            QPushButton:disabled {
                background-color: #cccccc;
                color: #666666;
            }
        """)
        
        button_layout.addWidget(self.start_btn)
        progress_layout.addLayout(button_layout)
        
        layout.addWidget(progress_group)
        
        # Add stretch to push everything to top
        layout.addStretch()
        
        self.tab_widget.addTab(organizer_widget, "Organize")

    def create_watcher_tab(self):
        """Create the file watcher management tab"""
        watcher_widget = QWidget()
        layout = QVBoxLayout(watcher_widget)
        layout.setSpacing(20)
        
        # Header
        header_label = QLabel("Automatic File Watching")
        header_font = QFont()
        header_font.setPointSize(14)
        header_font.setBold(True)
        header_label.setFont(header_font)
        layout.addWidget(header_label)
        
        # Watcher control
        control_group = QGroupBox("Watcher Control")
        control_layout = QVBoxLayout(control_group)
        
        # Toggle button container
        toggle_container = QHBoxLayout()
        toggle_label = QLabel("Enable automatic file watching")
        toggle_label.setStyleSheet("QLabel { color: #ffffff; font-weight: 500; }")
        
        # Create toggle button
        self.watcher_toggle_btn = QPushButton()
        self.watcher_toggle_btn.setCheckable(True)
        self.watcher_toggle_btn.setChecked(False)
        self.watcher_toggle_btn.setFixedSize(60, 30)
        self.watcher_toggle_btn.clicked.connect(self.toggle_watcher)
        self.update_toggle_button_style()
        
        toggle_container.addWidget(toggle_label)
        toggle_container.addStretch()
        toggle_container.addWidget(self.watcher_toggle_btn)
        control_layout.addLayout(toggle_container)
        
        # Status display
        self.watcher_status_label = QLabel("Status: Checking...")
        self.watcher_status_label.setStyleSheet("QLabel { color: #b3b3b3; font-style: italic; }")
        control_layout.addWidget(self.watcher_status_label)
        
        layout.addWidget(control_group)
        
        # Watched directories management
        directories_group = QGroupBox("Watched Directories")
        directories_layout = QVBoxLayout(directories_group)
        
        # Directory list
        self.watched_dirs_list = QListWidget()
        self.watched_dirs_list.setMaximumHeight(200)
        directories_layout.addWidget(self.watched_dirs_list)
        
        # Directory management buttons
        dir_button_layout = QHBoxLayout()
        
        self.add_dir_btn = QPushButton("Add")
        self.add_dir_btn.clicked.connect(self.add_watched_directory)
        
        self.remove_dir_btn = QPushButton("Remove")
        self.remove_dir_btn.clicked.connect(self.remove_watched_directory)
        
        dir_button_layout.addWidget(self.add_dir_btn)
        dir_button_layout.addWidget(self.remove_dir_btn)
        dir_button_layout.addStretch()
        
        directories_layout.addLayout(dir_button_layout)
        
        layout.addWidget(directories_group)
        
        # Info section
        info_label = QLabel("Files added to watched directories will be automatically organized by type.")
        info_label.setStyleSheet("QLabel { color: #b3b3b3; font-style: italic; }")
        info_label.setWordWrap(True)
        layout.addWidget(info_label)
        
        # Add stretch to push everything to top
        layout.addStretch()
        
        self.tab_widget.addTab(watcher_widget, "Auto Watch")

    def setup_status_bar(self):
        """Setup the status bar"""
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)
        self.status_bar.showMessage("Ready")

    def apply_styles(self):
        """Apply minimal professional dark theme styling"""
        self.setStyleSheet("""
            /* Main Window */
            QMainWindow {
                background-color: #1e1e1e;
                color: #ffffff;
            }
            
            /* Central Widget */
            QWidget {
                background-color: #1e1e1e;
                color: #ffffff;
            }
            
            /* Menu Bar */
            QMenuBar {
                background-color: #1e1e1e;
                color: #ffffff;
                border: none;
                padding: 2px;
            }
            
            QMenuBar::item {
                background-color: transparent;
                padding: 6px 12px;
                border-radius: 3px;
            }
            
            QMenuBar::item:selected {
                background-color: #2d2d2d;
            }
            
            QMenu {
                background-color: #2d2d2d;
                color: #ffffff;
                border: 1px solid #3a3a3a;
                border-radius: 3px;
                padding: 2px;
            }
            
            QMenu::item {
                padding: 6px 16px;
                border-radius: 2px;
                margin: 1px;
            }
            
            QMenu::item:selected {
                background-color: #007ACC;
            }
            
            /* Tab Widget */
            QTabWidget::pane {
                border: none;
                background-color: #1e1e1e;
            }
            
            QTabWidget::tab-bar {
                alignment: left;
            }
            
            QTabBar {
                alignment: left;
            }
            
            QTabBar::tab {
                background-color: #2d2d2d;
                color: #b3b3b3;
                border: none;
                min-width: 100px;
                max-width: 200px;
                padding: 10px 16px;
                margin-right: 1px;
                text-align: left;
            }
            
            QTabBar::tab:selected {
                background-color: #1e1e1e;
                color: #ffffff;
                border-bottom: 2px solid #007ACC;
            }
            
            QTabBar::tab:hover {
                background-color: #353535;
                color: #ffffff;
            }
            
            /* Group Boxes */
            QGroupBox {
                font-weight: 500;
                border: 1px solid #3a3a3a;
                border-radius: 4px;
                margin-top: 8px;
                padding-top: 12px;
                background-color: transparent;
                color: #ffffff;
            }
            
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 12px;
                padding: 0 6px;
                color: #b3b3b3;
                background-color: #1e1e1e;
            }
            
            /* Labels */
            QLabel {
                color: #ffffff;
                background-color: transparent;
            }
            
            /* Buttons */
            QPushButton {
                background-color: #2d2d2d;
                color: #ffffff;
                border: 1px solid #3a3a3a;
                border-radius: 4px;
                padding: 8px 12px;
                min-height: 12px;
                font-weight: 400;
            }
            
            QPushButton:hover {
                background-color: #353535;
                border-color: #4a4a4a;
            }
            
            QPushButton:pressed {
                background-color: #252525;
            }
            
            QPushButton:disabled {
                background-color: #2a2a2a;
                color: #666666;
                border-color: #2a2a2a;
            }
            
            /* Progress Bar */
            QProgressBar {
                border: 1px solid #3a3a3a;
                border-radius: 3px;
                text-align: center;
                background-color: #2d2d2d;
                color: #ffffff;
                font-weight: 400;
                height: 18px;
            }
            
            QProgressBar::chunk {
                background-color: #007ACC;
                border-radius: 2px;
            }
            
            /* List Widget */
            QListWidget {
                border: 1px solid #3a3a3a;
                border-radius: 3px;
                background-color: #2d2d2d;
                color: #ffffff;
                selection-background-color: #007ACC;
                selection-color: #ffffff;
                outline: none;
                padding: 2px;
            }
            
            QListWidget::item {
                padding: 6px;
                border-radius: 2px;
                margin: 0px;
            }
            
            QListWidget::item:hover {
                background-color: #353535;
            }
            
            QListWidget::item:selected {
                background-color: #007ACC;
                color: #ffffff;
            }
            
            /* Modern Checkbox */
            QCheckBox {
                color: #ffffff;
                spacing: 10px;
                font-weight: 400;
            }
            
            QCheckBox::indicator {
                width: 16px;
                height: 16px;
                border-radius: 8px;
            }
            
            QCheckBox::indicator:unchecked {
                border: 2px solid #4a4a4a;
                background-color: #2d2d2d;
            }
            
            QCheckBox::indicator:checked {
                border: 2px solid #007ACC;
                background-color: #007ACC;
                image: url(data:image/svg+xml;base64,PHN2ZyB3aWR0aD0iMTAiIGhlaWdodD0iOCIgdmlld0JveD0iMCAwIDEwIDgiIGZpbGw9Im5vbmUiIHhtbG5zPSJodHRwOi8vd3d3LnczLm9yZy8yMDAwL3N2ZyI+CjxwYXRoIGQ9Ik04LjUgMUwzLjUgNkwxLjUgNCIgc3Ryb2tlPSJ3aGl0ZSIgc3Ryb2tlLXdpZHRoPSIyIiBzdHJva2UtbGluZWNhcD0icm91bmQiIHN0cm9rZS1saW5lam9pbj0icm91bmQiLz4KPC9zdmc+);
            }
            
            QCheckBox::indicator:hover {
                border-color: #007ACC;
            }
            
            QCheckBox::indicator:unchecked:hover {
                background-color: #353535;
            }
            
            /* Status Bar */
            QStatusBar {
                background-color: #1e1e1e;
                color: #b3b3b3;
                border: none;
                padding: 6px;
                font-size: 12px;
            }
            
            /* Scrollbars */
            QScrollBar:vertical {
                border: none;
                background-color: transparent;
                width: 8px;
            }
            
            QScrollBar::handle:vertical {
                background-color: #4a4a4a;
                border-radius: 4px;
                min-height: 20px;
            }
            
            QScrollBar::handle:vertical:hover {
                background-color: #5a5a5a;
            }
            
            QScrollBar::add-line:vertical,
            QScrollBar::sub-line:vertical {
                border: none;
                background: none;
                height: 0px;
            }
        """)

    def select_folder(self):
        """Select folder for manual organization"""
        folder = QFileDialog.getExistingDirectory(self, "Select Folder to Organize", str(self.folder_path))
        if folder:
            self.folder_path = Path(folder)
            self.folder_label.setText(str(self.folder_path))

    def start_organizing(self):
        """Start manual file organization"""
        if not self.folder_path.exists():
            QMessageBox.warning(self, "Error", "Selected folder does not exist.")
            return
        
        self.start_btn.setEnabled(False)
        self.start_btn.setText("Organizing...")
        self.progress.setVisible(True)
        self.progress.setValue(0)
        self.status_bar.showMessage("Organizing files...")
        
        self.thread = OrganizerThread(self.folder_path)
        self.thread.progress_signal.connect(self.progress.setValue)
        self.thread.finished_signal.connect(self.on_organization_finished)
        self.thread.error_signal.connect(self.on_organization_error)
        self.thread.start()

    def on_organization_finished(self, message):
        """Handle organization completion"""
        self.start_btn.setEnabled(True)
        self.start_btn.setText("Organize Files")
        self.progress.setVisible(False)
        self.status_bar.showMessage(message, 5000)
        QMessageBox.information(self, "Success", message)

    def on_organization_error(self, error_message):
        """Handle organization error"""
        self.start_btn.setEnabled(True)
        self.start_btn.setText("Organize Files")
        self.progress.setVisible(False)
        self.status_bar.showMessage("Organization failed", 5000)
        QMessageBox.critical(self, "Error", error_message)

    def update_toggle_button_style(self):
        """Update toggle button appearance based on its state and enabled status"""
        if not self.watcher_toggle_btn.isEnabled():
            # Disabled state - very light gray
            self.watcher_toggle_btn.setStyleSheet("""
                QPushButton {
                    background-color: #404040;
                    border: 2px solid #353535;
                    border-radius: 15px;
                    color: #888888;
                    font-weight: bold;
                    font-size: 11px;
                }
                QPushButton:disabled {
                    background-color: #404040;
                    border: 2px solid #353535;
                    color: #888888;
                }
            """)
            self.watcher_toggle_btn.setText("OFF")
        elif self.watcher_toggle_btn.isChecked():
            # ON state - green
            self.watcher_toggle_btn.setStyleSheet("""
                QPushButton {
                    background-color: #4CAF50;
                    border: 2px solid #45a049;
                    border-radius: 15px;
                    color: white;
                    font-weight: bold;
                    font-size: 11px;
                }
                QPushButton:hover {
                    background-color: #45a049;
                }
            """)
            self.watcher_toggle_btn.setText("ON")
        else:
            # OFF state - gray
            self.watcher_toggle_btn.setStyleSheet("""
                QPushButton {
                    background-color: #666666;
                    border: 2px solid #555555;
                    border-radius: 15px;
                    color: white;
                    font-weight: bold;
                    font-size: 11px;
                }
                QPushButton:hover {
                    background-color: #555555;
                }
            """)
            self.watcher_toggle_btn.setText("OFF")

    def should_activate_tray(self):
        """Check if tray should be activated based on conditions"""
        try:
            status = self.watcher_service.get_status()
            directories = self.watcher_service.get_watched_directories()
            
            # Activate tray only if auto-organizing is enabled AND directories are configured
            return status["is_enabled"] and len(directories) > 0
        except Exception:
            return False

    def setup_tray_icon(self):
        """Setup system tray icon and menu"""
        if not QSystemTrayIcon.isSystemTrayAvailable():
            print("System tray is not available on this system")
            return False
        
        try:
            # Create tray icon
            self.tray_icon = QSystemTrayIcon(self)
            self.tray_icon.setIcon(self.windowIcon())
            self.tray_icon.setToolTip("FileDog - File Organizer (Background Mode)")
            
            # Create tray menu
            tray_menu = QMenu()
            
            # Show main window action
            show_action = QAction("Show FileDog", self)
            show_action.triggered.connect(self.show_and_raise)
            tray_menu.addAction(show_action)
            
            tray_menu.addSeparator()
            
            # Status action (read-only)
            self.tray_status_action = QAction("Status: Active", self)
            self.tray_status_action.setEnabled(False)
            tray_menu.addAction(self.tray_status_action)
            
            tray_menu.addSeparator()
            
            # Quit action
            quit_action = QAction("Quit FileDog", self)
            quit_action.triggered.connect(self.quit_application)
            tray_menu.addAction(quit_action)
            
            # Set menu and connect signals
            self.tray_icon.setContextMenu(tray_menu)
            self.tray_icon.activated.connect(self.tray_icon_activated)
            
            return True
        except Exception as e:
            print(f"Failed to create tray icon: {e}")
            return False

    def activate_tray(self):
        """Activate system tray for background monitoring"""
        if not self.is_tray_active:
            if self.setup_tray_icon():
                self.tray_icon.show()
                self.is_tray_active = True
                self.tray_icon.showMessage(
                    "FileDog Background Mode",
                    "FileDog is now running in the background and monitoring your directories.",
                    QSystemTrayIcon.MessageIcon.Information,
                    3000
                )
                print("✅ System tray activated - FileDog running in background")
                return True
            else:
                print("❌ Failed to activate system tray")
                return False
        return True

    def deactivate_tray(self):
        """Deactivate system tray"""
        if self.is_tray_active and self.tray_icon:
            self.tray_icon.hide()
            self.tray_icon = None
            self.is_tray_active = False
            print("🔸 System tray deactivated")

    def tray_icon_activated(self, reason):
        """Handle tray icon activation"""
        if reason == QSystemTrayIcon.ActivationReason.DoubleClick:
            self.show_and_raise()

    def show_and_raise(self):
        """Show and raise the main window"""
        self.show()
        self.raise_()
        self.activateWindow()

    def quit_application(self):
        """Quit the entire application from tray menu"""
        self.quit_application_completely()

    def toggle_watcher(self, enabled):
        """Toggle file watcher on/off and manage tray activation"""
        try:
            self.watcher_service.set_watcher_enabled(enabled)
            self.update_toggle_button_style()
            
            # Check if tray should be activated/deactivated
            if self.should_activate_tray():
                self.activate_tray()
                if enabled:
                    self.status_bar.showMessage("File watcher enabled - Background monitoring active", 3000)
            else:
                self.deactivate_tray()
                if enabled:
                    self.status_bar.showMessage("File watcher enabled - Add directories to activate background monitoring", 3000)
                else:
                    self.status_bar.showMessage("File watcher disabled", 3000)
            
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to toggle watcher: {str(e)}")
            self.watcher_toggle_btn.setChecked(not enabled)
            self.update_toggle_button_style()

    def add_watched_directory(self):
        """Add a new directory to watch and check tray activation"""
        directory = QFileDialog.getExistingDirectory(
            self, 
            "Select Directory to Watch", 
            str(Path.home())
        )
        if directory:
            success = self.watcher_service.add_watched_directory(directory)
            if success:
                self.load_watched_directories()
                self.status_bar.showMessage(f"Added directory: {Path(directory).name}", 3000)
                
                # Check if tray should be activated now that a directory is added
                if self.should_activate_tray():
                    self.activate_tray()
                    self.status_bar.showMessage(f"Added directory: {Path(directory).name} - Background monitoring activated", 3000)
            else:
                QMessageBox.warning(
                    self, 
                    "Error", 
                    "Could not add directory to watch list.\nDirectory may already be watched or invalid."
                )

    def remove_watched_directory(self):
        """Remove selected directory from watch list and check tray deactivation"""
        current_item = self.watched_dirs_list.currentItem()
        if current_item:
            directory = current_item.text()
            reply = QMessageBox.question(
                self,
                "Remove Directory",
                f"Remove directory from watch list?\n\n{directory}",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
            )
            
            if reply == QMessageBox.StandardButton.Yes:
                success = self.watcher_service.remove_watched_directory(directory)
                if success:
                    self.load_watched_directories()
                    self.status_bar.showMessage(f"Removed directory: {Path(directory).name}", 3000)
                    
                    # Check if tray should be deactivated if no directories remain
                    if not self.should_activate_tray():
                        self.deactivate_tray()
                        self.status_bar.showMessage(f"Removed directory: {Path(directory).name} - Background monitoring deactivated", 3000)
                else:
                    QMessageBox.warning(self, "Error", "Could not remove directory from watch list.")
        else:
            QMessageBox.information(self, "No Selection", "Please select a directory to remove.")

    def load_watched_directories(self):
        """Load and display watched directories and update toggle button state"""
        self.watched_dirs_list.clear()
        directories = self.watcher_service.get_watched_directories()
        for directory in directories:
            item = QListWidgetItem(directory)
            if not Path(directory).exists():
                item.setForeground(Qt.GlobalColor.red)
                item.setToolTip("Directory no longer exists")
            self.watched_dirs_list.addItem(item)
        
        # Enable/disable toggle button based on directory availability
        self.update_toggle_button_availability()
    
    def update_toggle_button_availability(self):
        """Enable or disable the toggle button based on directory availability"""
        directories = self.watcher_service.get_watched_directories()
        has_directories = len(directories) > 0
        
        # Block signals to prevent triggering toggle_watcher
        self.watcher_toggle_btn.blockSignals(True)
        
        if has_directories:
            # Enable toggle button
            self.watcher_toggle_btn.setEnabled(True)
            self.watcher_toggle_btn.setToolTip("Toggle automatic file watching")
        else:
            # Disable toggle button and ensure it's OFF
            self.watcher_toggle_btn.setEnabled(False)
            self.watcher_toggle_btn.setChecked(False)
            self.watcher_toggle_btn.setToolTip("Add directories first to enable automatic file watching")
            
            # If auto-watch was enabled but no directories, disable it
            if self.watcher_service.get_status()["is_enabled"]:
                self.watcher_service.set_watcher_enabled(False)
                self.deactivate_tray()
        
        # Update button style and unblock signals
        self.update_toggle_button_style()
        self.watcher_toggle_btn.blockSignals(False)

    def update_watcher_status(self):
        """Update watcher status display"""
        try:
            status = self.watcher_service.get_status()
            
            # Update toggle button without triggering signal
            self.watcher_toggle_btn.blockSignals(True)
            self.watcher_toggle_btn.setChecked(status["is_enabled"])
            self.update_toggle_button_style()
            self.watcher_toggle_btn.blockSignals(False)
            
            # Update status text
            if status["is_running"]:
                status_text = f"Active - Watching {status['active_watches']} directories"
            elif status["is_enabled"]:
                status_text = f"Enabled - {len(status['watched_directories'])} directories configured"
            else:
                status_text = "Disabled"
            
            self.watcher_status_label.setText(f"Status: {status_text}")
            
        except Exception as e:
            self.watcher_status_label.setText(f"Status: Error - {str(e)}")

    def show_preferences(self):
        """Show preferences dialog"""
        QMessageBox.information(self, "Preferences", "Preferences dialog will be implemented in a future version.")

    def show_about(self):
        """Show about dialog"""
        about_text = """
        <h2>FileDog</h2>
        <p><b>Version:</b> 1.0.0</p>
        <p><b>A cross-platform file organizer</b></p>
        <p>FileDog automatically organizes your files by type, making it easy to keep your folders clean and organized.</p>
        <p><b>Features:</b></p>
        <ul>
        <li>Manual file organization</li>
        <li>Automatic file watching</li>
        <li>Cross-platform support</li>
        <li>Customizable file type mappings</li>
        </ul>
        <p><b>Author:</b> Abhijith P Subash</p>
        """
        QMessageBox.about(self, "About FileDog", about_text)

    def show_help(self):
        """Show help dialog"""
        help_text = """
        <h3>How to use FileDog:</h3>
        
        <h4>Manual Organization:</h4>
        <p>1. Select a folder using "Browse..." or File → Select Folder</p>
        <p>2. Click "Organize Files" to sort all files by type</p>
        
        <h4>Automatic Watching:</h4>
        <p>1. Go to the "Auto Watch" tab</p>
        <p>2. Add directories you want to monitor</p>
        <p>3. Enable automatic file watching</p>
        <p>4. Files added to watched directories will be organized automatically</p>
        
        <h4>File Types:</h4>
        <p>Files are organized into folders based on their type:</p>
        <p>• Images → Images/</p>
        <p>• Videos → Videos/</p>
        <p>• Documents → PDFs/, WordDocs/, etc.</p>
        <p>• Code → Python/, JavaScript/, etc.</p>
        <p>• And many more...</p>
        
        <h4>Tips:</h4>
        <p>• The file watcher works in the background</p>
        <p>• Files are processed with a delay to ensure they're fully downloaded</p>
        <p>• Duplicate filenames are handled automatically</p>
        """
        QMessageBox.information(self, "Help", help_text)

    def closeEvent(self, event):
        """Handle application close event - hide to tray if auto-watch is active"""
        # If tray is active (auto-watch enabled with directories), hide to tray instead of closing
        if self.is_tray_active:
            self.hide()
            self.tray_icon.showMessage(
                "FileDog Hidden",
                "FileDog continues running in the background. Right-click the tray icon to access options.",
                QSystemTrayIcon.MessageIcon.Information,
                3000
            )
            event.ignore()  # Don't actually close the application
            return
        
        # Otherwise, normal shutdown process
        self.quit_application_completely()
        event.accept()
    
    def quit_application_completely(self):
        """Completely quit the application and all background processes"""
        # Stop file watcher
        if self.watcher_service and self.watcher_service.is_running:
            self.watcher_service.stop_watching()
        
        # Stop organizer thread if running
        if self.thread and self.thread.isRunning():
            self.thread.quit()
            self.thread.wait()
        
        # Hide and cleanup tray icon
        self.deactivate_tray()
        
        # Quit the application
        from PySide6.QtWidgets import QApplication
        QApplication.quit()
