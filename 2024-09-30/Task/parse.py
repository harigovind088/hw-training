import requests
from parsel import Selector
from pymongo import MongoClient
from requests.exceptions import ConnectionError, SSLError
import re

class WebParse:
    def __init__(self, db_name='agents_db', collection_name='agents_data'):
        # MongoDB connection
        self.client = MongoClient('mongodb://localhost:27017/')
        self.db = self.client[db_name]
        self.collection = self.db[collection_name]
        self.counter = 0

    def clean_text(self, text):
        # Clean up unwanted characters
        return text.replace(u'\u2019', "'") \
                   .replace(u'\u00a0', ' ') \
                   .replace(u'\u2026', '') \
                   .strip()

    def parse_product(self, website):
        try:
            response = requests.get(website, verify=False)  # Disable SSL verification
            response.raise_for_status()  # Raise an error for bad responses
            selector = Selector(text=response.text)

            # Extract descriptions using the provided XPaths
            agent_text = selector.xpath('//div[@class="site-home-page-agent-text"]/p/text() | //div[@class="site-home-page-agent-text"]/p[2]/text()').getall()
            about_content = selector.xpath('//div[@class="site-about-content"]//div[@class="site-cms-text"]/p/text()').getall()
            home_page_content = selector.xpath('//div[@class="site-home-page-content-text"]/p[1]/text() | //div[@class="site-home-page-content-text"]/p[2]/text()').getall()
            agent_content = selector.xpath('//div[@class="site-home-page-agent-content-text"]/text() | //div[@class="site-home-page-agent-content-text"]/p/text()').getall()
            about_text = selector.xpath('//div[@class="site-home-page-about-text"]/p/text()').getall()

            # Combine and clean extracted text
            combined_text = [
                *agent_text,
                *about_content,
                *home_page_content,
                *agent_content,
                *about_text
            ]
            description_text = ' '.join(self.clean_text(text) for text in combined_text if text.strip())

            # Update the corresponding MongoDB document with the description
            self.update_agent_description(website, description_text)

            self.counter += 1
            print(f"Fetched description for {website}")

        except (ConnectionError, SSLError) as e:
            print(f"Error fetching {website}: {e}")

    def update_agent_description(self, website, description):
        # Find the agent by website and update the description field
        result = self.collection.update_one({"website": website}, {"$set": {"description": description}})
        if result.modified_count > 0:
            print(f"Updated description for {website}")
        else:
            print(f"No agent found for website: {website}")

    def is_valid_url(self, url):
        return re.match(r'^https?://', url) is not None

    def parse_products(self):
        # Fetch websites from the MongoDB collection
        agents = self.collection.find({"website": {"$exists": True}})
        
        for agent in agents:
            website = agent.get("website")
            if not website or not self.is_valid_url(website):
                print(f"Skipping invalid website: {website}")
                continue
            self.parse_product(website)

        print("Finished processing all agents.")

        # Print descriptions for all agents
        self.print_agent_descriptions()

    def print_agent_descriptions(self):
        agents = self.collection.find({"website": {"$exists": True}})
        for agent in agents:
            description = agent.get("description", "")
            print(f"Description for {agent.get('website', 'N/A')}: '{description}'")

if __name__ == "__main__":
    parser = WebParse()
    parser.parse_products()
