import sqlite3
import matplotlib.pyplot as plt
from datetime import datetime
import sys
import unicodedata

DB_NAME = "parking_data.db"

def normalize_string(s):
    return ''.join(c for c in unicodedata.normalize('NFD', s)
                  if unicodedata.category(c) != 'Mn').lower()

def is_match(name1, name2):
    n1 = normalize_string(name1)
    n2 = normalize_string(name2)
    
    if n1 == n2:
        return True
    # Check for containment but ensure it's significant
    if len(n1) > 3 and n1 in n2:
        return True
    if len(n2) > 3 and n2 in n1:
        return True
    return False

def get_all_parkings():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    
    car_parkings = []
    bike_parkings = []
    
    # Get Car Parkings
    try:
        cursor.execute("SELECT DISTINCT name FROM car_parking ORDER BY name")
        car_parkings = [row[0] for row in cursor.fetchall()]
    except sqlite3.OperationalError:
        pass 

    # Get Bike Parkings
    try:
        cursor.execute("SELECT DISTINCT address FROM bike_parking ORDER BY address")
        bike_parkings = [row[0] for row in cursor.fetchall()]
    except sqlite3.OperationalError:
        pass
        
    conn.close()
    
    merged_parkings = []
    used_bikes = set()
    
    # Try to match cars with bikes
    for car_name in car_parkings:
        match_found = False
        for bike_name in bike_parkings:
            if bike_name in used_bikes:
                continue
                
            if is_match(car_name, bike_name):
                merged_parkings.append({
                    'type': 'Both',
                    'display_name': f"{car_name}", 
                    'car_name': car_name,
                    'bike_name': bike_name
                })
                used_bikes.add(bike_name)
                match_found = True
                break
        
        if not match_found:
            merged_parkings.append({
                'type': 'Car',
                'display_name': car_name,
                'name': car_name
            })
            
    # Add remaining bikes
    for bike_name in bike_parkings:
        if bike_name not in used_bikes:
            merged_parkings.append({
                'type': 'Bike',
                'display_name': bike_name,
                'name': bike_name
            })
            
    # Sort by display name
    merged_parkings.sort(key=lambda x: x['display_name'])
    return merged_parkings

def get_parking_data(parking_name, parking_type):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    
    if parking_type == 'Car':
        query = """
            SELECT timestamp, availableSpotNumber 
            FROM car_parking 
            WHERE name = ? 
            ORDER BY timestamp
        """
    else: # Bike
        query = """
            SELECT timestamp, availableBikeNumber 
            FROM bike_parking 
            WHERE address = ? 
            ORDER BY timestamp
        """
        
    cursor.execute(query, (parking_name,))
    data = cursor.fetchall()
    conn.close()
    return data

def process_data(raw_data):
    timestamps = []
    values = []
    for ts_str, val in raw_data:
        try:
            ts = datetime.strptime(ts_str, "%Y-%m-%d %H:%M:%S.%f")
        except ValueError:
            try:
                ts = datetime.strptime(ts_str, "%Y-%m-%d %H:%M:%S")
            except ValueError:
                continue
        timestamps.append(ts)
        values.append(val)
    return timestamps, values

def main():
    print("Fetching parking list...")
    parkings = get_all_parkings()

    if not parkings:
        print(f"No parking data found in {DB_NAME}. Make sure to run scraper.py first.")
        return

    print("\nAvailable Parkings:")
    for i, p in enumerate(parkings):
        if p['type'] == 'Both':
            print(f"{i + 1}. [Car & Bike] {p['display_name']}")
        else:
            print(f"{i + 1}. [{p['type']}] {p['display_name']}")

    while True:
        try:
            selection = input("\nEnter the number of the parking you want to view (or 'q' to quit): ")
            if selection.lower() == 'q':
                return
            
            index = int(selection) - 1
            if 0 <= index < len(parkings):
                selected_parking = parkings[index]
                break
            else:
                print("Invalid number. Please try again.")
        except ValueError:
            print("Invalid input. Please enter a number.")

    p_type = selected_parking['type']
    
    # We need to handle the figure creation differently for single vs dual plots
    
    if p_type == 'Both':
        print(f"\nFetching data for Car parking '{selected_parking['car_name']}'...")
        car_data = get_parking_data(selected_parking['car_name'], 'Car')
        print(f"Fetching data for Bike parking '{selected_parking['bike_name']}'...")
        bike_data = get_parking_data(selected_parking['bike_name'], 'Bike')
        
        ts_car, val_car = process_data(car_data)
        ts_bike, val_bike = process_data(bike_data)
        
        fig, ax1 = plt.subplots(figsize=(12, 6))
        
        color = 'tab:blue'
        ax1.set_xlabel('Time')
        ax1.set_ylabel('Available Car Spots', color=color)
        ax1.plot(ts_car, val_car, color=color, marker='o', linestyle='-', label='Car Spots')
        ax1.tick_params(axis='y', labelcolor=color)
        ax1.grid(True)
        
        ax2 = ax1.twinx()  # instantiate a second axes that shares the same x-axis
        
        color = 'tab:green'
        ax2.set_ylabel('Available Bike Spots', color=color)  # we already handled the x-label with ax1
        ax2.plot(ts_bike, val_bike, color=color, marker='x', linestyle='--', label='Bike Spots')
        ax2.tick_params(axis='y', labelcolor=color)
        
        plt.title(f"Available Spaces Over Time: {selected_parking['display_name']}")
        fig.tight_layout()  # otherwise the right y-label is slightly clipped
        
    else:
        plt.figure(figsize=(12, 6))
        name = selected_parking['name']
        print(f"\nFetching data for {p_type} parking '{name}'...")
        data = get_parking_data(name, p_type)
        ts, val = process_data(data)
        
        color = 'b' if p_type == 'Car' else 'g'
        label = "Available Spots" if p_type == 'Car' else "Available Bikes"
        
        plt.plot(ts, val, marker='o', linestyle='-', color=color)
        plt.title(f"{label} Over Time: {name}")
        plt.xlabel("Time")
        plt.ylabel(label)
        plt.grid(True)
        plt.xticks(rotation=45)
        plt.tight_layout()

    print("Displaying graph...")
    plt.show()

if __name__ == "__main__":
    main()
