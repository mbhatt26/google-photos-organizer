import shutil
import os
import zipfile

# Directory is 'Takeout'
# Merge all directories into 1 directory
def merge_directories(destination_directory, source_directories):
    if not os.path.exists(destination_directory):
        os.makedirs(destination_directory) #create a dst. directory if not exist
    
    for source_dir in source_directories:
        for root, dirs, files in os.walk(source_dir):
            for file in files:
                source_path = os.path.join(root, file)
                destination_path = os.path.join(destination_directory, os.path.relpath(source_path, source_dir))

                # Ensure the destination directory exists
                os.makedirs(os.path.dirname(destination_path), exist_ok=True)

                # Copy or move the file to the destination directory
                shutil.move(source_path, destination_path)  # Change to shutil.move if you want to move instead of copy
                print(f"'{source_path}' --> '{destination_path}'")


# unzip a folder function 
def unzip_takeout_folders(pathToZipfile, pathToExtractTo):
    if not zipfile.is_zipfile(pathToZipfile):
        print(f"{pathToZipfile} is not a valid ZIP file.")
        return
    
    with zipfile.ZipFile(pathToZipfile, 'r') as zip_ref:
        os.makedirs(pathToExtractTo, exist_ok=True)
        zip_ref.extractall(pathToExtractTo)
        print(f"Extracted {pathToZipfile} to {pathToExtractTo}")

def unzip_multiple_folders(zipped_path, extract_path):
    for zipped_file in zipped_path:
        # Construct full path for the zip file
        zip_file_path = os.path.join(extract_path, zipped_file + '.zip')

        # Check if the zip file exists
        if os.path.exists(zip_file_path):
            with zipfile.ZipFile(zip_file_path, 'r') as zip_ref:    
                # Extract the file
                zip_ref.extractall(extract_path)
                print(f"Extracted {zipped_file} directly into takeoutPrefix.")
        else:
            print(f"Zip file {zip_file_path} does not exist.") 