import requests
import json
from scrapy import Selector
from pipeline import MongoDBPipeline

class AgentUpdater:
    def __init__(self):
        self.pipeline = MongoDBPipeline()

    def fetch_and_update_agents(self):
        agents = self.pipeline.collection.find()
        for agent in agents:
            agent_url = agent['profile_url']
            self.update_agent_details(agent_url, agent)

    def update_agent_details(self, agent_url, agent):
        agent_response = requests.get(agent_url)
        agent_selector = Selector(text=agent_response.text)

        address = agent_selector.xpath('//div[@class="fragment"]/text()').get(default='').strip()
        description = agent_selector.xpath('//p[@class="opacity-75 ng-star-inserted"]/text()').get(default='').strip()
        phone_numbers = agent_selector.xpath('//a[@class="fragment ng-star-inserted"]/@href').getall()
        agent_phone_numbers = [number.replace('tel:', '').strip() for number in phone_numbers]

        result = agent_selector.xpath('//pre[@class="ng-star-inserted"]/script/text()').get(default='')
        data = json.loads(result) if result else {}

        city = data.get("address", {}).get("addressLocality", '') or ""
        state = data.get("address", {}).get("addressRegion", '') or ""
        country = data.get("address", {}).get("addressCountry", '') or ""
        zipcode = data.get("address", {}).get("postalCode", '') or ""

        title = ''
        office_phone_numbers = []
        website = ''
        email = ''
        social = {}

        update_data = {
            "first_name": agent.get("first_name", ""),
            "middle_name": agent.get("middle_name", ""),
            "last_name": agent.get("last_name", ""),
            "office_name": agent.get("office_name", ""),
            "title": title,
            "description": description,
            "languages": agent.get("languages", []),
            "image_url": agent.get("image_url", ""),
            "address": address,
            "city": city,
            "state": state,
            "country": country,
            "zipcode": zipcode,
            "office_phone_numbers": office_phone_numbers,
            "agent_phone_numbers": agent_phone_numbers,
            "email": email,
            "website": website,
            "social": social,
            "profile_url": agent_url
        }

        self.pipeline.update_agent(agent_url, update_data)
        print(f"Updated agent details for {agent_url}")

if __name__ == "__main__":
    updater = AgentUpdater()
    updater.fetch_and_update_agents()
    print("Agent data has been updated in MongoDB.")
