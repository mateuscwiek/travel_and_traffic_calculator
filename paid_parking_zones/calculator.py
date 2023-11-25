from shapely.geometry import Point
import pyproj
import geopandas as gpd
class PaidParkingZones:
    """
    Class for handling paid parking zones and prices.

    Attributes:
        config (Config): Configuration object containing paid parking settings.
        gdf_zones (geopandas.GeoDataFrame): GeoDataFrame containing paid parking zones.

    Methods:
        convert_coordinates: Convert coordinates from the input format to the output format.
        check_price: Check the parking price for a given set of coordinates.
    """

    def __init__(self, config):
        """
        Initializes the PaidParkingZones class.

        Args:
            config (Config): Configuration object containing paid parking settings.
        """
        self.config = config.paid_parking
        self.gdf_zones = gpd.read_file(self.config.data)

    def convert_coordinates(self, longitude, latitude):
        """
        Convert coordinates from the input format to the output format.

        Args:
            longitude (float): Longitude coordinate.
            latitude (float): Latitude coordinate.

        Returns:
            shapely.geometry.Point: Converted Point object.
        """
        point = f"{longitude} {latitude}"
        x, y = map(float, point.split())
        transformer = pyproj.Transformer.from_crs(
            self.config.input_coordinates_format,
            self.config.output_coordinates_format,
            always_xy=True
        )
        lon, lat = transformer.transform(x, y)
        return Point(lon, lat)

    def check_price(self, longitude, latitude):
        """
        Check the parking price for a given set of coordinates.

        Args:
            longitude (float): Longitude coordinate.
            latitude (float): Latitude coordinate.

        Returns:
            float: Parking price in PLN.
        """
        point = self.convert_coordinates(longitude, latitude)
        found_zone = None
        for index, row in self.gdf_zones.iterrows():
            if row["geometry"].contains(point):
                found_zone = row["Podstrefa"]
                break
        if found_zone is not None:
            return self.config.parking_price[found_zone]
        else:
            return 0