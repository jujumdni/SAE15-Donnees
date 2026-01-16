import requests
import json
import sqlite3
import time
from datetime import datetime

DB_NAME = "parking_data.db"

def init_db():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS car_parking (
            id TEXT,
            name TEXT,
            availableSpotNumber INTEGER,
            totalSpotNumber INTEGER,
            status TEXT,
            timestamp DATETIME
        )
    ''')
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS bike_parking (
            id TEXT,
            address TEXT,
            availableBikeNumber INTEGER,
            freeSlotNumber INTEGER,
            totalSlotNumber INTEGER,
            status TEXT,
            timestamp DATETIME
        )
    ''')
    
    conn.commit()
    conn.close()

def scrape_and_save():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    timestamp = datetime.now()

    try:
        # Car Parking
        print(f"Scraping car parking data at {timestamp}...")
        response_car = requests.get("https://portail-api-data.montpellier3m.fr/offstreetparking")
        if response_car.status_code == 200:
            data_car = response_car.json()
            for item in data_car:
                name = item.get('name', {}).get('value')
                available = item.get('availableSpotNumber', {}).get('value')
                total = item.get('totalSpotNumber', {}).get('value')
                status = item.get('status', {}).get('value')
                
                cursor.execute('''
                    INSERT INTO car_parking (id, name, availableSpotNumber, totalSpotNumber, status, timestamp)
                    VALUES (?, ?, ?, ?, ?, ?)
                ''', (item.get('id'), name, available, total, status, timestamp))
        
        # Bike Parking
        print(f"Scraping bike parking data at {timestamp}...")
        response_bike = requests.get("https://portail-api-data.montpellier3m.fr/bikestation")
        if response_bike.status_code == 200:
            data_bike = response_bike.json()
            for item in data_bike:
                address_info = item.get('address', {}).get('value')
                address = address_info.get('streetAddress') if isinstance(address_info, dict) else str(address_info)
                available_bikes = item.get('availableBikeNumber', {}).get('value')
                free_slots = item.get('freeSlotNumber', {}).get('value')
                total_slots = item.get('totalSlotNumber', {}).get('value')
                status = item.get('status', {}).get('value')

                cursor.execute('''
                    INSERT INTO bike_parking (id, address, availableBikeNumber, freeSlotNumber, totalSlotNumber, status, timestamp)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                ''', (item.get('id'), address, available_bikes, free_slots, total_slots, status, timestamp))
        
        conn.commit()
        print("Data saved successfully.")
        
    except Exception as e:
        print(f"Error occurred: {e}")
    finally:
        conn.close()

if __name__ == "__main__":
    init_db()
    while True:
        scrape_and_save()
        print("Waiting for 1 minute...")
        time.sleep(60)