from abc import ABC, abstractmethod
from  paid_parking_zones.calculator import PaidParkingZones
class MeansOfTransportRegistry:
    _registry = {}

    @classmethod
    def register(cls, transport_type):
        """
        Register a means of transport class.

        :param transport_type: Identifier for the means of transport.
        :return: The decorator function.
        """
        def decorator(klass):
            cls._registry[transport_type] = klass
            return klass

        return decorator

    @classmethod
    def get_transport(cls, transport_type):
        """
        Get a means of transport class based on its identifier.

        :param transport_type: Identifier for the means of transport.
        :return: The means of transport class or None if not found.
        """
        return cls._registry.get(transport_type, None)

def initialize_means_of_transport(transport_type: int,config):
    """
    Initialize a means of transport instance based on the provided transport type.

    :param transport_type: Identifier for the means of transport.
    :return: An instance of the means of transport or None if not found.
    """
    transport_class = MeansOfTransportRegistry.get_transport(transport_type)
    if transport_class:
        return transport_class(config)
    else:
        return None

class MeansOfTransport(ABC):
    """
    Abstract base class for means of transport.
    """

    def __init__(self,config):
        self.config = config.means_of_transport
    @abstractmethod
    def calculate_travel_cost(self, distance: float) -> float:
        """
        Calculate the cost for a single travel.

        :param distance: The distance of the travel.
        :return: The cost for the travel.
        """
        return NotImplementedError

    @abstractmethod
    def calculate_carbon_footprint(self, distance: float) -> float:
        """
        Calculate the CO2 emission for a trip.

        :param distance: The distance of the trip.
        :return: The CO2 emission for the trip.
        """
        return NotImplementedError

    def cost_summary(self, distance):
        """
        Calculate the cost and CO2 emission summary for a means of transport.

        :param distance: The distance of the trip.
        :return: A dictionary with 'cost' and 'co2' keys.
        """
        return {
            'cost': self.calculate_travel_cost(distance=distance),
            'co2': self.calculate_carbon_footprint(distance=distance)
        }

class Car(MeansOfTransport):
    """
    Class representing a car as a means of transport.
    """



    def __init__(self, avg_consumption: float | None, fuel_type: int | None, config):
        """
        Initialize the Car instance.

        :param avg_consumption: Average fuel consumption in liters per 100 km.
        :param fuel_type: Fuel type (0 for gasoline, 1 for diesel).
        """
        super().__init__(config)
        self.config = self.config.car
        self.fuel_type = fuel_type if fuel_type is not None else 0
        self.avg_consumption = float(avg_consumption) if avg_consumption is not None else self.config.default_avg_consumption
        self.emission = self.config.co2_emission[fuel_type]

    def calculate_carbon_footprint(self, distance: float) -> float:
        """
        Calculate the CO2 emission for a car trip.

        :param distance: The distance of the trip.
        :return: The CO2 emission for the trip.
        """
        emission = distance * self.emission
        return emission

    def calculate_travel_cost(self, distance: float, fuel_price_per_liter: float | None,
                              lon: float | None, lat: float | None, ppd: PaidParkingZones) -> float:
        """
        Calculate the travel cost for a car trip.

        :param distance: The distance of the trip.
        :param fuel_price_per_liter: Fuel price per liter (if None, use average fuel price).
        :param lon: Longitude coordinate of the destination.
        :param lat: Latitude coordinate of the destination.
        :param ppd: Instance of PaidParkingZones for checking paid parking zones.

        :return: The travel cost for the trip.
        """
        fuel_consumption_for_trip = (distance / 100) * self.avg_consumption
        fpl = self.config.default_avg_fuel_price[self.fuel_type] if fuel_price_per_liter is None else float(
            fuel_price_per_liter)
        travel_cost = fuel_consumption_for_trip * fpl
        if lat is not None and lon is not None:
            # Include the cost of paid parking if coordinates are provided
            travel_cost += ppd.check_price(latitude=lat, longitude=lon)

        return travel_cost

    def calculate_annual_travel_cost(self, daily_distance: float) -> float:
        """
        Calculate the annual travel cost for a car.

        :param daily_distance: The daily distance traveled.
        :return: The annual travel cost.
        """
        daily_fuel_consumption = (daily_distance / 100) * self.avg_consumption
        annual_fuel_consumption = daily_fuel_consumption * 365
        annual_travel_cost = annual_fuel_consumption * self.avg_consumption
        return annual_travel_cost

    def calculate_annual_co2_emission(self, daily_distance: float) -> float:
        """
        Calculate the annual CO2 emission for a car.

        :param daily_distance: The daily distance traveled.
        :return: The annual CO2 emission.
        """
        daily_fuel_consumption = (daily_distance / 100) * self.avg_consumption
        annual_fuel_consumption = daily_fuel_consumption * 365
        annual_co2_emission = annual_fuel_consumption * self.config.co2_emission[self.fuel_type]
        return annual_co2_emission

    def annual_summary(self, daily_distance):
        """
        Calculate the annual cost and CO2 emission summary for a car.

        :param daily_distance: The daily distance traveled.
        :return: A dictionary with 'cost' and 'co2' keys.
        """
        return {
            'cost': self.calculate_annual_travel_cost(float(daily_distance)),
            'co2': self.calculate_annual_co2_emission(float(daily_distance))/1000
        }

    def cost_summary(self, distance, fuel_price, lon, lat ,ppd):
        """
        Calculate the cost and CO2 emission summary for a car.

        :param distance: The distance of the trip.
        :param fuel_price: Fuel price per liter (if None, use average fuel price).
        :return: A dictionary with 'cost' and 'co2' keys.
        """
        return {
            'cost': self.calculate_travel_cost(distance=distance, fuel_price_per_liter=fuel_price,
                                               lon=lon, lat= lat ,ppd=ppd),
            'co2': self.calculate_carbon_footprint(distance=distance)
        }

@MeansOfTransportRegistry.register(0)
class Walking(MeansOfTransport):
    """
    Class representing walking as a means of transport.
    """

    def calculate_travel_cost(self, distance: float) -> float:
        """
        Calculate the cost for a walking trip.

        :param distance: The distance of the trip (irrelevant for walking).
        :return: The cost for the trip (always 0 for walking).
        """
        return 0

    def calculate_carbon_footprint(self, distance: float) -> float:
        """
        Calculate the CO2 emission for a walking trip.

        :param distance: The distance of the trip (irrelevant for walking).
        :return: The CO2 emission for the trip (always 0 for walking).
        """
        return 0

@MeansOfTransportRegistry.register(1)
class Bike(MeansOfTransport):
    def __init__(self, config):
        super().__init__(config)
        self.config = self.config.bike


    def calculate_carbon_footprint(self, distance: float) -> float:
        return 0

    def calculate_travel_cost(self, distance: float) -> float:
        driving_time = (distance / self.config.avg_speed)
        cost = self.config.price_per_hour * driving_time
        return cost


@MeansOfTransportRegistry.register(2)
class Scooter(MeansOfTransport):
    """
    Class representing a scooter as a means of transport.
    """

    def __init__(self, config):
        super().__init__(config)
        self.config = self.config.scooter


    def calculate_travel_cost(self, distance: float) -> float:
        """
        Calculate the travel cost for a scooter trip.

        :param distance: The distance of the trip.
        :return: The travel cost for the trip.
        """
        driving_time = (distance / self.config.avg_speed) / 60
        cost = self.config.start_price + self.config.cost_for_minute * driving_time
        return cost

    def calculate_carbon_footprint(self, distance: float) -> float:
        """
        Calculate the CO2 emission for a scooter trip.

        :param distance: The distance of the trip.
        :return: The CO2 emission for the trip.
        """
        energy_consumption = (distance/100) * self.config.avg_consumption
        co2_emission = energy_consumption * self.config.avg_co2_emission
        return co2_emission

@MeansOfTransportRegistry.register(3)
class BUS(MeansOfTransport):

    def calculate_travel_cost(self, distance: float) -> float:
        return 0

    def calculate_carbon_footprint(self, distance: float) -> float:
        return 0
