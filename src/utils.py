import os


def is_file_valid(path: str) -> bool:
	if not os.path.exists(path):
		print(f"File not found: {file_path}")
		return False
	
	if not os.path.isfile(path):
		print(f"This is a directory: {file_path}")
		return False
	
	return True
