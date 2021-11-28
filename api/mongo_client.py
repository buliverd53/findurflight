import json
from pymongo import MongoClient
from bson import json_util, ObjectId


url = "mongodb://localhost:27017"

def save_data(collection_name, flight_json):
    try:
        client = MongoClient(url)
        client_collection = client[collection_name]
        for flight in flight_json['flights']:
            client_collection.insert_one(flight)
    except Exception as e:
        print(e)

def get_data(db_name):
    flights_data = []
    mongo_client = MongoClient(url)
    schema_client = mongo_client[db_name]
    client_collection = schema_client[db_name]
    flights = client_collection.find()
    for i in flights:
        flights_data.append(i)
    page_sanitized = json.loads(json_util.dumps(flights_data))
    return page_sanitized
