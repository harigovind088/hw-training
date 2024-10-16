import requests
from scrapy import Selector
from urllib.parse import urljoin
from pipeline import MongoDBPipeline
from settings import BASE_URL, HEADERS

class AgentScraper:
    def __init__(self):
        self.pipeline = MongoDBPipeline()
        self.agents = []

    def fetch_data(self, url):
        try:
            response = requests.get(url, headers=HEADERS)
            response.raise_for_status()
        except requests.exceptions.RequestException as e:
            print(f"Request failed: {e}")
            return None
        return response.text

    def parse_agents(self, html):
        sel = Selector(text=html)
        relative_urls = sel.xpath('//article[@class="rng-agent-roster-agent-card js-sort-item rng-agent-roster-agent"]/div[@class="rng-agent-roster-card-photo"]/a/@href').getall()
        names = sel.xpath("//h3[@class='rn-agent-roster-name js-sort-name']/text()[1]").getall()
        titles = sel.xpath("//h3[@class='rn-agent-roster-name js-sort-name']/span[@class='account-title']/text()").getall()
        image_urls = sel.xpath('//article[@class="rng-agent-roster-agent-card js-sort-item rng-agent-roster-agent"]//div[@class="rng-agent-roster-card-photo"]/a/img/@src').getall()
        agent_phone_numbers = sel.xpath("//li[a/span[text()='M']]/a/@href").getall()
        office_phone_numbers = sel.xpath("//li[a/span[text()='O']]/a/@href").getall()

        for name, relative_url, title, image_url, agent_phone, office_phone in zip(names, relative_urls, titles, image_urls, agent_phone_numbers, office_phone_numbers):
            full_url = urljoin(BASE_URL, relative_url)
            print(f"Fetching profile URL: {full_url}")

            name_parts = name.strip().split()
            first_name, middle_name, last_name = self.split_name(name_parts)

            agent_data = {
                "first_name": first_name,
                "middle_name": middle_name,
                "last_name": last_name,
                "office_name": "",
                "title": title.strip() if title else "",
                "description": "",
                "languages": [],
                "image_url": image_url,
                "address": "",
                "city": "",
                "state": "",
                "country": "United States",
                "zipcode": "",
                "office_phone_number": [office_phone.replace("tel:", "").strip() if office_phone else ""],
                "agent_phone_number": [agent_phone.replace("tel:", "").strip() if agent_phone else ""],
                "email": "",
                "website": "",
                "social": {
                    "facebook_url": "",
                    "twitter_url": "",
                    "linkedin_url": "",
                    "instagram_url": "",
                    "other_urls": []
                },
                "profile_url": full_url
            }

            self.agents.append(agent_data)
            self.pipeline.save_agent(agent_data)

    def split_name(self, name_parts):
        if len(name_parts) == 1:
            return name_parts[0], "", ""
        elif len(name_parts) == 2:
            return name_parts[0], "", name_parts[1]
        elif len(name_parts) == 3:
            return name_parts[0], name_parts[1], name_parts[2]
        else:
            return name_parts[0], "", " ".join(name_parts[1:])

    def scrape(self, url):
        html = self.fetch_data(url)
        if html:
            self.parse_agents(html)
        print(f'Total agents fetched and saved to MongoDB: {len(self.agents)}')

def main():
    scraper = AgentScraper()
    scraper.scrape("https://www.houlihanlawrence.com/roster/agents/0")

if __name__ == "__main__":
    main()
