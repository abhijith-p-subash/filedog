import os
import shutil
import platform
import magic
import json
from pathlib import Path

with open('folder_config.json', "r") as f:
    folder_config = json.load(f)


def get_folder_name(file_type, config):
    if file_type in config["file_type"][file_type]:
        return config["file_type"][file_type]
    
    for key, folder in config["file_type"].items():
        if file_type.startswith(key):
            return folder
        
    return config["default"]

def check_create_dir(path, folder_name):
    folder_path = path / folder_name
    if not folder_path.exists():
        folder_path.mkdir()
        print(f"Folder '{folder_name}' created at {folder_path}")
    else:
        print(f"Folder '{folder_name}' already exists at {folder_path}")

def move_data(path, folder_name, file):
    try:
        source = path/file
        target = path / folder_name / file
        print("Start Moving file: {file}")
        shutil.move(source, target)
        print("Done ✅")
    except Exception as e:
        print(f"Failed Error: {e}")


def check_and_move(file, file_type, file_path, path):
    try:
        folder_name = None
        print(f"File type:{file_type}")
        print(f"File path:{file_path}")
        print(f"Path:{path}")

        if file_type.startswith('image'):
            print("Image")
            folder_name = folder_config.get('image')
            print(f"FOLDER NAME => {folder_name}")
            check_create_dir(path, folder_name)
            move_data(path, folder_name, file)
        elif file_type == 'application/pdf':
            print("PDF")
            folder_name = folder_config.get('application/pdf')
            print(f"FOLDER NAME => {folder_name}")
            check_create_dir(path, folder_name)
            move_data(path, folder_name, file)
        elif file_type.startswith('audio'):
            print("Audio")
            folder_name = folder_config.get('audio')
            print(f"FOLDER NAME => {folder_name}")
            check_create_dir(path, folder_name)
            move_data(path, folder_name, file)
        elif file_type.startswith('video'):
            print("Video")
            folder_name = folder_config.get('video')
            print(f"FOLDER NAME => {folder_name}")
            check_create_dir(path, folder_name)
            move_data(path, folder_name, file)
        elif 'excel' in file_type:
            print("Excel")
            folder_name = folder_config.get('excel')
            print(f"FOLDER NAME => {folder_name}")
            check_create_dir(path, folder_name)
            move_data(path, folder_name, file)
        elif 'word' in file_type:
            print("Word Document")
            folder_name = folder_config.get('word')
            print(f"FOLDER NAME => {folder_name}")
            check_create_dir(path, folder_name)
            move_data(path, folder_name, file)
        elif file_type == 'text/csv':
            print("CSV")
            folder_name = folder_config.get('text/csv')
            print(f"FOLDER NAME => {folder_name}")
            check_create_dir(path, folder_name)
            move_data(path, folder_name, file)
        else:
            print("Unknown file type")
            folder_name = folder_config.get('default')
            print(f"FOLDER NAME => {folder_name}")
            check_create_dir(path, folder_name)
            move_data(path, folder_name, file)
    except Exception as e:
        print(e)
        return e
    

download_path = Path.home() / "Downloads"

print(platform.system())
print(download_path)


files = os.listdir(download_path)
print(files)

for index, file in enumerate(files):
    file_path = download_path / file
    print(f"FILE PATH:{file_path}")
    if file_path.is_file():
        print(f"{index + 1}. {file}")
        try:
            file_type = magic.from_file(str(file_path), mime=True)
            print(f"File type is {file_type}\n")
            check_and_move(file, file_type, file_path, download_path)
        except Exception as e:
            print(f"Could not determine file type: {e}\n")



    