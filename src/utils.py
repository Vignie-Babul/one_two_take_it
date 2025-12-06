import os


def is_file_valid(path: str) -> bool:
    if not os.path.exists(path):
        print(f"Файл не найден: {file_path}")
        return False
    
    if not os.path.isfile(path):
        print(f"Указанный путь является директорией: {file_path}")
        return False
    
    return True
