import sqlite3
import math
import unicodedata

DB_NAME = "parking_data.db"

# --- Fonctions utilitaires réutilisées de view_data.py ---
def normalize_string(s):
    return ''.join(c for c in unicodedata.normalize('NFD', s)
                  if unicodedata.category(c) != 'Mn').lower()

def is_match(name1, name2):
    n1 = normalize_string(name1)
    n2 = normalize_string(name2)
    
    if n1 == n2:
        return True
    if len(n1) > 3 and n1 in n2:
        return True
    if len(n2) > 3 and n2 in n1:
        return True
    return False

def get_shared_parkings():
    """Retourne une liste de dictionnaires pour les parkings qui ont à la fois des voitures et des vélos."""
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    
    car_parkings = []
    bike_parkings = []
    
    try:
        cursor.execute("SELECT DISTINCT name FROM car_parking ORDER BY name")
        car_parkings = [row[0] for row in cursor.fetchall()]
        
        cursor.execute("SELECT DISTINCT address FROM bike_parking ORDER BY address")
        bike_parkings = [row[0] for row in cursor.fetchall()]
    except sqlite3.OperationalError:
        print("Erreur: Impossible de lire la base de données. Assurez-vous qu'elle existe.")
        conn.close()
        return []
        
    conn.close()
    
    shared_parkings = []
    used_bikes = set()
    
    for car_name in car_parkings:
        for bike_name in bike_parkings:
            if bike_name in used_bikes:
                continue
                
            if is_match(car_name, bike_name):
                shared_parkings.append({
                    'display_name': car_name, 
                    'car_name': car_name,
                    'bike_name': bike_name
                })
                used_bikes.add(bike_name)
                break
    
    return shared_parkings

# --- Fonctions d'analyse statistique ---

def calculate_mean(data):
    if not data:
        return 0.0
    return sum(data) / len(data)

def calculate_correlation(x, y):
    """Calcule le coefficient de corrélation de Pearson entre deux listes."""
    if len(x) != len(y) or len(x) < 2:
        return 0.0

    n = len(x)
    mean_x = calculate_mean(x)
    mean_y = calculate_mean(y)

    numerator = sum((xi - mean_x) * (yi - mean_y) for xi, yi in zip(x, y))
    
    sum_sq_diff_x = sum((xi - mean_x) ** 2 for xi in x)
    sum_sq_diff_y = sum((yi - mean_y) ** 2 for yi in y)
    
    denominator = math.sqrt(sum_sq_diff_x) * math.sqrt(sum_sq_diff_y)
    
    if denominator == 0:
        return 0.0
        
    return numerator / denominator

def get_paired_data(car_name, bike_name):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    
    # Nous joignons sur le timestamp pour nous assurer de comparer le moment exact
    query = """
        SELECT 
            c.availableSpotNumber, 
            c.totalSpotNumber,
            b.availableBikeNumber, 
            b.totalSlotNumber,
            c.timestamp
        FROM car_parking c
        JOIN bike_parking b ON c.timestamp = b.timestamp
        WHERE c.name = ? AND b.address = ?
        ORDER BY c.timestamp
    """
    
    cursor.execute(query, (car_name, bike_name))
    rows = cursor.fetchall()
    conn.close()
    
    # Décompression dans des listes
    car_avail = []
    car_total = []
    bike_avail = []
    bike_total = []
    
    for r in rows:
        # Parfois les requêtes peuvent échouer et retourner None, filtrer les données valides
        if r[0] is not None and r[2] is not None:
            car_avail.append(r[0])
            car_total.append(r[1])
            bike_avail.append(r[2])
            bike_total.append(r[3])
            
    return car_avail, car_total, bike_avail, bike_total

def analyze_parking(parking):
    print(f"\n{'='*20} Analyse : {parking['display_name']} {'='*20}")
    
    car_avail, car_total, bike_avail, bike_total = get_paired_data(parking['car_name'], parking['bike_name'])
    
    count = len(car_avail)
    if count < 2:
        print("Pas assez de données pour calculer les statistiques.")
        return

    # Statistiques basiques
    avg_car = calculate_mean(car_avail)
    avg_bike = calculate_mean(bike_avail)
    
    # Calcul de l'occupation (Occupation = 1 - (Disponible / Total))
    mean_car_capacity = calculate_mean(car_total)
    mean_bike_capacity = calculate_mean(bike_total)
    
    car_occupancy_pct = (1 - (avg_car / mean_car_capacity)) * 100 if mean_car_capacity > 0 else 0
    bike_occupancy_pct = (1 - (avg_bike / mean_bike_capacity)) * 100 if mean_bike_capacity > 0 else 0

    print(f"Points de données analysés : {count}")
    print(f"Dispo Voiture Moy : {avg_car:.1f} / {mean_car_capacity:.0f} places")
    print(f"Occupation Voiture: {car_occupancy_pct:.1f}%")
    print(f"Dispo Vélo Moy :    {avg_bike:.1f} / {mean_bike_capacity:.0f} vélos")
    print(f"Occupation Vélo :   {bike_occupancy_pct:.1f}%")

    # Corrélation
    correlation = calculate_correlation(car_avail, bike_avail)
    
    print(f"\nCorrélation entre dispo Voiture et Vélo : {correlation:.4f}")
    
    interpretation = ""
    if abs(correlation) < 0.1:
        interpretation = "Pas de relation (Indépendant)"
    elif abs(correlation) < 0.3:
        interpretation = "Relation faible"
    elif abs(correlation) < 0.5:
        interpretation = "Relation modérée"
    else:
        interpretation = "Relation forte"
        
    direction = "positive" if correlation > 0 else "négative"
    
    if abs(correlation) >= 0.1:
        print(f"-> Cela signifie qu'il y a une {interpretation} ({direction}).")
    else:
        print(f"-> {interpretation}")

    # Analyse Parc Relais (Intermodalité)
    print("\n--- Analyse 'Parc Relais' ---")
    
    # Pour un Parc Relais, on s'attend à ce que quand les gens garent leur voiture (Dispo Voiture Baisse),
    # ils prennent un vélo (Dispo Vélo Baisse).
    # Donc les deux courbes devraient descendre et monter ensemble.
    # C'est une corrélation POSITIVE.
    
    if correlation > 0.3:
        print("✅ POSITIF : Cela ressemble à un Parc Relais qui fonctionne.")
        print("   (Les disponibilités varient ensemble : Voitures garées = Vélos empruntés).")
    elif correlation < -0.3:
        print("❌ NEGATIF : Ne semble pas fonctionner comme un relais Car->Vélo.")
        print("   (Le compotement est inversé: Parking plein = Station vélo pleine).")
    else:
        print("❓ NEUTRE : Pas de lien évident détecté pour l'instant.")

def main():
    print("Recherche des parkings partagés (Voiture & Vélo)...")
    shared = get_shared_parkings()
    
    if not shared:
        print("Aucun parking partagé trouvé.")
        return
        
    print(f"{len(shared)} lieux partagés trouvés.")
    
    for parking in shared:
        analyze_parking(parking)

if __name__ == "__main__":
    main()
