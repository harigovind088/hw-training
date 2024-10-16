from pymongo import MongoClient
from settings import DB_NAME, COLLECTION_NAME

class MongoDBPipeline:
    def __init__(self):
        self.client = MongoClient('mongodb://localhost:27017/') 
        self.db = self.client[DB_NAME]
        self.collection = self.db[COLLECTION_NAME]

    def save_agent(self, agent_data):
        self.collection.insert_one(agent_data)

    def update_agent(self, bio_url, data):
        self.collection.update_one({"profile_url": bio_url}, {"$set": data})

    def fetch_profile_urls(self):
        return self.collection.find({}, {"profile_url": 1})
