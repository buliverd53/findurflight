from pymongo import MongoClient


def get_client():
    url = "mongodb://localhost:27017"
    client_mongo = MongoClient(url)
    db_flights = client_mongo.flights

    return db_flights
