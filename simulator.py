import random
from datetime import datetime, timedelta

def run_simulation(num_scenarios: int, scenario_type: str, start: datetime, end: datetime):
    """
    Generates a time series dataset for power levels based on specified scenarios.

    Parameters:
    - num_scenarios (int): The number of scenarios to generate. Must be at least 1.
    - scenario_type (str): The type of scenario to simulate. Options are "summer peak", "winter peak", "light load".
    - start (datetime): The start datetime for the dataset.
    - end (datetime): The end datetime for the dataset.

    Returns:
    - list[dict]: A list of dictionaries, each containing:
        - 'scenario' (int): The scenario index.
        - 'datetime' (datetime): The timestamp for the power measurement.
        - 'power_MW' (float): The power level in megawatts.
    """
    
    if num_scenarios < 1:
        raise ValueError("The num_scenarios must be at least 1.")
    
    if start >= end:
        raise ValueError("The start time must be before the end time.")
    
    # Define power level ranges for each scenario type
    scenario_ranges = {
        "summer peak": (500, 1000),
        "winter peak": (400, 900),
        "light load": (200, 500),
    }
    
    # Validate the scenario type
    if scenario_type not in scenario_ranges:
        raise ValueError(f"Invalid scenario type: {scenario_type}")
    
    scenario_range = scenario_ranges[scenario_type]
    
    # Generate hourly time intervals between start and end
    delta = timedelta(hours=1)
    time_intervals = []
    current_time = start
    while current_time <= end:
        time_intervals.append(current_time)
        current_time += delta
    
    # Generate the dataset for each scenario
    data = []
    for scenario in range(num_scenarios):
        power = round(random.uniform(*scenario_range), 2)
        for dt in time_intervals:
            # Adjust power level randomly within the scenario range
            power = round(min(max(power + 10 * random.random(), scenario_range[0]), scenario_range[1]), 2)
            data.append({
                "scenario": scenario,
                "datetime": dt,
                "power_MW": power
            })
    
    return data

# Example usage
if __name__ == "__main__":
    simulation_results = run_simulation(
        num_scenarios=3,
        scenario_type="summer peak",
        start=datetime(2024, 11, 1, 0, 0),
        end=datetime(2024, 11, 2, 23, 59)
    )
    
    for record in simulation_results:
        print(record)
