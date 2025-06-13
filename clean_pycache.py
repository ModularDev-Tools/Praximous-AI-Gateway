# clean_pycache.py
import os
import shutil

def delete_pycache(project_root="."):
    """
    Deletes all __pycache__ directories and .pyc files within the project_root.
    """
    deleted_folders_count = 0
    deleted_files_count = 0

    for root, dirs, files in os.walk(project_root, topdown=False): # topdown=False to delete subdirs first
        # Delete .pyc files
        for name in files:
            if name.endswith(".pyc"):
                file_path = os.path.join(root, name)
                try:
                    os.remove(file_path)
                    print(f"Deleted file: {file_path}")
                    deleted_files_count += 1
                except OSError as e:
                    print(f"Error deleting file {file_path}: {e}")

        # Delete __pycache__ directories
        if "__pycache__" in dirs:
            pycache_dir = os.path.join(root, "__pycache__")
            try:
                shutil.rmtree(pycache_dir)
                print(f"Deleted directory: {pycache_dir}")
                deleted_folders_count += 1
            except OSError as e:
                print(f"Error deleting directory {pycache_dir}: {e}")

    print(f"\nCache cleaning complete.")
    print(f"Deleted {deleted_folders_count} __pycache__ folder(s).")
    print(f"Deleted {deleted_files_count} .pyc file(s).")

if __name__ == "__main__":
    delete_pycache()