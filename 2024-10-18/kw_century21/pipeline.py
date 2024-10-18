from pymongo import MongoClient
from settings import MONGO_DB, MONGO_COLLECTION_URL, MONGO_COLLECTION_DATA

class MongoDBPipeline:
    def __init__(self):
        self.client = MongoClient('mongodb://localhost:27017/')
        self.db = self.client[MONGO_DB]
        self.crawler_url_collection = self.db[MONGO_COLLECTION_URL]
        self.final_data_collection = self.db[MONGO_COLLECTION_DATA]

    def save_crawler_url(self, url):
        self.crawler_url_collection.insert_one({"profile_url": url})

    def fetch_crawler_urls(self):
        return self.crawler_url_collection.find({"profile_url": {"$exists": True}})

    def save_final_data(self, data):
        self.final_data_collection.insert_one(data)

    def update(self, profile_url, data):
        pass
