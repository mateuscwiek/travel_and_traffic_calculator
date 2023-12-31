# Traffic and Travel Calculator


## Installation


1. Install dependencies:

    ```bash
    pip install -r requirements.txt
    ```

## Usage

1. Run the Flask application:

    ```bash
    python app.py
    ```

2. Access the following endpoints:

    - **Get Traffic Data**: 
        - Endpoint: `http://localhost:5000/get_traffic`
        - Method: `GET`
        - Parameters:
            - `hour` (integer): The hour for which traffic data is requested.
            - `day_of_week` (string): The day of the week for which traffic data is requested.
        - Response: JSON with traffic data.

    - **Get Current Traffic Data**: 
        - Endpoint: `http://localhost:5000/get_current_traffic`
        - Method: `GET`
          - Response: JSON with current traffic data.
   -    **Get Annual Saving Summary**: 
        - Endpoint: `http://localhost:5000/get_annual_saving`
        - Method: `GET`
        - Parameters:
            - `avg_consumption` (float, optional): Average fuel consumption in liters per 100 km for a car.
            - `fuel_type` (integer, optional): Fuel type (0 for gasoline, 1 for diesel) for a car.
            - `daily_distance` (float, optional): The daily distance traveled for a car.
        - Response: JSON with annual cost and CO2 emission savings.
        
    - **Get Saving for Travel**: 
        - Endpoint: `http://localhost:5000/get_saving_for_travel`
        - Method: `GET`
        - Parameters:
            - `transport_type` (integer): Identifier for the means of transport.
            - `distance` (float): The distance of the travel.
            - `avg_consumption` (float, optional): Average fuel consumption in liters per 100 km for a car.
            - `fuel_type` (integer, optional): Fuel type (0 for gasoline, 1 for diesel) for a car.
            - `fuel_price` (float, optional): Fuel price per liter for a car.
            - `lon` (float, optional): Longitude coordinate for paid parking calculation.
            - `lat` (float, optional): Latitude coordinate for paid parking calculation.
      - Response: JSON with cost and CO2 emission savings

      - **Get Air Quality**:
          - Endpoint: `http://localhost:5000/get_air_quality`
          - Method: `GET`
          - Parameters:
              - `lat` (float): Latitude of the location.
              - `lon` (float): Longitude of the location.
          - Response: JSON with air quality data
            Example:
            ```json
            {
              "air_quality": "Dobry",
              "air_quality_id": 1,
              "extra_points": 0
            }
            ```
            where 'air_quality' represents the air quality level and 'air_quality_id'
            ranges from 0 (best) to 5 (worst). 'extra_points' depends of air quality worse = more points

## How it works

1. Cost and CO2 emission calculator



- Travel cost and CO2 emission savings.

To calculate saving for specific travel we first calculate emission and cost for selected means of transport (walking,bike, scooter or bus)

Assumptions for Individual Modes of Transport:
- **Walking:**
  - Emission: Zero emission
  - Cost: Zero cost

- **Bike:**
  - Emission: Zero emission
  - Cost: Based on Blinkee pricing in Rzeszów

- **Scooter:**
  - Emission: Based on the average CO2 emission for scooters (g/kWh/100km)
  - Cost: Based on Blinkee pricing in Rzeszów

- **Bus:**
  - Emission: Zero emission (assuming the bus will drive anyway, so as a user, you do not generate a carbon footprint)
  - Cost: Zero (we assume that the user has a standing ticket). In the next phase, we can also involve ticket pricing.


Then we calculate cost and emission for car based on engine type, average fuel consumption and fuel price. 
Average CO2 emission per 100 km for combustion engines vehicles was taken as average split between gasoline and diesel engine.

We also include paid parking zones in city. Based on .shp files for Rzeszów there is a function which calculate if for 
specific destination (lat,lng) we are in paid parking zone and what zone ("Podstrefa"). 

![PPZ](paid_parking_zones/images/ppd.png "")

We have pricing for each zone and this value to total price. We assume that user stay 1 hour in paid parking zone.


Then we subtract cost for car and selected means of transport to calculate total savings

- Annual savings

We provide function to calculate total annual saving (cost and CO2 emission) selecting alternative means of transport

Based on daily average distance covered bu user we calculate total annual cost (fuel) and CO2 emission.



2. Current traffic volume

Based on measured data traffic flow in Rzeszów from OpenData we extract information on traffic volume for specific weekday and hour.
We use current traffic volume to estimate scoring rate

- Data processing

You can follow the process with saved jupyter notebook checkpoints:

    
    jupyter notebook traffic_intensity/data_parser.ipynb
    


First we analyse how it looks for selected street

![Traffic flow example for specific day](traffic_intensity/images/example_traffic.png "")


Then we normalize data from 0 to 1 for selected street

![Traffic flow normalized](traffic_intensity/images/values.png "")


Then we calculate average traffic volume for every weekday and hour

![Global traffic](traffic_intensity/images/global_traffic.png "")


Data were saved in csv: 

    traffic_intensity/data/global_avarage_traffic.csv


- Get current traffic

We provide function to calculate current traffic (value from 0 to 1) based on specific hour and weekday.
This normalized traffic volume is used as score ratio. 


3. Air quality - extra points

Because we want to encourage users to use communication, especially when the air quality is poor, or to engage in outdoor activities when the weather is good. 
Based on the API "https://powietrze.gios.gov.pl/pjp/content/api," we have prepared an analysis of air quality for a specific location 
(if no location is provided, the default is the air quality for Piłsudskiego Street in Rzeszów). 
The endpoint returns information about air quality based on the nearest sensor in the area and extra points for using public transport.