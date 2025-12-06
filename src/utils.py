import os


def is_file_valid(path: str) -> bool:
	if not os.path.exists(path):
		print(f'File not found: {path}')
		return False

	if not os.path.isfile(path):
		print(f'This is a directory: {path}')
		return False

	return True
