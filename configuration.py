ACCEPTED_IMAGE_FILETYPES = ['jpg', 'jpeg', 'dng']
VIDEO_FILETYPES = ['mov', 'mp4']
FILE_SORTING_LIST = ['jpg', 'jpeg', 'JPG', 'png', 'heic', 'HEIC', 'dng', 'DNG', 'mov', 'MOV', 'mp4', 'MP4']

TRACKER_FILE = 'location_tracker.csv'

ISLAND_GROUPS = {
    'South Aegean': 'South Aegean',
    'North Aegean': 'North Aegean',
    'Crete': 'Crete',
    'Dodecanese': 'Dodekanisa',
    'Attica': 'Saronic',
    'Ionian Islands': 'Ionio',
    'Ioanian Islands': 'Ionio'

}


from geopy.geocoders import Nominatim
GEOLOCATOR = Nominatim(user_agent="photo_organizer")

CODEC = 'ISO-8859-1'  # or latin-1