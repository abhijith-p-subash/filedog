import os
import shutil
import platform
import magic
import json
from pathlib import Path

with open('folder_config.json', "r") as f:
    folder_config = json.load(f)


def check_create_dir(path, folder_name):
    folder_path = path / folder_name
    if not folder_path.exists():
        folder_path.mkdir()
        print(f"📂 Created folder: {folder_path}")
    else:
        print(f"📂 Folder exists: {folder_path}")

def move_data(path, folder_name, file):
    try:
        source = path / file
        target = path / folder_name / file
        print(f"➡️ Moving file: {file}")
        shutil.move(str(source), str(target))
        print("✅ Done")
        return True
    except Exception as e:
        print(f"❌ Move failed: {e}")
        return False

def get_folder_name(file_type, config):
    print(f"🔍 Looking up folder for file type: {file_type}")
    # 1. Exact match
    if file_type in config["file_type"]:
        folder = config["file_type"][file_type]
        print(f"✅ Exact match found: {folder}")
        return folder
    
    
    # 2. prefix match (like image/, audio/, video/)
    for key, folder in config["file_type"].items():
        print("In loop")
        if file_type.startswith(key):
            print(f"✅ Prefix match found: {key} -> {folder}")
            return folder
    # Fallback  
    print(f"⚠️ No match found, using default: {config['default']}")
    return config["default"]


def check_and_move(file, file_type, path):
    try:
        print(f"🔎 File type: {file_type}")
        folder_name = get_folder_name(file_type, folder_config)
        print(f"📂 Target folder: {folder_name}")

        check_create_dir(path, folder_name)
        res = move_data(path, folder_name, file)
        if res:
            print(f"✅ Successfully processed: {file}")
        else:
            print(f"❌ Failed to move: {file}")

    except Exception as e:
        print(f"⚠️ Error processing {file}: {e}")
        return False
    return True

download_path = Path.home() / "Downloads"
print(f"🖥️ Operating System: {platform.system()}")
print(f"📂 Scanning directory: {download_path}")

try:
    files = os.listdir(download_path)
    print(f"📋 Found {len(files)} items")
    processed_count = 0
    success_count = 0

    for index, file in enumerate(files):
        file_path = download_path / file
        print(f"\n{'='*50}")
        print(f"Processing item {index + 1}/{len(files)}: {file}")
        # print(f"FILE PATH:{file_path}")
        if file_path.is_file():
            try:
                file_type = magic.from_file(str(file_path), mime=True)
                print(f"🏷️ Detected file type: {file_type}")
                if check_and_move(file, file_type, download_path):
                    success_count += 1
                processed_count += 1
            except Exception as e:
                print(f"❌ Could not determine file type for {file}: {e}")

        print(f"\n{'='*50}")
        print("📊 Summary:")
        print(f"   • Files processed: {processed_count}")
        print(f"   • Successfully moved: {success_count}")
        print(f"   • Failed: {processed_count - success_count}")
except Exception as e:
    print(f"❌ Error accessing directory: {e}")


    