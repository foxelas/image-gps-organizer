from os.path import exists, getmtime
from os import makedirs, listdir, stat, utime, getcwd
from os.path import join as pathjoin
from datetime import datetime, timezone
import tkinter as tk
import piexif


def get_date_from_filename(filename):
    # For filenames with pattern IMG_20220730_081219_847.jpg
    date_time_str = filename.split('.')[0]
    parts = date_time_str.split('_')
    parts = parts[1:]
    if len(parts)>2:
        parts = parts[:-1]
    date_time_str = '_'.join(parts)
    try:
        date_time_obj = datetime.strptime(date_time_str, '%Y%m%d_%H%M%S')
        return date_time_obj
    except ValueError:
        print(f'Failed to modify file {filename}')
        return None

def write_date_on_metadata(filepath, target_datetime):
    datetime_timestamp = datetime.timestamp(target_datetime)
    datetime_utf_string = datetime.strftime(target_datetime, "%Y:%m:%d %H:%M:%S").encode('utf-8')

    ## change exif datetimestamp for "Date Taken"
    exif_dict = piexif.load(filepath)
    exif_dict['Exif'][piexif.ExifIFD.DateTimeOriginal] = datetime_utf_string
    exif_dict['Exif'][piexif.ExifIFD.DateTimeDigitized] = datetime_utf_string
    exif_bytes = piexif.dump(exif_dict)
    piexif.insert(exif_bytes, filepath)

    ## Change access and modified time
    stats = stat(filepath)
    #print(stats)
    modify_date = datetime.fromtimestamp(stats.st_mtime)
    access_date = datetime.fromtimestamp(stats.st_atime)
    #print(f'Previous access date {access_date} and modified date {modify_date}')
    #print(f'New access date {target_datetime} and modified date {target_datetime}')
    utime(filepath, (datetime_timestamp, datetime_timestamp))



def rename_files_in_current_folder(): 
    source_dir = getcwd()
    print(f'Source folder: {source_dir}')

    #target_dir = pathjoin(source_dir, 'output')
    #if not exists(target_dir):
    #    makedirs(target_dir)

    target_files = listdir(source_dir)
    target_files = [x for x in target_files if '.jpg' in x]

    local_tz = datetime.now(timezone.utc).astimezone().tzinfo

    for img_file in target_files:
        filepath = pathjoin(source_dir, img_file)
        target_datetime = get_date_from_filename(img_file).replace(tzinfo=local_tz)
        if target_datetime is not None:
            write_date_on_metadata(filepath, target_datetime)

    lbl2.config(text="Done!")


root = tk.Tk()

canvas1 = tk.Canvas(root, width = 300, height = 300)
canvas1.pack()
    
button1 = tk.Button(text='Click Me', command=rename_files_in_current_folder, bg='blue',fg='white')
canvas1.create_window(150, 150, window=button1)
lbl = tk.Label(text="The images should be placed in the same\nfolder as this .exe file.The expected image \nformat is IMG_20220730_081219_847.jpg.")
lbl.place(x=40, y=50)
lbl2 = tk.Label(text="")
lbl2.place(x=130, y=200)

root.mainloop()