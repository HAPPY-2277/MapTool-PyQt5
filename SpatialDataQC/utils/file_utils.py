import os
from typing import Optional


def ensure_dir(directory: str) -> str:
    if not os.path.exists(directory):
        os.makedirs(directory)
    return directory


def get_file_extension(file_path: str) -> str:
    return os.path.splitext(file_path)[1].lower()


def get_file_name(file_path: str) -> str:
    return os.path.basename(file_path)


def get_file_dir(file_path: str) -> str:
    return os.path.dirname(file_path)


def is_file_exists(file_path: str) -> bool:
    return os.path.isfile(file_path)


def get_unique_filename(directory: str, base_name: str, extension: str) -> str:
    counter = 1
    file_path = os.path.join(directory, f"{base_name}{extension}")
    
    while os.path.exists(file_path):
        file_path = os.path.join(directory, f"{base_name}_{counter}{extension}")
        counter += 1
    
    return file_path


def format_file_size(size_bytes: int) -> str:
    for unit in ['B', 'KB', 'MB', 'GB']:
        if size_bytes < 1024:
            return f"{size_bytes:.2f} {unit}"
        size_bytes /= 1024
    return f"{size_bytes:.2f} TB"
