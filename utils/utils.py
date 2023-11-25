

def calculate_cost_co2_difference(car_calculation, selected_transport_calculation):
    if 'cost' in car_calculation and 'co2' in car_calculation and 'cost' in selected_transport_calculation and 'co2' in selected_transport_calculation:
        cost_difference = car_calculation['cost'] - selected_transport_calculation['cost']
        co2_difference = car_calculation['co2'] - selected_transport_calculation['co2']
        return {'cost_difference': cost_difference, 'co2_difference': co2_difference}
    else:
        return None  # Handle the case where one or both dictionaries don't have the expected keys