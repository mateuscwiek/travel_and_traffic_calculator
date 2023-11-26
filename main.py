from flask import Flask, request, jsonify
from means_of_transport import initialize_means_of_transport, MeansOfTransport, Car
from utils.utils import *
import pandas as pd
from paid_parking_zones.calculator import PaidParkingZones
from hydra import initialize, compose
from datetime import datetime
from air_quality.air_data import AirQuality

app = Flask(__name__)
initialize(version_base=None, config_path="conf", job_name="test")
config = compose(config_name='config')

df = pd.read_csv(config.traffic.average_traffic_file)
ppz = PaidParkingZones(config)
air_quality = AirQuality(config)

@app.route('/get_traffic', methods=['GET'])
def get_traffic():
    """
    Get traffic data based on the provided hour and day of the week.

    :return: JSON response with traffic data.
    """
    cfg = config.traffic
    hour = int(request.args.get(cfg.params.hour))
    day_of_week = request.args.get(cfg.params.day_of_week)
    result = df[(df[cfg.hour] == hour) & (df[cfg.day_of_week] == day_of_week)]

    if result.empty:
        return jsonify({"error": "No data found for the provided parameters."}), 404
    traffic_result = {
        config.traffic.traffic_result: round(result.values[0][0],2)
    }
    return jsonify(traffic_result)


@app.route('/get_current_traffic', methods=['GET'])
def get_current_traffic():
    """
    Get current traffic data based on the current hour and day of the week.

    :return: JSON response with current traffic data.
    """
    current_time = datetime.now()
    current_hour = current_time.hour
    current_day_of_week = current_time.strftime('%A')
    result = df[(df[config.traffic.hour] == current_hour) & (df[config.traffic.day_of_week] == current_day_of_week)]

    if result.empty:
        return jsonify({"error": "No data found for the current time."}), 404
    traffic_result = {
        config.traffic.traffic_result: round(result.values[0][0],2)
    }
    return jsonify(traffic_result)


@app.route('/get_saving_for_travel', methods=['GET'])
def get_saving_for_travel():
    """
    Get cost and CO2 emission savings for a given means of transport.

    :return: JSON response with cost and CO2 emission savings compare to car.
    """
    cfg_params = config.means_of_transport.params
    transport_type = int(request.args.get(cfg_params.transport_type.value, cfg_params.transport_type.default))
    distance = float(request.args.get(cfg_params.distance.value, cfg_params.distance.default))
    car_avg_consumption = request.args.get(cfg_params.avg_consumption.value, cfg_params.avg_consumption.default)
    fuel_type = request.args.get(cfg_params.fuel_type.value, cfg_params.fuel_type.default)
    fuel_price = request.args.get(cfg_params.fuel_price.value, cfg_params.fuel_price.default)
    lon = request.args.get(cfg_params.lon.value,cfg_params.lon.default)
    lat = request.args.get(cfg_params.lat.value,cfg_params.lat.default)
    # Calculate CO2 and cost for the selected transport type
    transport: MeansOfTransport | None = initialize_means_of_transport(transport_type, config)

    if transport is None:
        return jsonify({'error': 'Invalid transport type'}), 404

    transport_summary_cost = transport.cost_summary(distance)

    car_transport = Car(car_avg_consumption, fuel_type, config)
    car_summary_cost = car_transport.cost_summary(distance, fuel_price,lon,lat,ppz)

    savings = calculate_cost_co2_difference(car_summary_cost, transport_summary_cost)

    if savings is not None:
        return jsonify(savings)
    else:
        return jsonify({'error': 'Invalid data or missing keys'}), 404


@app.route('/get_annual_saving', methods=['GET'])
def get_annual_saving_summary():
    """
    Get annual cost and CO2 emission for a car.

    :return: JSON response with annual cost and CO2 emission savings.
    """
    cfg_params = config.means_of_transport.params
    avg_consumption = request.args.get(cfg_params.avg_consumption.value, cfg_params.avg_consumption.default)
    fuel_type = request.args.get(cfg_params.fuel_type.value, cfg_params.fuel_type.default)
    daily_distance = request.args.get(cfg_params.daily_distance.value, cfg_params.daily_distance.default)
    car = Car(avg_consumption, fuel_type, config)
    annual_summary = car.annual_summary(daily_distance)

    if annual_summary is not None:
        return jsonify(annual_summary)
    else:
        return jsonify({'error': 'Invalid data or missing keys'}), 404



@app.route('/get_air_quality', methods=['GET'])
def get_air_quality():
    """
    Endpoint for retrieving air quality data based on provided latitude and longitude.

    Query Parameters:
    - lat (float): Latitude of the location.
    - lon (float): Longitude of the location.

    Returns:
    - JSON: Air quality data in the specified format.
      Example:
      {
        "air_quality": "Dobry",
        "air_quality_id": 1,
        "extra_points" : 0
      }
      where 'air_quality' represents the air quality level and 'air_quality_id'
      ranges from 0 (best) to 5 (worst).
    """
    lat = request.args.get(config.air_pollution.params.lat, None)
    lon = request.args.get(config.air_pollution.params.lon, None)

    # Get air quality data based on provided coordinates if None we teke default for Rzeszów
    result = air_quality.get_air_quality(lat, lon)

    # Check if the result is not None
    if result is not None:
        return jsonify(result)
if __name__ == '__main__':
    app.run(debug=True)
