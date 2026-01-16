import sqlite3

DB_NAME = "parking_data.db"

def get_date_range():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    
    print(f"Analyse des dates dans {DB_NAME}...")
    
    # Check Car Parking
    try:
        cursor.execute("SELECT MIN(timestamp), MAX(timestamp), COUNT(*) FROM car_parking")
        result = cursor.fetchone()
        if result:
            car_min, car_max, car_count = result
            print("\n--- Parking Voitures ---")
            if car_count > 0:
                print(f"Nombre d'entrées : {car_count}")
                print(f"Début : {car_min}")
                print(f"Fin   : {car_max}")
            else:
                print("Aucune donnée.")
        
    except sqlite3.OperationalError as e:
        print(f"Erreur table voiture : {e}")

    # Check Bike Parking
    try:
        cursor.execute("SELECT MIN(timestamp), MAX(timestamp), COUNT(*) FROM bike_parking")
        result = cursor.fetchone()
        if result:
            bike_min, bike_max, bike_count = result
            print("\n--- Parking Vélos ---")
            if bike_count > 0:
                print(f"Nombre d'entrées : {bike_count}")
                print(f"Début : {bike_min}")
                print(f"Fin   : {bike_max}")
            else:
                print("Aucune donnée.")
            
    except sqlite3.OperationalError as e:
        print(f"Erreur table vélo : {e}")
        
    conn.close()

if __name__ == "__main__":
    get_date_range()
