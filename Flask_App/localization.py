import requests

def localize_user():
    r = requests.get('https://api.ipgeolocation.io/ipgeo?apiKey=4b18db3b647a4102993fefd9a710bfb5')
    result = r.json()
    localisation = str(result["city"]) + " - " + str(result["zipcode"])
    latitude = result["latitude"]
    longitude = result["longitude"]
    return(localisation, latitude, longitude)
