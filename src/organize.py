import os
import shutil

# Define paths
downloads_folder = '/Users/hichem/Downloads'
desktop_path = '/Users/hichem/Desktop'
flux_images_folder = os.path.join(desktop_path, 'Flux Images')

# Supported image extensions
image_extensions = ['.jpg', '.jpeg', '.png', '.gif', '.bmp', '.tiff']

def create_directory_if_not_exists(path):
    """Create a directory if it does not exist."""
    if not os.path.exists(path):
        os.makedirs(path)
        print(f"Created folder: {path}")

def move_file(src, dst):
    """Move a file from src to dst with error handling."""
    try:
        shutil.move(src, dst)
        print(f"Moved file: {os.path.basename(src)}")
    except Exception as e:
        print(f"Error moving file: {e}")

def organize_downloads():
    # Create Flux Images folder on Desktop
    create_directory_if_not_exists(flux_images_folder)

    # Iterate over files in the Downloads folder
    for filename in os.listdir(downloads_folder):
        file_path = os.path.join(downloads_folder, filename)
        
        # Skip directories
        if os.path.isdir(file_path):
            continue

        # Get extension and lowercase it
        _, ext = os.path.splitext(filename)
        ext = ext.lower()

        # Check if it's an image file
        if ext not in image_extensions:
            continue

        # Check for "flux" in the filename (case-insensitive)
        if 'flux' in filename.lower():
            # Move flux-related images to Flux Images folder
            move_file(file_path, os.path.join(flux_images_folder, filename))
        else:
            # Organize other images by type
            image_type_folder = os.path.join(downloads_folder, ext.lstrip('.').upper())
            create_directory_if_not_exists(image_type_folder)
            move_file(file_path, os.path.join(image_type_folder, filename))

if __name__ == "__main__":
    print("Starting to organize Downloads folder...")
    organize_downloads()
    print("Organizing complete.")
