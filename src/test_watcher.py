#!/usr/bin/env python3
"""
Test script for the file watcher functionality
"""

import time
from pathlib import Path
from core.file_watcher import FileWatcherService

def test_watcher():
    """Test the file watcher functionality"""
    print("Testing File Watcher Service...")
    
    # Create a test directory
    test_dir = Path.home() / "filedog_test"
    test_dir.mkdir(exist_ok=True)
    print(f"Created test directory: {test_dir}")
    
    # Initialize watcher service
    def log_message(msg):
        print(f"[WATCHER] {msg}")
    
    watcher = FileWatcherService(logger=log_message)
    
    # Add test directory to watch list
    print(f"Adding {test_dir} to watch list...")
    success = watcher.add_watched_directory(str(test_dir))
    print(f"Add directory result: {success}")
    
    # Enable watcher
    print("Enabling watcher...")
    watcher.set_watcher_enabled(True)
    
    # Get status
    status = watcher.get_status()
    print(f"Watcher status: {status}")
    
    # Start watching
    print("Starting file watcher...")
    start_success = watcher.start_watching()
    print(f"Start watcher result: {start_success}")
    
    if start_success:
        print("File watcher is now active!")
        print(f"Try creating a file in: {test_dir}")
        print("The file should be automatically organized.")
        print("Press Ctrl+C to stop the test...")
        
        try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            print("\nStopping watcher...")
            watcher.stop_watching()
            print("Test completed!")
    else:
        print("Failed to start watcher")
    
    # Clean up - remove test directory from watch list
    print("Cleaning up...")
    watcher.remove_watched_directory(str(test_dir))
    watcher.set_watcher_enabled(False)

if __name__ == "__main__":
    test_watcher()
