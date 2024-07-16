import os
import shutil
import tkinter as tk
from os.path import join as pathjoin
from tkinter import filedialog
import piexif
from PIL import Image
from configuration import ACCEPTED_FILETYPES, ISLAND_GROUPS, CODEC, GEOLOCATOR


def exif_to_tag(exif_dict):
    exif_tag_dict = {}
    thumbnail = exif_dict.pop('thumbnail')
    exif_tag_dict['thumbnail'] = thumbnail.decode(CODEC)
    for ifd in exif_dict:
        exif_tag_dict[ifd] = {}
        for tag in exif_dict[ifd]:
            try:
                element = exif_dict[ifd][tag].decode(CODEC)

            except AttributeError:
                element = exif_dict[ifd][tag]

            exif_tag_dict[ifd][piexif.TAGS[ifd][tag]["name"]] = element

    return exif_tag_dict


def exif_tag_to_lat_lon(gps_data):
    def convert_to_degrees(value):
        """Helper function to convert GPS coordinates to degrees in float."""
        d = value[0][0] / value[0][1]
        m = value[1][0] / value[1][1]
        s = value[2][0] / value[2][1]
        return d + (m / 60.0) + (s / 3600.0)

    gps_latitude = gps_data.get('GPSLatitude')
    gps_latitude_ref = gps_data.get('GPSLatitudeRef')
    gps_longitude = gps_data.get('GPSLongitude')
    gps_longitude_ref = gps_data.get('GPSLongitudeRef')

    if gps_latitude and gps_latitude_ref and gps_longitude and gps_longitude_ref:
        lat = convert_to_degrees(gps_latitude)
        lon = convert_to_degrees(gps_longitude)

        if gps_latitude_ref != 'N':
            lat = -lat
        if gps_longitude_ref != 'E':
            lon = -lon

        return lat, lon
    else:
        return None, None

import xml.etree.ElementTree as ET

def extract_exif_from_xmp(xmp_data):
    try:
        # Parse the XMP data
        root = ET.fromstring(xmp_data)

        # Define namespaces
        namespaces = {
            'rdf': 'http://www.w3.org/1999/02/22-rdf-syntax-ns#',
            'tiff': 'http://ns.adobe.com/tiff/1.0/',
            'exif': 'http://ns.adobe.com/exif/1.0/',
            'xmp': 'http://ns.adobe.com/xap/1.0/',
            'xmpMM': 'http://ns.adobe.com/xap/1.0/mm/',
            'dc': 'http://purl.org/dc/elements/1.1/',
            'crs': 'http://ns.adobe.com/camera-raw-settings/1.0/',
            'drone-dji': 'http://www.dji.com/drone-dji/1.0/',
            'GPano': 'http://ns.google.com/photos/1.0/panorama/'
        }

        # Find rdf:Description element
        description = root.find('.//rdf:Description', namespaces)

        # Extract attributes from rdf:Description
        exif_data = {}
        if description is not None:
            exif_data['ModifyDate'] = description.get(f"{{{namespaces['xmp']}}}ModifyDate")
            exif_data['CreateDate'] = description.get(f"{{{namespaces['xmp']}}}CreateDate")
            exif_data['Make'] = description.get(f"{{{namespaces['tiff']}}}Make")
            exif_data['Model'] = description.get(f"{{{namespaces['tiff']}}}Model")
            exif_data['Format'] = description.get(f"{{{namespaces['dc']}}}format")
            exif_data['GpsLatitude'] = description.get(f"{{{namespaces['drone-dji']}}}GpsLatitude")
            exif_data['GpsLongitude'] = description.get(f"{{{namespaces['drone-dji']}}}GpsLongitude")
            exif_data['AbsoluteAltitude'] = description.get(f"{{{namespaces['drone-dji']}}}AbsoluteAltitude")
            exif_data['RelativeAltitude'] = description.get(f"{{{namespaces['drone-dji']}}}RelativeAltitude")
            exif_data['GimbalRollDegree'] = description.get(f"{{{namespaces['drone-dji']}}}GimbalRollDegree")
            exif_data['GimbalYawDegree'] = description.get(f"{{{namespaces['drone-dji']}}}GimbalYawDegree")
            exif_data['GimbalPitchDegree'] = description.get(f"{{{namespaces['drone-dji']}}}GimbalPitchDegree")
            exif_data['FlightRollDegree'] = description.get(f"{{{namespaces['drone-dji']}}}FlightRollDegree")
            exif_data['FlightYawDegree'] = description.get(f"{{{namespaces['drone-dji']}}}FlightYawDegree")
            exif_data['FlightPitchDegree'] = description.get(f"{{{namespaces['drone-dji']}}}FlightPitchDegree")

        return exif_data

    except Exception as e:
        print(f"Error extracting EXIF from XMP: {e}")
        return None


def get_gps_data_from_metadata(filepath):
    lat = None
    lon = None
    im = Image.open(filepath)

    if filepath.lower().endswith('.jpg'):
        exif_dict = piexif.load(im.info.get('exif'))
        exif_data = exif_to_tag(exif_dict)
        gps_data = exif_data['GPS']
        lat, lon = exif_tag_to_lat_lon(gps_data)
        print(lat, lon)

    elif filepath.lower().endswith('.dng'):
        exif_dict = extract_exif_from_xmp(im.info.get('xmp').decode('utf-8'))
        lat = exif_dict.get('GpsLatitude')
        lon = exif_dict.get('GpsLongitude')

    return lat, lon


def get_address_from_gps(lat, lon):
    location = GEOLOCATOR.reverse(lat + "," + lon, language="en")
    return location.address


def parse_island_name(parts):
    island = parts[-4].replace("Regional Unit", "").strip()
    if island == "of Islands":
        return parts[-5].replace("Municipality of", "").strip()
    else:
        return island


def parse_island_group(parts):
    group = ISLAND_GROUPS[parts[-3].strip()]
    return group


def parse_address(address):
    parts = address.split(",")
    island = parse_island_name(parts)
    group = parse_island_group(parts)
    return island, group


def copy_file(source_path, target_dir, target_name):
    if not os.path.exists(target_dir):
        os.makedirs(target_dir)  # Create the directory if it doesn't exist

    destination_path = pathjoin(target_dir, target_name)
    shutil.copy2(source_path, destination_path)
    print(f"File copied to: {destination_path}")


def move_file_to_output_folder(filepath):
    lat, lon = get_gps_data_from_metadata(filepath)
    print(f"Found GPS data in {filepath}")

    address = get_address_from_gps(str(lat), str(lon))
    print(address)
    island, group = parse_address(address)
    print(island, group)

    # Move the file to the output folder
    filename = os.path.basename(filepath)
    filename, extension = os.path.splitext(filename)
    target_dir = pathjoin("Stelios Photos for Istion", group, island)
    target_name = filename + "_" + group + "_" + island + extension
    copy_file(filepath, target_dir, target_name)
    print(f"\n")


def select_target_directory():
    directory_path = filedialog.askdirectory()

    if directory_path:
        return directory_path
    else:
        return None


def list_files_in_directory(target_dir, function=None):
    file_list = []
    # Walk through the directory tree
    for root, dirnames, filenames in os.walk(target_dir):
        filenames = [x for x in filenames if x.lower().endswith(tuple(ACCEPTED_FILETYPES))]
        for filename in filenames:
            full_path = os.path.join(root, filename)
            file_list.append(full_path)
            if function is not None:
                function(full_path)

    return file_list


def organize_photos():

    target_dir = select_target_directory()
    if target_dir is None:
        return

    print(f"Selected directory: {target_dir}")

    target_files = list_files_in_directory(target_dir)
    print(f"Found {len(target_files)} files in the selected directory")

    list_files_in_directory(target_dir, function=move_file_to_output_folder)

    lbl2.config(text="Done!")


root = tk.Tk()

canvas1 = tk.Canvas(root, width=500, height=300)
canvas1.pack()

button1 = tk.Button(text='Organize Photos', command=organize_photos, bg='blue', fg='white')
canvas1.create_window(140, 150, window=button1, height=50, width=200)
lbl = tk.Label(
    text=" Scans a selected folder (and its subfolders) for photos with GPS metadata. \nMoves these photos to a new folder, renaming them to include \nthe corresponding island and group information.",
    justify = tk.LEFT, bd=4, relief = tk.RIDGE, bg = 'lightblue')
lbl.place(x=40, y=50)
lbl2 = tk.Label(text="")
lbl2.place(x=130, y=200)

root.mainloop()
