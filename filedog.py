#!/usr/bin/env python3
"""
FileDog - Cross-Platform File Organizer
Main launcher script that provides both GUI and CLI functionality
"""

import sys
import os
from pathlib import Path

# Add src directory to path so we can import modules
src_path = Path(__file__).parent / "src"
sys.path.insert(0, str(src_path))

def main():
    """Main entry point"""
    if len(sys.argv) > 1:
        command = sys.argv[1].lower()
        
        if command in ['gui', 'app', 'ui']:
            # Launch GUI application
            try:
                from src.main import main as gui_main
                gui_main()
            except Exception as e:
                print(f"❌ Error launching GUI: {e}")
                print("   The GUI may not be available on this system")
                print("   Try using CLI mode instead: python filedog.py cli --help")
                sys.exit(1)
                
        elif command in ['tray', 'background', 'daemon']:
            # Launch system tray application
            try:
                from src.ui.tray_application import main as tray_main
                sys.exit(tray_main())
            except Exception as e:
                print(f"❌ Error launching tray application: {e}")
                print("   System tray may not be available on this system")
                sys.exit(1)
                
        elif command in ['cli', 'organize']:
            # Launch CLI organizer
            sys.argv = ['cli.py'] + sys.argv[2:]  # Remove 'cli' from args
            from src.cli import main as cli_main
            cli_main()
            
        elif command in ['service']:
            # Launch background service (console)
            sys.argv = ['background_service.py'] + sys.argv[2:]  # Remove 'service' from args  
            from src.background_service import main as service_main
            service_main()
            
        elif command in ['test']:
            # Run test
            from src.test_watcher import test_watcher
            test_watcher()
            
        elif command in ['help', '--help', '-h']:
            show_help()
            
        else:
            print(f"❌ Unknown command: {command}")
            show_help()
            sys.exit(1)
    else:
        # Default to tray application for seamless background monitoring
        try:
            from src.ui.tray_application import main as tray_main
            sys.exit(tray_main())
        except Exception as e:
            # Fallback to GUI if tray is not available
            try:
                from src.main import main as gui_main
                gui_main()
            except Exception as gui_error:
                print(f"❌ Error launching applications:")
                print(f"   Tray: {e}")
                print(f"   GUI: {gui_error}")
                print("\n📋 Available commands:")
                show_help()
                sys.exit(1)

def show_help():
    """Show help information"""
    print("""
FileDog - Cross-Platform File Organizer v1.0.0

Usage:
    python filedog.py [command] [options]

Commands:
    (default)             Launch system tray application (background monitoring)
    gui, app, ui          Launch the GUI application window
    tray, background      Launch system tray application explicitly
    cli, organize         Use command-line interface for organizing files
    service               Run console background service  
    test                  Test file watcher functionality
    help                  Show this help message

Examples:
    python filedog.py                           # Launch tray app (background)
    python filedog.py tray                      # Launch tray app explicitly
    python filedog.py gui                       # Launch GUI window
    python filedog.py cli /path/to/organize     # Organize files via CLI
    python filedog.py service start            # Start console service
    python filedog.py service status           # Check service status
    python filedog.py test                     # Test file watcher

System Tray Features:
    • Right-click tray icon for menu
    • Double-click tray icon to open GUI
    • Pause/Resume organizing from tray
    • Real-time notifications for organized files
    • Continues monitoring even when GUI is closed

For detailed help on specific commands:
    python filedog.py cli --help               # CLI help
    python filedog.py service --help           # Service help

Features:
    • System tray integration with background monitoring
    • Manual file organization by MIME type
    • Automatic file watching and organization
    • Cross-platform support (Windows, macOS, Linux)
    • Persistent background monitoring
    • Customizable file type configurations
    """)

if __name__ == "__main__":
    main()
