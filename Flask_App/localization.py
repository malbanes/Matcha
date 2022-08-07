import requests
from geopy.geocoders import Nominatim
import math
import os


def localize_user():
    r = requests.get('https://api.ipgeolocation.io/ipgeo?apiKey=' + str(os.getenv('GEO_API')))
    result = r.json()
    print(result)
    localisation = str(result["city"]) + " - " + str(result["zipcode"])
    latitude = result["latitude"]
    longitude = result["longitude"]
    return(localisation, latitude, longitude)

def localize_text(loc):
    try:
        geolocator = Nominatim(user_agent="Matcha 42 school project app")
        new_loc = geolocator.geocode(str(loc)).raw
        #print(new_loc['lat'])
        #print(new_loc['lon'])
        print(new_loc['display_name'])
        if ", " in new_loc['display_name']:
            city_name = new_loc['display_name'].split(", ")[0].strip()
        else:
            city_name = new_loc['display_name'].strip()
        return float(new_loc['lat']), float(new_loc['lon']), str(city_name)
    except:
        return 0.0, 0.0, "ERROR - WRONG LOCALISATION"

def distance(lat1, lon1, lat2, lon2):
    R = 6373.0
    #radius of the Earth

    lat1 = math.radians(lat1)
    lon1 = math.radians(lon1)
    lat2 = math.radians(lat2)
    lon2 = math.radians(lon2)

    dlon = lon2 - lon1
    dlat = lat2 - lat1

    a = math.sin(dlat / 2)**2 + math.cos(lat1) * math.cos(lat2) * math.sin(dlon / 2)**2
    #Haversine formula
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    distance = R * c

    #print(distance)
    return(distance)