
from PIL import Image
from PIL.ExifTags import TAGS
import shutil
import os
import json
from win32com.propsys import propsys, pscon
from win32com.shell import shellcon
import pythoncom, os
import ctypes
from ctypes import wintypes

def encode_exif(exif_data):
    # Encode the modified EXIF data
    exif_bytes = b''
    for tag, value in exif_data.items():
        tag_id = TAGS.get(tag, tag)
        exif_bytes += tag_id.to_bytes(2, byteorder='big', signed=False)
        exif_bytes += (2).to_bytes(2, byteorder='big', signed=False)
        exif_bytes += (len(value)).to_bytes(4, byteorder='big', signed=False)
        exif_bytes += value if isinstance(value, bytes) else str(value).encode('utf-8')

    return exif_bytes

def update_image_description(image_path, new_description):
    
    print(image_path)
    # Open the image
    img = Image.open(image_path)

    # Get the existing EXIF data (if any)
    exif_data = img.info.get("exif", {})
    print(exif_data)

    # Add or update the ImageDescription tag in the EXIF data
    exif_data[TAGS.get(270)] = new_description
    new_path = image_path + '2'

    # Save the image with the updated EXIF data
    img.save(new_path, exif=encode_exif(exif_data))
    
################################################
### 4.a Gather the data
def print_non_zero_values(dictionary, file_path):
    geoDataAvailable = False
    for key, value in dictionary.items():
        if float(value) != 0:
            geoDataAvailable = True
            print(f"Non-zero values in {file_path}: - {key}: {value}")
        
            if (key == "latitude"):
                lat = value
            elif (key == "longitude"):
                long = value
            elif (key == "altitude"):
                alt = value
    if (geoDataAvailable):
        pk_lat = propsys.PSGetPropertyKeyFromName("System.GPS.Latitude")
        pk_long = propsys.PSGetPropertyKeyFromName("System.GPS.Longitude")
        pk_alt = propsys.PSGetPropertyKeyFromName("System.GPS.Altitude")
        ps = propsys.SHGetPropertyStoreFromParsingName(file_path, None, 2)

        print(f"PropertyKey: {pk_lat}")

        propcount = ps.GetCount()
        print(f"Prop count before location update: {propcount}")

        new_lat = propsys.PROPVARIANTType(lat)
        new_long = propsys.PROPVARIANTType(long)
        new_alt = propsys.PROPVARIANTType(alt)

        ps.SetValue(pk_lat, new_lat)
        ps.SetValue(pk_long, new_long)
        ps.SetValue(pk_alt, new_alt)

        propcountb = ps.GetCount()
        print(f"Prop count after location update: {propcountb}")
        ps.Commit()

def decimal_degrees_to_dms(decimal_degree):
    # Convert decimal degrees to degrees, minutes, and seconds
    is_negative = decimal_degree < 0
    decimal_degree = abs(decimal_degree)
    degrees = int(decimal_degree)
    minutes = int((decimal_degree - degrees) * 60)
    seconds = (decimal_degree - degrees - minutes/60) * 3600 * 10000  # Multiplying by 10000 for precision
    # Representing as a tuple of (value, scale) to form a rational number
    dms = ((degrees, 1), (minutes, 1), (int(seconds), 10000))
    if is_negative:
        # For negative values, invert the degrees
        dms = ((-dms[0][0], dms[0][1]), dms[1], dms[2])
    return dms

def decimal_degrees_to_rational(decimal_degree):
    # Convert a decimal degree into a rational approximation (numerator, denominator).
    # This is a simplified representation and may need refinement for more accuracy.
    is_negative = decimal_degree < 0
    decimal_degree_abs = abs(decimal_degree)
    numerator = int(decimal_degree_abs * 10000)
    denominator = 10000
    if is_negative:
        numerator = -numerator
    return (numerator, denominator)

################################################
### 4.b. Update file date created and date modified
    
    
################################################
### 4.c. Update file description tage
    
################################################
### 4.d. Update file location tag

def set_gps_coordinates(file_path, latitude, longitude):
    # Ensure COM libraries are initialized
    pythoncom.CoInitialize()
    
    # Open the file property store
    property_store = propsys.SHGetPropertyStoreFromParsingName(file_path, None, 2, propsys.IID_IPropertyStore)
    
    # Convert decimal degrees to degrees, minutes, seconds
    lat_dms = decimal_degrees_to_rational(latitude)
    lon_dms = decimal_degrees_to_rational(longitude)
    print(f"Latitude: {latitude}, Longitude: {longitude}")
    
    # Set the GPS Latitude property
    var_lat = propsys.PROPVARIANTType(lat_dms, pythoncom.VT_VECTOR | pythoncom.VT_I4)
    property_store.SetValue(pscon.PKEY_GPS_Latitude, var_lat)
    
    # Set the GPS Longitude property
    var_lon = propsys.PROPVARIANTType(lon_dms, pythoncom.VT_VECTOR | pythoncom.VT_I4)
    property_store.SetValue(pscon.PKEY_GPS_Longitude, var_lon)
    
    # Commit changes to the file
    property_store.Commit()
    print(f"Updated GPS coordinates for {file_path}")
    

def update_file_metadata(directory):
    # Look in the specified directory and iterate over the files
    for root, dirs, files in os.walk(directory):
        for file in files:
        # For each file ending in .json, find the file without the .json
            if file.endswith(".json"):
                print(f"File ends in json: {file}")
                json_file_path = os.path.join(root, file)
                original_file_path = os.path.splitext(json_file_path)[0]  # Remove the '.json' extension
                if os.path.exists(original_file_path):
                    print(f"Media file {original_file_path} found.")
                    # Read JSON file
                    with open(json_file_path, 'r') as json_file:
                        json_data = json.load(json_file)

                        # Extract creation and modification times
                        creation_time = int(json_data.get('photoTakenTime', {}).get('timestamp'))
                        modification_time = int(json_data.get('creationTime', {}).get('timestamp'))
                        
                        print(original_file_path)
                        print(creation_time)
                        print(modification_time)

                        if creation_time and modification_time:
                            # Convert timestamp to datetime
                            # Update original file creation time
                            os.utime(original_file_path, (creation_time, creation_time))

                        # testing metadata:
                        description = json_data.get('description')
                        if description:
                            #update_image_description(original_file_path, description)
                            print(json_file_path + description)

                            '''try:
                                os.remove(json_file_path)
                                print(f"File '{json_file_path}' deleted")

                            except OSError as e:
                                print(f"Error deleting file '{json_file_path}': {e}")  '''

def update_file_metadata_windows(file_path_str, creation_time, modification_time):

    # Convert Unix timestamp to Windows FILETIME
    # Windows FILETIME is the number of 100-nanosecond intervals since January 1, 1601 (UTC)
    # Unix timestamp is seconds since January 1, 1970 (UTC)
    # 11644473600 is the number of seconds between the 1601 and 1970 epochs
    # 10000000 is the number of 100-nanosecond intervals in a second
    creation_time_ft = int((creation_time + 11644473600) * 10000000)
    modification_time_ft = int((modification_time + 11644473600) * 10000000)

    # Open the file to get a handle
    handle = ctypes.windll.kernel32.CreateFileW(file_path_str, 0x10000000, 0, None, 3, 0x80, None)
    if handle == -1:
        raise ctypes.WinError()

    # Create FILETIME structures
    creation_time_ctypes = wintypes.FILETIME(creation_time_ft & 0xFFFFFFFF, creation_time_ft >> 32)
    modification_time_ctypes = wintypes.FILETIME(modification_time_ft & 0xFFFFFFFF, modification_time_ft >> 32)

#    if( os.path.splitext(file_path_str)[1].lower() == '.mov') :
#        print(f"file_path: {file_path_str}")

    # Update the file times
    result = ctypes.windll.kernel32.SetFileTime(handle, ctypes.byref(creation_time_ctypes), None, ctypes.byref(modification_time_ctypes))
    if not result:
        raise ctypes.WinError()

    # Close the file handle
    ctypes.windll.kernel32.CloseHandle(handle)


def edit_properties(file_path_str, description, dictionary):
    geoDataAvailable = False
    for key, value in dictionary.items():
        if float(value) != 0:
            geoDataAvailable = True
#           print(f"Non-zero values in {file_path_str}: - {key}: {value}")
        
            if (key == "latitude"):
                lat = value
            elif (key == "longitude"):
                long = value
            elif (key == "altitude"):
                alt = value
    location_str = "latitude: " + str(lat) + ", longitude: " + str(long) + ", altitude: " + str(alt) 

    try:
        ps = propsys.SHGetPropertyStoreFromParsingName(file_path_str, None, 2, propsys.IID_IPropertyStore)
        
        if description:
            pk_desc = propsys.PSGetPropertyKeyFromName("System.Title")
#            print(file_path_str, " - New description:", description)
            newValue = propsys.PROPVARIANTType(description)
            ps.SetValue(pk_desc, newValue)

        if (geoDataAvailable):
            # Get the property key for the "Comment" property
            pk_comment = propsys.PSGetPropertyKeyFromName("System.Comment")
        
            # Log the file and new comments containing location for confirmation
#            print(f"Location: {location_str}")
            
            # Create a new PROPVARIANT to hold the comments
            new_value = propsys.PROPVARIANTType(location_str)
            
            # Set the "Comments" property to the new value
            ps.SetValue(pk_comment, new_value)
            """pk_lat = propsys.PSGetPropertyKeyFromName("System.GPS.Latitude")
            pk_long = propsys.PSGetPropertyKeyFromName("System.GPS.Longitude")
            pk_alt = propsys.PSGetPropertyKeyFromName("System.GPS.Altitude")

            print(f"PropertyKey: {pk_lat}")

            propcount = ps.GetCount()
            print(f"Prop count before location update: {propcount}")

            new_lat = propsys.PROPVARIANTType(lat)
            new_long = propsys.PROPVARIANTType(long)
            new_alt = propsys.PROPVARIANTType(alt)

            ps.SetValue(pk_lat, new_lat)
            ps.SetValue(pk_long, new_long)
            ps.SetValue(pk_alt, new_alt)

            propcountb = ps.GetCount()
            print(f"Prop count after location update: {propcountb}")"""
    #        set_gps_coordinates(file_path_str, lat, long)
        ps.Commit()
    except:
        print(f"Title, Comments not updated: {file_path_str} - Description: {description}, location: {location_str}")
