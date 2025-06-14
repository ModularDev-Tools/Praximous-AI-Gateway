# clean_pycache.py
import os
import shutil
from pathlib import Path # Import Path

def delete_pycache(project_root_str: str = "."): # Added type hint for the input string
    """
    Deletes all __pycache__ directories and .pyc files within the project_root.
    """
    project_root = Path(project_root_str).resolve() # Convert to Path object and resolve to absolute path
    deleted_folders_count = 0
    deleted_files_count = 0

    print(f"Scanning for __pycache__ directories and .pyc files in: {project_root}\n")

    # os.walk still takes a string, but we can convert Path objects inside the loop
    for root_str, dirs, files in os.walk(str(project_root), topdown=False):
        root_path = Path(root_str) # Current root as a Path object

        # Delete .pyc files
        for name in files:
            if name.endswith(".pyc"):
                file_path = root_path / name # Use Path's / operator for joining
                try:
                    file_path.unlink() # Path.unlink() to delete file
                    print(f"Deleted file: {file_path}")
                    deleted_files_count += 1
                except OSError as e:
                    print(f"Error deleting file {file_path}: {e}")

        # Delete __pycache__ directories
        if "__pycache__" in dirs: # 'dirs' contains directory names, not full paths
            pycache_dir_path = root_path / "__pycache__" # Construct full path to __pycache__
            try:
                shutil.rmtree(pycache_dir_path) # shutil.rmtree works with Path objects
                print(f"Deleted directory: {pycache_dir_path}")
                deleted_folders_count += 1
            except OSError as e:
                print(f"Error deleting directory {pycache_dir_path}: {e}")

    print(f"\nCache cleaning complete.")
    print(f"Deleted {deleted_folders_count} __pycache__ folder(s).")
    print(f"Deleted {deleted_files_count} .pyc file(s).")

if __name__ == "__main__":
    delete_pycache()