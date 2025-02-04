import shutil
import os

def clean_folders_except_pdf():
    """
    This function removes all folders and their contents except for the 'pdf' folder.
    It should be called after the PDF generation process is complete.
    """
    # List of folders to keep
    folders_to_keep = ['pdf']

    # Get the current working directory
    current_dir = os.getcwd()

    # Iterate through all items in the current directory
    for item in os.listdir(current_dir):
        item_path = os.path.join(current_dir, item)
        if os.path.isdir(item_path) and item not in folders_to_keep:
            try:
                # Remove the directory and all its contents
                shutil.rmtree(item_path)
                print(f"Removed directory: {item_path}")
            except Exception as e:
                print(f"Could not remove directory {item_path}. Error: {e}")    
