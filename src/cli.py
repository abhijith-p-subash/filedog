#!/usr/bin/env python3
"""
Cross-Platform File Organizer CLI
Organizes files in any directory based on their MIME types.
Works on Windows, macOS, and Linux.
"""

import os
import sys
import shutil
import platform
import argparse
import json
import mimetypes
from pathlib import Path
from typing import Dict, Optional, Tuple

# Try to import python-magic, fall back to mimetypes if not available
try:
    import magic
    HAS_MAGIC = True
except ImportError:
    HAS_MAGIC = False
    print("⚠️  python-magic not found. Using built-in mimetypes (less accurate)")
    print("   Install with: pip install python-magic")
    if platform.system() == "Windows":
        print("   On Windows, also install: pip install python-magic-bin")

class CrossPlatformFileOrganizer:
    def __init__(self, config_path: Optional[str] = None):
        self.config = self._load_config(config_path)
        self.stats = {
            'processed': 0,
            'moved': 0,
            'errors': 0,
            'skipped': 0
        }
    
    def _load_config(self, config_path: Optional[str]) -> Dict:
        """Load configuration from JSON file or use default"""
        default_config = {
            "file_type": {
                "image/": "Images",
                "video/": "Videos", 
                "audio/": "Audio",
                "text/plain": "Text_Files",
                "text/csv": "CSV_Files",
                "text/html": "HTML_Files",
                "text/css": "CSS_Files",
                "text/javascript": "JavaScript",
                "application/json": "JSON_Files",
                "application/xml": "XML_Files",
                "application/pdf": "PDFs",
                "application/msword": "Word_Documents",
                "application/vnd.openxmlformats-officedocument.wordprocessingml.document": "Word_Documents",
                "application/vnd.ms-excel": "Excel_Files",
                "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet": "Excel_Files",
                "application/vnd.ms-excel.sheet.macroenabled.12": "Excel_Files",
                "application/vnd.ms-powerpoint": "PowerPoint_Files",
                "application/vnd.openxmlformats-officedocument.presentationml.presentation": "PowerPoint_Files",
                "application/vnd.oasis.opendocument.text": "OpenDocument_Text",
                "application/vnd.oasis.opendocument.spreadsheet": "OpenDocument_Spreadsheet",
                "application/vnd.oasis.opendocument.presentation": "OpenDocument_Presentation",
                "application/zip": "Archives",
                "application/x-rar-compressed": "Archives",
                "application/x-7z-compressed": "Archives",
                "application/x-tar": "Archives",
                "application/gzip": "Archives",
                "application/x-bzip2": "Archives",
                "text/x-python": "Code_Files",
                "application/x-python": "Code_Files",
                "application/javascript": "Code_Files",
                "text/x-java-source": "Code_Files",
                "application/java-archive": "Code_Files",
                "application/x-sh": "Scripts",
                "application/x-csh": "Scripts",
                "text/x-php": "Code_Files",
                "application/x-ruby": "Code_Files",
                "application/x-perl": "Code_Files",
                "application/x-executable": "Executables",
                "application/x-msdownload": "Executables",
                "application/octet-stream": "Binary_Files",
                "application/vnd.android.package-archive": "Android_APK",
                "application/x-dosexec": "Windows_Executables",
                "font/": "Fonts"
            },
            "default": "Other_Files"
        }
        
        if config_path and os.path.exists(config_path):
            try:
                with open(config_path, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except Exception as e:
                print(f"⚠️  Error loading config file: {e}")
                print("   Using default configuration...")
                return default_config
        
        return default_config
    
    def _get_file_type(self, file_path: Path) -> str:
        """Get MIME type of file using best available method"""
        try:
            if HAS_MAGIC:
                return magic.from_file(str(file_path), mime=True)
            else:
                # Fallback to mimetypes module
                mime_type, _ = mimetypes.guess_type(str(file_path))
                return mime_type or 'application/octet-stream'
        except Exception as e:
            print(f"⚠️  Could not determine file type for {file_path.name}: {e}")
            return 'application/octet-stream'
    
    def _get_folder_name(self, file_type: str) -> str:
        """Determine target folder name based on file type"""
        # Exact match
        if file_type in self.config["file_type"]:
            return self.config["file_type"][file_type]
        
        # Prefix match (like image/, audio/, video/)
        for key, folder in self.config["file_type"].items():
            if file_type.startswith(key):
                return folder
        
        # Fallback to default
        return self.config["default"]
    
    def _sanitize_folder_name(self, folder_name: str) -> str:
        """Sanitize folder name for cross-platform compatibility"""
        # Replace problematic characters for Windows
        problematic_chars = '<>:"|?*'
        for char in problematic_chars:
            folder_name = folder_name.replace(char, '_')
        
        # Remove leading/trailing spaces and dots
        folder_name = folder_name.strip(' .')
        
        # Ensure it's not empty
        if not folder_name:
            folder_name = "Unknown"
        
        return folder_name
    
    def _create_directory(self, path: Path, folder_name: str) -> Path:
        """Create directory if it doesn't exist"""
        folder_name = self._sanitize_folder_name(folder_name)
        folder_path = path / folder_name
        
        try:
            folder_path.mkdir(exist_ok=True)
            return folder_path
        except Exception as e:
            print(f"❌ Could not create directory {folder_path}: {e}")
            raise
    
    def _move_file(self, source: Path, target_dir: Path) -> bool:
        """Move file to target directory with conflict resolution"""
        target_path = target_dir / source.name
        
        # Handle file name conflicts
        counter = 1
        original_target = target_path
        while target_path.exists():
            stem = original_target.stem
            suffix = original_target.suffix
            target_path = target_dir / f"{stem}_{counter}{suffix}"
            counter += 1
        
        try:
            shutil.move(str(source), str(target_path))
            if target_path != original_target:
                print(f"   📝 Renamed to: {target_path.name}")
            return True
        except Exception as e:
            print(f"   ❌ Move failed: {e}")
            return False
    
    def _validate_directory(self, path_str: str) -> Optional[Path]:
        """Validate and return Path object for directory"""
        try:
            path = Path(path_str).resolve()
            
            if not path.exists():
                print(f"❌ Directory does not exist: {path}")
                return None
            
            if not path.is_dir():
                print(f"❌ Path is not a directory: {path}")
                return None
            
            # Test if we can read the directory
            try:
                list(path.iterdir())
            except PermissionError:
                print(f"❌ Permission denied: Cannot access {path}")
                return None
            
            return path
        
        except Exception as e:
            print(f"❌ Invalid path '{path_str}': {e}")
            return None
    
    def organize_directory(self, target_path: str, dry_run: bool = False, verbose: bool = False) -> None:
        """Main function to organize files in a directory"""
        print(f"🖥️  Platform: {platform.system()} {platform.release()}")
        print(f"🐍 Python: {sys.version.split()[0]}")
        print(f"📁 Target directory: {target_path}")
        
        path = self._validate_directory(target_path)
        if not path:
            return
        
        if dry_run:
            print("🧪 DRY RUN MODE - No files will be moved")
        
        print("📂 Scanning directory...")
        
        try:
            # Get all files (not directories)
            files = [f for f in path.iterdir() if f.is_file()]
            
            if not files:
                print("📭 No files found to organize")
                return
            
            print(f"📋 Found {len(files)} files to process")
            print("=" * 60)
            
            for index, file_path in enumerate(files, 1):
                if verbose:
                    print(f"\n[{index}/{len(files)}] Processing: {file_path.name}")
                else:
                    # Show progress for non-verbose mode
                    if index % 10 == 0 or index == len(files):
                        print(f"📊 Progress: {index}/{len(files)} files processed")
                
                try:
                    # Get file type
                    file_type = self._get_file_type(file_path)
                    folder_name = self._get_folder_name(file_type)
                    
                    if verbose:
                        print(f"   🏷️  MIME type: {file_type}")
                        print(f"   📂 Target folder: {folder_name}")
                    
                    if not dry_run:
                        # Create target directory and move file
                        target_dir = self._create_directory(path, folder_name)
                        success = self._move_file(file_path, target_dir)
                        
                        if success:
                            self.stats['moved'] += 1
                            if verbose:
                                print(f"   ✅ Moved to: {target_dir.name}/")
                        else:
                            self.stats['errors'] += 1
                    else:
                        if verbose:
                            print(f"   🧪 Would move to: {folder_name}/")
                    
                    self.stats['processed'] += 1
                
                except Exception as e:
                    self.stats['errors'] += 1
                    print(f"   ❌ Error processing {file_path.name}: {e}")
            
            # Print summary
            self._print_summary(dry_run)
            
        except Exception as e:
            print(f"❌ Error accessing directory: {e}")
    
    def _print_summary(self, dry_run: bool) -> None:
        """Print operation summary"""
        print("\n" + "=" * 60)
        print("📊 SUMMARY")
        print(f"   • Files processed: {self.stats['processed']}")
        
        if not dry_run:
            print(f"   • Successfully moved: {self.stats['moved']}")
            print(f"   • Errors: {self.stats['errors']}")
        else:
            print(f"   • Would be organized: {self.stats['processed']}")
        
        if self.stats['errors'] > 0:
            print(f"\n⚠️  {self.stats['errors']} files had errors")


def main():
    parser = argparse.ArgumentParser(
        description="Cross-platform file organizer - Organize files by type",
        epilog="Examples:\n"
               "  %(prog)s /path/to/directory\n"
               "  %(prog)s C:\\Users\\Name\\Downloads\n"
               "  %(prog)s ~/Downloads --dry-run --verbose\n"
               "  %(prog)s . --config custom_config.json",
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    
    parser.add_argument(
        'directory',
        help='Directory path to organize (can be absolute or relative)'
    )
    
    parser.add_argument(
        '--config', '-c',
        help='Path to custom configuration JSON file'
    )
    
    parser.add_argument(
        '--dry-run', '-n',
        action='store_true',
        help='Preview changes without moving files'
    )
    
    parser.add_argument(
        '--verbose', '-v',
        action='store_true',
        help='Show detailed output for each file'
    )
    
    parser.add_argument(
        '--version',
        action='version',
        version='File Organizer CLI v1.0.0'
    )
    
    args = parser.parse_args()
    
    # Initialize organizer
    organizer = CrossPlatformFileOrganizer(config_path=args.config)
    
    # Run organization
    try:
        organizer.organize_directory(
            target_path=args.directory,
            dry_run=args.dry_run,
            verbose=args.verbose
        )
    except KeyboardInterrupt:
        print("\n⚠️  Operation cancelled by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()