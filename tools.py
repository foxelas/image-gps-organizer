import os
from PIL import Image
from pillow_heif import register_heif_opener
import piexif

register_heif_opener()

from configuration import FILE_SORTING_LIST, ACCEPTED_IMAGE_FILETYPES, VIDEO_FILETYPES


def list_files_in_directory(target_dir, function=None, target_filetypes=ACCEPTED_IMAGE_FILETYPES + VIDEO_FILETYPES, **kwargs):
    file_list = []
    # Walk through the directory tree
    for root, dirnames, filenames in os.walk(target_dir):
        filenames = [x for x in filenames if x.lower().endswith(tuple(target_filetypes))]
        for filename in filenames:
            full_path = os.path.join(root, filename)
            file_list.append(full_path)

    file_list = sort_files_by_priority(file_list)

    if function is not None:
        for full_path in file_list:
            function(full_path, **kwargs)

    return file_list


priority_dict = {ext: index for index, ext in enumerate(FILE_SORTING_LIST)}


def get_priority(file_path):
    extension = file_path.split('.')[-1].lower()
    return priority_dict.get(extension, len(priority_dict))


def sort_files_by_priority(file_paths):
    return sorted(file_paths, key=get_priority)


def convert_jpeg_to_png(file_path):
    try:
        # Open the image using Pillow
        with Image.open(file_path) as img:
            # Save as .png with the same filename (but different extension)
            file_path = os.path.splitext(file_path)[0] + '.png'
            img.save(file_path, 'PNG')
            print(f"Converted '{file_path}'")
    except Exception as e:
        print(f"Error converting '{file_path}': {e}")


def convert_jpeg_to_png_bulk(target_dir):
    print(f"Selected directory: {target_dir}")
    # Ensure the directory exists
    if not os.path.exists(target_dir):
        print(f"The directory '{target_dir}' does not exist.")
        return

    list_files_in_directory(target_dir, function=convert_jpeg_to_png, target_filetypes=['jpg', 'jpeg', 'JPG', 'JPEG'])
    print("Done!")


def get_geotagging(exif):
    geo_tagging_info = {}
    if not exif:
        raise ValueError("No EXIF metadata found")
    else:
        exif = exif.get_ifd(0x8825)
        gps_keys = ['GPSVersionID', 'GPSLatitudeRef', 'GPSLatitude', 'GPSLongitudeRef', 'GPSLongitude',
                    'GPSAltitudeRef', 'GPSAltitude', 'GPSTimeStamp', 'GPSSatellites', 'GPSStatus', 'GPSMeasureMode',
                    'GPSDOP', 'GPSSpeedRef', 'GPSSpeed', 'GPSTrackRef', 'GPSTrack', 'GPSImgDirectionRef',
                    'GPSImgDirection', 'GPSMapDatum', 'GPSDestLatitudeRef', 'GPSDestLatitude', 'GPSDestLongitudeRef',
                    'GPSDestLongitude', 'GPSDestBearingRef', 'GPSDestBearing', 'GPSDestDistanceRef', 'GPSDestDistance',
                    'GPSProcessingMethod', 'GPSAreaInformation', 'GPSDateStamp', 'GPSDifferential']

        for k, v in exif.items():
            try:
                geo_tagging_info[gps_keys[k]] = str(v)
            except IndexError:
                pass
        return geo_tagging_info


def convert_heic_to_jpg(input_path, quality=95, strip_exif=False, delete_original=False):
    """
    Converts a HEIC image to JPG format with minimal quality loss.

    Args:
        input_path (str): Path to the input HEIC file.
        quality (int): Quality of the output JPG (1-100, higher is better).

    Returns:
        None
        :param strip_exif:
    """
    try:
        # Read the HEIC file
        image = Image.open(input_path)
        exif_dict = piexif.load(image.info["exif"])
        exif_bytes = piexif.dump(exif_dict)

        output_path = os.path.splitext(input_path)[0] + '.jpg'

        if strip_exif:
            exif_bytes = piexif.dump({})

        # Save as JPG with the specified quality
        image.save(output_path, "JPEG", quality=quality, exif=exif_bytes)
        print(f"Conversion successful: {output_path}")

        if delete_original:
            os.remove(input_path)

    except Exception as e:
        print(f"Error during conversion: {e}")

def convert_heic_to_jpg_bulk(target_dir, quality=95, strip_exif=False, delete_original=False):

    print(f"Selected directory: {target_dir}")
    # Ensure the directory exists
    if not os.path.exists(target_dir):
        print(f"The directory '{target_dir}' does not exist.")
        return

    list_files_in_directory(target_dir, function=convert_heic_to_jpg, target_filetypes=['heic', 'HEIC'],
                            quality=quality, strip_exif=strip_exif, delete_original=delete_original)
    print("Done!")

# Example usage:
# Replace '/path/to/directory' with the actual directory path containing the images
# import tools
# tools.convert_jpeg_to_png_bulk('G:\\My Drive\\Stickers\\μεμε')
# tools.convert_heic_to_jpg_bulk()
