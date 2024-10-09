from pymongo import MongoClient
from setting import MONGO_URI, DB_NAME, COLLECTION_NAME

class MongoDBPipeline:
    def __init__(self):
        self.client = MongoClient(MONGO_URI)
        self.db = self.client[DB_NAME]
        self.collection = self.db[COLLECTION_NAME]

    def insert_agent(self, agent_data):
        self.collection.insert_one(agent_data)

    def update_agent(self, profile_url, update_data):
        self.collection.update_one({'profile_url': profile_url}, {'$set': update_data})
