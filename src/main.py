# Import required modules
import json
import zipfile
import os
from file_functions import *
from metadata_functions import *
from pathlib import Path
from datetime import datetime
import platform

from PIL import Image
from PIL.ExifTags import TAGS, GPSTAGS


# These are the steps needed:

################################################
# Step 1: Read the JSON file to get the environment variables
with open('vars/environment_vars_test.json', 'r') as file:
    env_vars = json.load(file)

path_info = env_vars['pathInfo']
extract_path = path_info['takeoutPrefix']

# Ensure the target directory exists, create if it doesn't (check once outside the loop)
if not os.path.exists(extract_path):
    os.makedirs(extract_path)
    print(f"Ensured directory {extract_path} exists")

# Step 2: Extract each zip file directly into the takeoutPrefix directory
#unzip_multiple_folders (path_info['zippedFiles'], extract_path)
    
################################################
### 3. Merge all directories together

for takeout_file in path_info['takeoutFiles']:
    allTakeoutFiles = os.path.join(extract_path, takeout_file + '.zip')

#dest = allTakeoutFiles[0]
dest = os.path.join(extract_path, path_info["takeoutFiles"][0])
#source = allTakeoutFiles[1:]

#merge_directories(dest, source)

################################################
### 4. Update file metadata. Find corresponding json metadata and use the info to:

# Edit the file's metadata with the information inside the json file
#update_file_metadata('Takeout')

def update_metadata(file_path, json_path):
    # Load the JSON data
    with open(json_path, 'r') as f:
        data = json.load(f)

    file_path_str = str(file_path)

    # Use the timestamp directly
    creation_time = int(data['photoTakenTime']['timestamp'])
    modification_time = int(data['creationTime']['timestamp'])

    # Check if a non-empty description exists
    description = data.get('description', '').strip()
    
        # Here you can add your logic to handle the description
        # For example, printing it or embedding it into the file metadata (if supported)
    edit_properties(file_path_str, description, data['geoDataExif'])

    # Check and print non-zero values in geoData
    #print_non_zero_values(data['geoData'], file_path_str)

    # Check and print non-zero values in geoDataExif
    #print_non_zero_values(data['geoDataExif'], file_path_str)

    if platform.system() == 'Windows':
        update_file_metadata_windows(file_path_str, creation_time, modification_time)
    else:
        # Update the file times for non-Windows systems
        os.utime(file_path_str, (creation_time, modification_time))
    
#    os.remove(str(json_path))
#    print(f"{json_path} deleted successfully.")
  
print(f"Updating file metadata now: {dest}")
#update_file_metadata(dest)
def main():
    for root, dirs, files in os.walk(dest):
        for file in files:
            json_file = Path(root) / f'{file}.json'
            #if json_file.exists():
                #update_metadata(Path(root) / file, json_file) 
                    
def process_directory():
    # Dictionary to hold base_name to its files and json_file mapping
    files_map = {}

    for root, dirs, files in os.walk(dest):
        for file in files:
            if file.endswith('.json'):
                base_name = file.rsplit('.', 2)[0]  # Assumes the base name is everything before the 2nd "." from the right
                full_path = Path(root) / base_name
                if full_path not in files_map:
                    files_map[full_path] = {'files': [], 'json': None}
                files_map[full_path]['json'] = Path(root) / file
            else:
                # This part assumes the base name is everything before the first "." from the right
                #base_name, _, _ = file.partition('.')
                base_name = file.rsplit('.', 1)[0]
                full_path = Path(root) / base_name
                if full_path not in files_map:
                    files_map[full_path] = {'files': [], 'json': None}
                files_map[full_path]['files'].append(Path(root) / file)

    # Process files based on the mapping
    for base_file, data in files_map.items():
        """if len(data['files']) > 1:
            print(f"Base Name: {base_file}")
            print(f"  Associated Files: {[str(file) for file in data['files']]}")
            print(f"  JSON File: {data['json']}")"""

        json_file = data['json']
        if json_file:
            for file_path in data['files']:
                update_metadata(file_path, json_file)

    
process_directory()



