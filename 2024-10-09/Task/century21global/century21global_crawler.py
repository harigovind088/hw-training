import requests
import json
from scrapy import Selector
from setting import HEADERS, BASE_URL
from pipeline import MongoDBPipeline

class AgentScraper:
    def __init__(self, max_pages=75):
        self.pipeline = MongoDBPipeline()
        self.max_pages = max_pages


    def split_name(self, name):
        parts = name.split()
        
        if len(parts) > 3:
            first_name = parts[0] + ' ' + ' '.join(parts[1:])  
            middle_name = ''
            last_name = ''
        else:
            first_name = parts[0] if len(parts) > 0 else ''
            middle_name = ' '.join(parts[1:-1]) if len(parts) > 2 else ''
            last_name = parts[-1] if len(parts) > 1 else ''
        
        return first_name, middle_name, last_name


    def fetch_agents(self):
        for page in range(1, self.max_pages + 1):
            url = BASE_URL.format(page)
            response = requests.get(url=url, headers=HEADERS)

            if response.status_code == 200:
                selector = Selector(text=response.text)
                agent_links = selector.xpath('//a[@class="row gy-3 gy-lg-0 flex-fill"]/@href').getall()

                for link in agent_links:
                    agent_url = f"https://www.century21global.com{link}"
                    self.fetch_agent_details(agent_url)
                print(f"Fetched {len(agent_links)} agents from page {page}.")
            else:
                print(f"Failed to retrieve page {page}: Status code {response.status_code}")

    def fetch_agent_details(self, agent_url):
        agent_response = requests.get(agent_url, headers=HEADERS)
        agent_selector = Selector(text=agent_response.text)

        json_data = agent_selector.xpath("//pre/script/text()").get()
        if json_data:
            try:
                data = json.loads(json_data)
                name = data.get("name", "")
                first_name, middle_name, last_name = self.split_name(name)
                organization_name = data.get("parentOrganization", {}).get("name", "")
                image_url = data.get("image", "")
                languages = data.get("knowsLanguage", [])

                if isinstance(languages, str):
                    languages = [languages]
                elif not isinstance(languages, list):
                    languages = []

                agent_data = {
                    "first_name": first_name,
                    "middle_name": middle_name,
                    "last_name": last_name,
                    "office_name": organization_name,
                    "title": "",
                    "description": "",
                    "languages": languages,
                    "image_url": image_url,
                    "address": "",
                    "city": "",
                    "state": "",
                    "country": "",
                    "zipcode": "",
                    "office_phone_numbers": [],
                    "agent_phone_numbers": [],
                    "email": "",
                    "website": "",
                    "social": {},
                    "profile_url": agent_url
                }

                self.pipeline.insert_agent(agent_data)

            except json.JSONDecodeError:
                print(f"Error decoding JSON for {agent_url}")
        else:
            print(f"No JSON data found for {agent_url}")

if __name__ == "__main__":
    scraper = AgentScraper(max_pages=75)
    scraper.fetch_agents()
    print("Data has been fetched and stored in MongoDB.")
