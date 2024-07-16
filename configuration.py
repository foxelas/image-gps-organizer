ACCEPTED_FILETYPES = ['jpg', 'dng'] #, 'mp4', 'mov']

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