import json
import os
import time
import threading
from pathlib import Path
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
from .organizer import FileOrganizer

class FileOrganizerHandler(FileSystemEventHandler):
    """Handler for file system events that organizes files automatically"""
    
    def __init__(self, logger=None):
        super().__init__()
        self.organizer = FileOrganizer(logger=logger)
        self.logger = logger or print
        # Add a small delay to avoid organizing files that are still being written
        self.processing_delay = 2.0
        self.pending_files = {}
        self.timer_lock = threading.Lock()

    def log(self, message):
        if self.logger:
            self.logger(message)

    def on_created(self, event):
        """Handle file creation events"""
        if not event.is_directory:
            self.log(f"🔍 New file detected: {event.src_path}")
            self._schedule_file_processing(event.src_path)

    def on_moved(self, event):
        """Handle file move events (like download completion)"""
        if not event.is_directory:
            self.log(f"📁 File moved: {event.dest_path}")
            self._schedule_file_processing(event.dest_path)

    def _schedule_file_processing(self, file_path):
        """Schedule file processing with a delay to ensure file is completely written"""
        with self.timer_lock:
            # Cancel any existing timer for this file
            if file_path in self.pending_files:
                self.pending_files[file_path].cancel()
            
            # Schedule new processing
            timer = threading.Timer(self.processing_delay, self._process_file, args=[file_path])
            self.pending_files[file_path] = timer
            timer.start()
            self.log(f"⏱️ Scheduled processing for: {Path(file_path).name}")

    def _process_file(self, file_path):
        """Process a single file"""
        try:
            file_path_obj = Path(file_path)
            if file_path_obj.exists() and file_path_obj.is_file():
                self.log(f"🚀 Auto-organizing: {file_path_obj.name}")
                
                # Use the organizer's methods to process the single file
                parent_dir = file_path_obj.parent
                file_name = file_path_obj.name
                
                # Get file type and organize
                import magic
                file_type = magic.from_file(str(file_path_obj), mime=True).lower()
                self.organizer.check_and_move(file_name, file_type, parent_dir)
                
            else:
                self.log(f"⚠️ File no longer exists: {file_path}")
                
        except Exception as e:
            self.log(f"❌ Error processing {file_path}: {e}")
        finally:
            # Clean up the pending file entry
            with self.timer_lock:
                if file_path in self.pending_files:
                    del self.pending_files[file_path]


class FileWatcherService:
    """Service for monitoring directories and auto-organizing files"""
    
    def __init__(self, logger=None):
        self.logger = logger or print
        self.observer = None
        self.watched_paths = {}
        self.is_running = False
        self.config_path = Path(__file__).parent.parent / "config" / "watcher_config.json"
        self.handler = FileOrganizerHandler(logger=logger)

    def log(self, message):
        if self.logger:
            self.logger(message)

    def load_config(self):
        """Load watcher configuration"""
        try:
            if self.config_path.exists():
                with open(self.config_path, 'r') as f:
                    return json.load(f)
            else:
                return {
                    "watched_directories": [],
                    "watcher_enabled": False,
                    "auto_organize": True,
                    "check_interval": 1.0
                }
        except Exception as e:
            self.log(f"❌ Error loading watcher config: {e}")
            return {
                "watched_directories": [],
                "watcher_enabled": False,
                "auto_organize": True,
                "check_interval": 1.0
            }

    def save_config(self, config):
        """Save watcher configuration"""
        try:
            self.config_path.parent.mkdir(exist_ok=True)
            with open(self.config_path, 'w') as f:
                json.dump(config, f, indent=2)
            return True
        except Exception as e:
            self.log(f"❌ Error saving watcher config: {e}")
            return False

    def add_watched_directory(self, directory_path):
        """Add a directory to the watch list"""
        path = Path(directory_path).resolve()
        if not path.exists():
            self.log(f"❌ Directory does not exist: {path}")
            return False
        
        if not path.is_dir():
            self.log(f"❌ Path is not a directory: {path}")
            return False

        config = self.load_config()
        path_str = str(path)
        
        if path_str not in config["watched_directories"]:
            config["watched_directories"].append(path_str)
            self.save_config(config)
            self.log(f"✅ Added to watch list: {path}")
            
            # If watcher is running, start monitoring this directory immediately
            if self.is_running:
                self._start_watching_directory(path_str)
            return True
        else:
            self.log(f"⚠️ Directory already being watched: {path}")
            return False

    def remove_watched_directory(self, directory_path):
        """Remove a directory from the watch list"""
        config = self.load_config()
        path_str = str(Path(directory_path).resolve())
        
        if path_str in config["watched_directories"]:
            config["watched_directories"].remove(path_str)
            self.save_config(config)
            self.log(f"✅ Removed from watch list: {path_str}")
            
            # If watcher is running, stop monitoring this directory
            if self.is_running and path_str in self.watched_paths:
                self.observer.unschedule(self.watched_paths[path_str])
                del self.watched_paths[path_str]
            return True
        else:
            self.log(f"⚠️ Directory not in watch list: {path_str}")
            return False

    def get_watched_directories(self):
        """Get list of currently watched directories"""
        config = self.load_config()
        return config["watched_directories"]

    def _start_watching_directory(self, directory_path):
        """Start watching a specific directory"""
        try:
            watch = self.observer.schedule(self.handler, directory_path, recursive=False)
            self.watched_paths[directory_path] = watch
            self.log(f"👁️ Started monitoring: {directory_path}")
        except Exception as e:
            self.log(f"❌ Failed to start monitoring {directory_path}: {e}")

    def start_watching(self):
        """Start the file watcher service"""
        if self.is_running:
            self.log("⚠️ Watcher is already running")
            return False

        try:
            config = self.load_config()
            if not config.get("watcher_enabled", False):
                self.log("⚠️ Watcher is disabled in configuration")
                return False

            self.observer = Observer()
            
            # Start watching all configured directories
            for directory_path in config["watched_directories"]:
                if Path(directory_path).exists():
                    self._start_watching_directory(directory_path)
                else:
                    self.log(f"⚠️ Skipping non-existent directory: {directory_path}")

            self.observer.start()
            self.is_running = True
            self.log("✅ File watcher service started")
            return True
            
        except Exception as e:
            self.log(f"❌ Failed to start watcher service: {e}")
            return False

    def stop_watching(self):
        """Stop the file watcher service"""
        if not self.is_running:
            self.log("⚠️ Watcher is not running")
            return False

        try:
            if self.observer:
                self.observer.stop()
                self.observer.join(timeout=5)
                self.observer = None
            
            self.watched_paths.clear()
            self.is_running = False
            self.log("✅ File watcher service stopped")
            return True
            
        except Exception as e:
            self.log(f"❌ Failed to stop watcher service: {e}")
            return False

    def set_watcher_enabled(self, enabled):
        """Enable or disable the watcher service"""
        config = self.load_config()
        config["watcher_enabled"] = enabled
        self.save_config(config)
        
        if enabled and not self.is_running:
            self.start_watching()
        elif not enabled and self.is_running:
            self.stop_watching()

    def is_watcher_enabled(self):
        """Check if watcher is enabled in configuration"""
        config = self.load_config()
        return config.get("watcher_enabled", False)

    def get_status(self):
        """Get current watcher service status"""
        return {
            "is_running": self.is_running,
            "is_enabled": self.is_watcher_enabled(),
            "watched_directories": self.get_watched_directories(),
            "active_watches": len(self.watched_paths)
        }
