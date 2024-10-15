from pymongo import MongoClient

# Initialize MongoDB client
client = MongoClient("mongodb://localhost:27017/")
db = client["propertyfinder_monthly_2024_10"]
properties_collection = db["wasalt_ksa"]

def save_property_data(property_data):
    properties_collection.insert_one(property_data)

def update_property_data(url, property_data):
    properties_collection.update_one({"url": url}, {"$set": property_data}, upsert=True)

def fetch_urls():
    return list(properties_collection.find({}, {"url": 1}))
