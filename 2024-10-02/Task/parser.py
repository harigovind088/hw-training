import time
import requests
from pymongo import MongoClient
from scrapy import Selector

class AgentDetailUpdater:
    def __init__(self, mongo_uri, db_name, collection_name):
        self.client = MongoClient(mongo_uri)
        self.db = self.client[db_name]
        self.collection = self.db[collection_name]

        self.headers = {
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7",
            "Accept-Language": "en-GB,en-US;q=0.9,en;q=0.8",
            "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/128.0.0.0 Safari/537.36",
            "sec-ch-ua": "\"Chromium\";v=\"128\", \"Not;A=Brand\";v=\"24\", \"Google Chrome\";v=\"128\"",
            "sec-ch-ua-mobile": "?0",
            "sec-ch-ua-platform": "\"Linux\""
        }

    def fetch_agent_details(self):
        agents = self.collection.find({"Website": {"$ne": ""}})  
        total_agents = self.collection.count_documents({"Website": {"$ne": ""}})
        print(f"Found {total_agents} agents with valid website URLs.")

        for idx, agent in enumerate(agents, start=1):
            website_url = agent.get("Website")
            if website_url:
                print(f"Fetching details for agent {idx}/{total_agents}: {website_url}")
                self.update_agent_info(website_url, agent["_id"])

    def update_agent_info(self, website_url, agent_id, retries=3, delay=5):
        for attempt in range(retries):
            try:
                response = requests.get(website_url, headers=self.headers) 
                response.raise_for_status()  
                selector = Selector(text=response.text)

                address = selector.xpath("//div[@class='footer-top-left']//address/text()[1]").get(default="").strip()
                city_state_zip = selector.xpath("//div[@class='footer-top-left']//address/text()[2]").get(default="").strip()
                description = selector.xpath("//*[contains(@class,'about-widget-dscription')]//text()").get(default="").strip()

                city, state, zipcode = "", "", ""
                if city_state_zip:
                    parts = city_state_zip.split(',')
                    if len(parts) == 2:
                        city = parts[0].strip()
                        state_zip_parts = parts[1].strip().split()
                        if state_zip_parts:
                            state = state_zip_parts[0].strip()
                            zipcode = state_zip_parts[1].strip() if len(state_zip_parts) > 1 else ""
                        else:
                            state = ""
                            zipcode = ""
                else:
                    state = zipcode = ""

                update_data = {
                    "Address": address,
                    "City": city,
                    "State": state,
                    "Zipcode": zipcode,
                    "Description": description
                }
                self.collection.update_one({"_id": agent_id}, {"$set": update_data})
                print(f"Updated agent ID {agent_id} with new details.")
                return  

            except requests.exceptions.HTTPError as e:
                if response.status_code == 403:
                    print(f"Access denied for {website_url}. Attempt {attempt + 1}/{retries}. Retrying in {delay} seconds...")
                    time.sleep(delay)  
                else:
                    print(f"HTTP error {response.status_code} for {website_url}: {e}")
                    break
            except Exception as e:
                print(f"Error fetching details for {website_url}: {e}")
                break

if __name__ == "__main__":
    mongo_uri = 'mongodb://localhost:27017/'  
    db_name = 'agents_db'  
    collection_name = 'second'  
    updater = AgentDetailUpdater(mongo_uri, db_name, collection_name)
    updater.fetch_agent_details()
