import os
import os

import pillow_heif
from PIL import Image

from configuration import FILE_SORTING_LIST, ACCEPTED_IMAGE_FILETYPES, VIDEO_FILETYPES


def list_files_in_directory(target_dir, function=None, target_filetypes=ACCEPTED_IMAGE_FILETYPES + VIDEO_FILETYPES):
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
            function(full_path)

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

def convert_heic_to_jpg(input_path, quality=95):
    """
    Converts a HEIC image to JPG format with minimal quality loss.

    Args:
        input_path (str): Path to the input HEIC file.
        quality (int): Quality of the output JPG (1-100, higher is better).

    Returns:
        None
    """
    try:
        # Read the HEIC file
        heif_file = pillow_heif.open_heif(input_path)

        # Convert HEIF to a Pillow Image
        image = Image.frombytes(
            heif_file.mode, heif_file.size, heif_file.data, "raw", heif_file.mode, heif_file.stride
        )

        output_path = os.path.splitext(input_path)[0] + '.jpg'

        # Save as JPG with the specified quality
        image.save(output_path, "JPEG", quality=quality)

        print(f"Conversion successful: {output_path}")
    except Exception as e:
        print(f"Error during conversion: {e}")

def convert_heic_to_jpg_bulk(target_dir):
    print(f"Selected directory: {target_dir}")
    # Ensure the directory exists
    if not os.path.exists(target_dir):
        print(f"The directory '{target_dir}' does not exist.")
        return

    list_files_in_directory(target_dir, function=convert_heic_to_jpg, target_filetypes=['heic', 'HEIC'])
    print("Done!")


# Example usage:
# Replace '/path/to/directory' with the actual directory path containing the images
# convert_jpeg_to_png_bulk('G:\\My Drive\\Stickers\\μεμε')
