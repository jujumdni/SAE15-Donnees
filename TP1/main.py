import requests
import json

response_car_parking=requests.get("https://portail-api-data.montpellier3m.fr/offstreetparking")
data_car_parking = response_car_parking.json()

response_bike_parking=requests.get("https://portail-api-data.montpellier3m.fr/bikestation")
data_bike_parking = response_bike_parking.json()

for item in data_car_parking:
    print(item)
    print("\n")

for item in data_bike_parking:
    print(item)
    print("\n")