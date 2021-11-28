from pymongo import MongoClient


def get_client():
    url = "mongodb://localhost:27017"
    client_mongo = MongoClient(url)
    db_flights = client_mongo.flights

    return db_flights

def save_data(collection_name, flight_json):
    try:
        for flight in flight_json['flights']:
            mongo_client = get_client()
            flights_collection = mongo_client.collection_name
            flights_collection.insert_one(flight)
    except Exception as e:
        print(e)
