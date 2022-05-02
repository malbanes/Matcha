# Importing Modules
from time import sleep
import numpy as np
import random
# Use 'conda install shapely' to import the shapely library.
from shapely.geometry import Polygon, Point
from geopy.geocoders import Nominatim
import geocoder


poly = Polygon([(51.09170677401565, 2.4334755625000115),
(48.35104723378386, -5.0811728749999885),
(46.56007878821072, -1.3548317198585025),
(43.445222916737386, -1.4737054084670165),
(43.33395411136464, 6.6551894436497605),
(49.29046221021668, 6.8739280457664975)])
geolocator = Nominatim(user_agent="https")


def polygon_random_points (poly, num_points):
    min_x, min_y, max_x, max_y = poly.bounds
    points = []
    while len(points) < num_points:
        random_point = Point([random.uniform(min_x, max_x), random.uniform(min_y, max_y)])
        if (random_point.within(poly)):
            points.append(random_point)
    return points

def main():
    # Choose the number of points desired. This example uses 20 points. 
    points = polygon_random_points(poly,5000)
    # Printing the results.
    for p in points:
        #location = geolocator.reverse(str(p.x)+","+str(p.y))
        x = f'{p.x:.5f}'
        y = f'{p.y:.5f}'
        try:
            location = geocoder.osm([x, y], method='reverse').json
            sleep(5)
            city = location.get('municipality')
            #address = location.raw['address']
            #city = location.raw.get('address').get('city')
            if city != None:
                print(p.x,",",p.y,", \'2022-05-02\', \'" + city + "\'),")
        except:
            #HHHHH
            pass

if __name__ == "__main__":
    main()