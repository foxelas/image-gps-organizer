import os
import shutil
import tkinter as tk
from os.path import join as pathjoin
from tkinter import filedialog
import xml.etree.ElementTree as ET
import ffmpeg
import piexif
from PIL import Image
import pandas as pd
from configuration import ACCEPTED_IMAGE_FILETYPES, ISLAND_GROUPS, CODEC, GEOLOCATOR, VIDEO_FILETYPES, TRACKER_FILE, \
    FILE_SORTING_LIST
from tools import list_files_in_directory


def init_date_tracker():
    if os.path.exists(TRACKER_FILE):
        date_tracker_df_ = pd.read_csv(TRACKER_FILE, index_col=0)
        date_tracker_df_.index = pd.to_datetime(date_tracker_df_.index)

    else:
        date_tracker_df_ = pd.DataFrame({'capture_datetime': [], 'latitude': [], 'longitude': [], 'location': []})
        date_tracker_df_.set_index('capture_datetime', inplace=True)
        date_tracker_df_.to_csv(TRACKER_FILE)

    return date_tracker_df_


date_tracker_df = init_date_tracker()


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
            exif_data['CreateDate'] = description.get(f"{{{namespaces['xmp']}}}ModifyDate")
            exif_data['MetadataDate'] = description.get(f"{{{namespaces['xmp']}}}MetadataDate")
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


def get_video_metadata(filepath):
    probe = ffmpeg.probe(filepath)
    return probe['format']['tags']


def append_to_tracker(capture_datetime, lat, lon, location):
    if capture_datetime is not None and capture_datetime not in date_tracker_df.index:
        capture_datetime = pd.to_datetime(capture_datetime)
        date_tracker_df.loc[capture_datetime] = [lat, lon, location]
        date_tracker_df.sort_index(inplace=True)
        print(f"Append to tracker: {capture_datetime}, {lat}, {lon}, {location}")
        print(date_tracker_df)


def fetch_from_tracker(capture_datetime):
    if capture_datetime is not None:
        print(f"Fetching GPS data for {capture_datetime}")
        try:
            idx = date_tracker_df.index.get_indexer([capture_datetime], method='nearest')
            res = date_tracker_df.iloc[idx]
            lat = res['latitude'].values[0]
            lon = res['longitude'].values[0]
            return lat, lon
        except ValueError as e:
            print(f"Error: {e}")
            return None, None
    else:
        return None, None


def get_gps_data_from_metadata(filepath, capture_datetime=None):
    print(f"Processing file: {filepath}")
    lat = None
    lon = None

    if filepath.lower().endswith('.jpg'):
        im = Image.open(filepath)
        exif_dict = piexif.load(im.info.get('exif'))
        exif_data = exif_to_tag(exif_dict)
        gps_data = exif_data['GPS']
        capture_datetime = exif_data['Exif']['DateTimeOriginal']
        capture_datetime = pd.to_datetime(capture_datetime, format='%Y:%m:%d %H:%M:%S')
        lat, lon = exif_tag_to_lat_lon(gps_data)

    elif filepath.lower().endswith('.dng'):
        im = Image.open(filepath)
        exif_dict = extract_exif_from_xmp(im.info.get('xmp').decode('utf-8'))
        lat = exif_dict.get('GpsLatitude')
        lon = exif_dict.get('GpsLongitude')
        ## ignore because it is wrong date
        capture_datetime = None
        # capture_datetime = exif_dict.get('MetadataDate') if exif_dict.get('MetadataDate') is not None else exif_dict.get('CreateDate')
        # capture_datetime = pd.to_datetime(capture_datetime, format='mixed').replace(tzinfo=None)

    elif filepath.lower().endswith('.mov'):
        res = get_video_metadata(filepath)
        capture_datetime = res['creation_time']
        capture_datetime = pd.to_datetime(capture_datetime, format='%Y-%m-%dT%H:%M:%S.%f%z').replace(tzinfo=None)
        lat, lon = fetch_from_tracker(capture_datetime)
        if lat is None or lon is None:
            print(f"No GPS data available for video files: {filepath}")

    elif filepath.lower().endswith('.mp4'):
        res = get_video_metadata(filepath)
        capture_datetime = res['creation_time']
        capture_datetime = pd.to_datetime(capture_datetime, format='%Y-%m-%dT%H:%M:%S.%f%z').replace(tzinfo=None)
        lat, lon = fetch_from_tracker(capture_datetime)
        if lat is None or lon is None:
            print(f"No GPS data available for video files: {filepath}")

    return lat, lon, capture_datetime


def get_address_from_gps(lat, lon):
    location = GEOLOCATOR.reverse(lat + "," + lon, language="en", timeout=None, addressdetails=True)
    print(location.address)
    return location.raw


def parse_island_name(municipality, regional_unit):
    if municipality is not None:
        island = municipality.replace("Municipality of", "").strip()
        island = island.replace("Municipality", "").strip()
        return island
    else:
        island = regional_unit.replace("Regional Unit of", "").strip()
        island = island.replace("Regional Unit", "").strip()
        return island


def parse_address(address):
    address = address['address']

    municipality = address.get('municipality', None)
    regional_unit = address.get('county', None)
    state_district = address.get('state_district', None)
    island = parse_island_name(municipality, regional_unit)
    group = ISLAND_GROUPS.get(state_district)
    return island, group


def copy_file(source_path, target_dir, target_name):
    if not os.path.exists(target_dir):
        os.makedirs(target_dir)  # Create the directory if it doesn't exist

    destination_path = pathjoin(target_dir, target_name)
    shutil.copy2(source_path, destination_path)
    print(f"File copied to: {destination_path}")


def move_file_to_output_folder(filepath):
    lat, lon, capture_datetime = get_gps_data_from_metadata(filepath)

    if lat is None or lon is None:
        # Move the file to the output folder
        filename = os.path.basename(filepath)
        filename, extension = os.path.splitext(filename)
        target_dir = pathjoin("Stelios Photos for Istion", "no_gps")
        target_name = filename + "_" + "no_gps" + extension
        copy_file(filepath, target_dir, target_name)
        return

    address = get_address_from_gps(str(lat), str(lon))
    island, group = parse_address(address)
    print(island, group)

    if filepath.lower().endswith(tuple(ACCEPTED_IMAGE_FILETYPES)):
        append_to_tracker(capture_datetime, lat, lon, island)

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


def organize_photos():
    target_dir = select_target_directory()
    if target_dir is None:
        return

    print(f"Selected directory: {target_dir}")

    list_files_in_directory(target_dir, function=move_file_to_output_folder)

    print(date_tracker_df)
    date_tracker_df.to_csv(TRACKER_FILE)
    print("Done!")
    lbl2.config(text="Done!")


root = tk.Tk()

canvas1 = tk.Canvas(root, width=500, height=300)
canvas1.pack()

button1 = tk.Button(text='Organize Photos', command=organize_photos, bg='blue', fg='white')
canvas1.create_window(140, 150, window=button1, height=50, width=200)
lbl = tk.Label(
    text=" Scans a selected folder (and its subfolders) for photos with GPS metadata. \nMoves these photos to a new folder, renaming them to include \nthe corresponding island and group information.",
    justify=tk.LEFT, bd=4, relief=tk.RIDGE, bg='lightblue')
lbl.place(x=40, y=50)
lbl2 = tk.Label(text="")
lbl2.place(x=130, y=200)

root.mainloop()
