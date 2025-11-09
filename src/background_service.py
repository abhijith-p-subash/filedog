#!/usr/bin/env python3
"""
FileDog Background Service
Runs the file watcher service in the background to monitor directories
even when the main GUI application is not running.
"""

import sys
import time
import signal
import threading
from pathlib import Path
from core.file_watcher import FileWatcherService

class BackgroundService:
    """Background service for file watching"""
    
    def __init__(self):
        self.watcher_service = None
        self.running = False
        self.stop_event = threading.Event()

    def log(self, message):
        """Log messages with timestamp"""
        timestamp = time.strftime("%Y-%m-%d %H:%M:%S")
        print(f"[{timestamp}] {message}")

    def signal_handler(self, signum, frame):
        """Handle shutdown signals"""
        self.log(f"Received signal {signum}, shutting down...")
        self.stop()

    def start(self):
        """Start the background service"""
        self.log("Starting FileDog Background Service...")
        
        # Setup signal handlers for graceful shutdown
        signal.signal(signal.SIGINT, self.signal_handler)
        signal.signal(signal.SIGTERM, self.signal_handler)
        
        # Initialize watcher service
        self.watcher_service = FileWatcherService(logger=self.log)
        
        # Check if watcher is enabled
        if not self.watcher_service.is_watcher_enabled():
            self.log("File watcher is disabled in configuration. Enable it through the GUI first.")
            return False
        
        # Get watched directories
        watched_dirs = self.watcher_service.get_watched_directories()
        if not watched_dirs:
            self.log("No directories configured for watching. Add directories through the GUI first.")
            return False
        
        self.log(f"Configured to watch {len(watched_dirs)} directories:")
        for directory in watched_dirs:
            self.log(f"  - {directory}")
        
        # Start the watcher
        if self.watcher_service.start_watching():
            self.running = True
            self.log("Background service started successfully!")
            self.log("Press Ctrl+C to stop the service")
            
            # Keep the service running
            try:
                while self.running and not self.stop_event.is_set():
                    time.sleep(1)
            except KeyboardInterrupt:
                self.log("Keyboard interrupt received")
            
            self.stop()
            return True
        else:
            self.log("Failed to start file watching service")
            return False

    def stop(self):
        """Stop the background service"""
        if not self.running:
            return
        
        self.log("Stopping background service...")
        self.running = False
        self.stop_event.set()
        
        if self.watcher_service:
            self.watcher_service.stop_watching()
        
        self.log("Background service stopped")

    def status(self):
        """Show service status"""
        watcher_service = FileWatcherService()
        status = watcher_service.get_status()
        
        print("FileDog Background Service Status:")
        print(f"  Enabled: {'Yes' if status['is_enabled'] else 'No'}")
        print(f"  Running: {'Yes' if status['is_running'] else 'No'}")
        print(f"  Watched Directories: {len(status['watched_directories'])}")
        print(f"  Active Watches: {status['active_watches']}")
        
        if status['watched_directories']:
            print("\nWatched Directories:")
            for directory in status['watched_directories']:
                exists = "✓" if Path(directory).exists() else "✗"
                print(f"  {exists} {directory}")

def main():
    """Main entry point for background service"""
    import argparse
    
    parser = argparse.ArgumentParser(
        description="FileDog Background Service - File Watcher",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s start          # Start the background service
  %(prog)s status         # Show service status
  %(prog)s --help         # Show this help message

The service will monitor configured directories and automatically
organize files when they are added. Configure directories and
enable the watcher using the main FileDog GUI application first.
        """
    )
    
    parser.add_argument(
        'command',
        choices=['start', 'status'],
        help='Command to execute'
    )
    
    parser.add_argument(
        '--version',
        action='version',
        version='FileDog Background Service v1.0.0'
    )
    
    args = parser.parse_args()
    
    service = BackgroundService()
    
    if args.command == 'start':
        try:
            success = service.start()
            sys.exit(0 if success else 1)
        except Exception as e:
            print(f"Error starting service: {e}")
            sys.exit(1)
    
    elif args.command == 'status':
        try:
            service.status()
            sys.exit(0)
        except Exception as e:
            print(f"Error getting status: {e}")
            sys.exit(1)

if __name__ == "__main__":
    main()
