import os
import logging
from pathlib import Path
import shutil

def file_exists(path_to_file: str) -> bool:
    return Path(path_to_file).is_file()

def remove_file_name_from_dir(dir) -> str:
    # Get the absoluate path as formatted by os.path.abspath(). This ensures each directory is separated by '\\'
    dir = os.path.abspath(dir)
    # Find the index of the last '\\' indicating the end of the last folder.
    idx = dir.rfind('\\')
    return dir[:idx+1]

def directory_exists(dir) -> bool:
    # Clean the string in case a file name is passed with directory
    if '.' in dir:
        dir = remove_file_name_from_dir(dir)
    return os.path.isdir(dir)
    
def create_directory(dir):
    # Clean the string in case a file name is passed with directory
    if '.' in dir:
        dir = remove_file_name_from_dir(dir)
    if not os.path.isdir(dir):
        # Use os.makedirs instead of os.mkdir. Otherwise requests to create a directory with a subfolder
        # will cause an error: FileNotFoundError: [WinError 3] The system cannot find the path specified: '../TestDir2/next/'
        os.makedirs(dir)
    else:
        logging.info(f'Tried to create directory {dir}, but it already exists.')

def remove_directory(dir):
    if directory_exists(dir):
        shutil.rmtree(dir)

def remove_file(f):
    if file_exists(f):
        os.remove(f)

def get_files_in_directory(dir) -> list[str]:
    f = []
    for (dirpath, dirnames, filenames) in os.walk(dir):
        f.extend(filenames)
        break
    return f

def write_to_file(f, text):
    create_directory(remove_file_name_from_dir(f))
    with open(f,'w', encoding='utf-8') as f:
        f.write(text)
