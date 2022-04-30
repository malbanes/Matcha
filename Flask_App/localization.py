import requests
from geopy.geocoders import Nominatim

def localize_user():
    r = requests.get('https://api.ipgeolocation.io/ipgeo?apiKey=')
    result = r.json()
    localisation = str(result["city"]) + " - " + str(result["zipcode"])
    latitude = result["latitude"]
    longitude = result["longitude"]
    return(localisation, latitude, longitude)

def localize_text(loc):
    try:
        geolocator = Nominatim(user_agent="Matcha 42 school project app")
        new_loc = geolocator.geocode(str(loc)).raw
        print(new_loc['lat'])
        print(new_loc['lon'])
        print(new_loc['display_name'])
        if ", " in new_loc['display_name']:
            city_name = new_loc['display_name'].split(", ")[0].strip()
        else:
            city_name = new_loc['display_name'].strip()
        return float(new_loc['lat']), float(new_loc['lon']), str(city_name)
    except:
        return 0.0, 0.0, "ERROR - WRONG LOCALISATION"

