ACCEPTED_IMAGE_FILETYPES = ['jpg', 'dng']
VIDEO_FILETYPES = ['mov', 'mp4']

TRACKER_FILE = 'location_tracker.csv'

ISLAND_GROUPS = {
    'South Aegean': 'Cyclades',
    'North Aegean': 'Sporades',
    'Crete': 'Crete',
    'Dodecanese': 'Dodekanisa',
    'Attica': 'Saronic',
    'Ionian Islands': 'Ionio'
}

from geopy.geocoders import Nominatim
GEOLOCATOR = Nominatim(user_agent="photo_organizer")

CODEC = 'ISO-8859-1'  # or latin-1