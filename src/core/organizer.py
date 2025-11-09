import json
import os
import shutil
import magic
from pathlib import Path

CONFIG_PATH = Path(__file__).parent.parent / "config" / "folder_config.json"

with open(CONFIG_PATH, "r") as f:
    folder_config = json.load(f)

class FileOrganizer:
    def __init__(self, logger=None):
        self.logger = logger or print

    def log(self, message):
        if self.logger:
            self.logger(message)

    

    def organize(self, path: Path):
        try:
            files = os.listdir(path)
            self.log(f"📋 Found {len(files)} items")
            processed_count = 0
            success_count = 0

            for index, file in enumerate(files):
                file_path = path / file
                self.log(f"\n{'='*50}")
                self.log(f"Processing item {index + 1}/{len(files)}: {file}")
                # self.log(f"FILE PATH:{file_path}")
                if file_path.is_file():
                    try:
                        file_type = magic.from_file(str(file_path), mime=True).lower()
                        self.log(f"🏷️ Detected file type: {file_type}")
                        if self.check_and_move(file, file_type, path):
                            success_count += 1
                        processed_count += 1
                    except Exception as e:
                        self.log(f"❌ Could not determine file type for {file}: {e}")

                self.log(f"\n{'='*50}")
                self.log("📊 Summary:")
                self.log(f"   • Files processed: {processed_count}")
                self.log(f"   • Successfully moved: {success_count}")
                self.log(f"   • Failed: {processed_count - success_count}")
        except Exception as e:
            self.log(f"❌ Error accessing directory: {e}")
        


        # -------- HELPER FUNCTIONS --------
    def check_create_dir(self, path, folder_name):
        folder_path = path / folder_name
        if not folder_path.exists():
            folder_path.mkdir(parents=True, exist_ok=True)
            self.log(f"📂 Created folder: {folder_path}")
        else:
            self.log(f"📂 Folder exists: {folder_path}")

    def move_data(self, path, folder_name, file):
        try:
            source = path / file
            target = path / folder_name / file
            self.log(f"➡️ Moving file: {file}")
            shutil.move(str(source), str(target))
            self.log("✅ Done")
            return True
        except Exception as e:
            self.log(f"❌ Move failed: {e}")
            return False
        
    def get_folder_name(self,file_type, config):
        self.log(f"🔍 Looking up folder for file type: {file_type}")
        # 1. Exact match
        if file_type in config["file_type"]:
            folder = config["file_type"][file_type]
            self.log(f"✅ Exact match found: {folder}")
            return folder
    
    
        # 2. prefix match (like image/, audio/, video/)
        for key, folder in config["file_type"].items():
            self.log("In loop")
            if file_type.startswith(key):
                self.log(f"✅ Prefix match found: {key} -> {folder}")
                return folder
        # Fallback  
        self.log(f"⚠️ No match found, using default: {config['default']}")
        return config["default"]
    
    def check_and_move(self, file, file_type, path):
        try:
            self.log(f"🔎 File type: {file_type}")
            folder_name = self.get_folder_name(file_type, folder_config)
            self.log(f"📂 Target folder: {folder_name}")

            self.check_create_dir(path, folder_name)
            res = self.move_data(path, folder_name, file)
            if res:
                self.log(f"✅ Successfully processed: {file}")
            else:
                self.log(f"❌ Failed to move: {file}")

        except Exception as e:
            self.log(f"⚠️ Error processing {file}: {e}")
            return False
        return True
