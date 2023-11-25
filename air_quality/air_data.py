import requests
from math import radians, sin, cos, sqrt, atan2
import json

class AirQuality:
    """
    Class for handling air quality data.

    Parameters:
    - config (dict): Configuration parameters for air quality.

    Attributes:
    - config (dict): Configuration parameters for air quality.
    - stations_json (list): List of stations with air quality data in JSON format.

    Methods:
    - calculate_distance: Calculates the distance between two points on a sphere.
    - find_nearest_station: Finds the identifier of the nearest station based on coordinates.
    - get_air_quality: Retrieves air quality data for specified coordinates.
    """

    def __init__(self, config):
        """
        Initializes the AirQuality object.

        Parameters:
        - config (dict): Configuration parameters for air quality.
        """
        self.config = config.air_pollution
        self.stations_json = json.load(open(self.config.sensor_list_data, "r", encoding="utf-8"))

    def calculate_distance(self, lat1, lon1, lat2, lon2):
        """
        Calculates the distance between two points on a sphere (in kilometers).

        Parameters:
        - lat1, lon1, lat2, lon2: Geographic coordinates of two points.

        Returns:
        - distance: Distance between the points in kilometers.
        """
        R = 6371.0  # Earth radius in kilometers
        lat1_rad = radians(lat1)
        lon1_rad = radians(lon1)
        lat2_rad = radians(lat2)
        lon2_rad = radians(lon2)

        dlon = lon2_rad - lon1_rad
        dlat = lat2_rad - lat1_rad

        a = sin(dlat / 2)**2 + cos(lat1_rad) * cos(lat2_rad) * sin(dlon / 2)**2
        c = 2 * atan2(sqrt(a), sqrt(1 - a))

        distance = R * c
        return distance


    def find_nearest_station(self, target_lat, target_lon):
        """
        Finds the identifier of the nearest station based on coordinates.

        Parameters:
        - target_lat, target_lon: Geographic coordinates of a location.

        Returns:
        - nearest_station_id: Identifier of the nearest station.
        """
        nearest_station_id = None
        min_distance = float('inf')
        for station in self.stations_json:
            station_lat = float(station["gegrLat"])
            station_lon = float(station["gegrLon"])

            distance = self.calculate_distance(float(target_lat), float(target_lon), station_lat, station_lon)

            if distance < min_distance:
                min_distance = distance
                nearest_station_id = station["id"]

        return nearest_station_id

    def get_air_quality(self, lat, lon):
        """
        Retrieves air quality data for specified coordinates.

        Parameters:
        - lat, lon: Geographic coordinates of a location.

        Returns:
        - dict: Air quality data.
        """
        if lat is None or lon is None:
            station_id = self.config.default_sensor_id
        else:
            station_id = self.find_nearest_station(lat, lon)

        if station_id is not None:
            try:
                response = requests.get(f'{self.config.air_pollution_url}{station_id}')
                if response.status_code == 200:
                    air_data = response.json()
                    return {
                        'air_quality': air_data[self.config.air_index_key][self.config.index_level],
                        'air_quality_id': air_data[self.config.air_index_key]['id'],
                        'extra_points': self.config.extra_points[air_data[self.config.air_index_key]['id']]
                    }

            except requests.RequestException as e:
                print(f"Request error: {e}")
