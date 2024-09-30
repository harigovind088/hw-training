import requests
from scrapy import Selector
import re
from pymongo import MongoClient

class AgentScraper:
    def __init__(self, url, db_name='agents_db', collection_name='agents_data'):
        self.url = url
        self.headers = {
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7",
            "Accept-Language": "en-GB,en-US;q=0.9,en;q=0.8",
            "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/128.0.0.0 Safari/537.36",
            "sec-ch-ua": "\"Chromium\";v=\"128\", \"Not;A=Brand\";v=\"24\", \"Google Chrome\";v=\"128\"",
            "sec-ch-ua-mobile": "?0",
            "sec-ch-ua-platform": "\"Linux\""
        }
        
        self.client = MongoClient('mongodb://localhost:27017/')
        self.db = self.client[db_name]
        self.collection = self.db[collection_name]

    def fetch_agents(self):
        response = requests.get(url=self.url, headers=self.headers)
        selector = Selector(text=response.text)

        agents = []
        for agent in selector.xpath('//article[@class="rng-agent-roster-agent-card js-sort-item"]'):
            agent_info = {
                "first_name": agent.xpath('.//h1/text()').get().strip().split()[0],
                "last_name": agent.xpath('.//h1/text()').get().strip().split()[-1],
                "middle_name": ' '.join(agent.xpath('.//h1/text()').get().strip().split()[1:-1]),
                "title": agent.xpath('.//h1/span[@class="account-title"]/text()').get(default="").strip(),
                "office_name": agent.xpath('.//p/strong/text()').get().strip(),
                "address": agent.xpath('.//strong/following-sibling::text()[1]').get(default="").strip(),
                "country": "United States",
                "city": agent.xpath('.//span[@class="js-sort-city"]/text()').get(default="").strip(),
                "state": self.extract_state(agent),
                "zipcode": self.extract_zipcode(agent),
                "image_url": agent.xpath('.//img/@src').get(),
                "website": agent.xpath('.//ul[2]/li[1]/a/@href').get(),
                "profile_url": self.get_profile_url(agent),
                "office_phone_numbers": [phone.strip() for phone in agent.xpath('.//ul[1]/li[1]/a/text()').getall()],
                "agent_phone_numbers": [
                    phone.strip() for phone in agent.xpath('.//ul[1]/li[2]/a/text()').getall()
                    if phone.strip() and phone.strip() != "Email"
                ],
                "social_links": self.extract_social_links(agent),
                "language": self.extract_language(agent),
                "email": self.extract_email(agent)
            }

            agent_info = {k: v if v else "" for k, v in agent_info.items()}
            agents.append(agent_info)

        return agents

    def get_profile_url(self, agent):
        profile_url = agent.xpath('.//a/@href').get()
        return f"https://www.huff.com{profile_url}" if profile_url and profile_url.startswith('/bio') else ""

    def extract_state(self, agent):
        state_info = agent.xpath('.//span[@class="js-sort-city"]/following::text()[1]').get(default="")
        match = re.search(r'\|\s*([A-Z]{2})\s*\d{5}\s*\|', state_info)
        return match.group(1) if match else ""

    def extract_zipcode(self, agent):
        state_info = agent.xpath('.//span[@class="js-sort-city"]/following::text()[1]').get(default="")
        match = re.search(r'\|\s*[A-Z]{2}\s*(\d{5})\s*\|', state_info)
        return match.group(1) if match else ""

    def extract_social_links(self, agent):
        social_links = agent.xpath('.//li[@class="rng-agent-profile-contact-social"]/a/@href').getall()
        structured_links = {
            "Facebook": "",
            "Twitter": "",
            "LinkedIn": "",
            "OtherLinks": []
        }
        
        for link in social_links:
            if "facebook" in link:
                structured_links["Facebook"] = link
            elif "twitter" in link:
                structured_links["Twitter"] = link
            elif "linkedin" in link:
                structured_links["LinkedIn"] = link
            else:
                structured_links["OtherLinks"].append(link)

        return structured_links

    def extract_language(self, agent):
        languages = agent.xpath(".//p[starts-with(text(), 'Speaks:')]/text()").getall()
        return languages[0].replace("Speaks:", "").strip() if languages else " "

    def extract_email(self, agent):
        email = agent.xpath('.//ul[1]/li[3]/a/@href').get()
        return email.replace("mailto:", "") if email and "@" in email else ""

    def deduplicate_agents(self, agents):
        unique_agents = {}
        for agent in agents:
            identifier = (agent.get("website"), agent.get("first_name"), agent.get("last_name"))
            if identifier not in unique_agents:
                unique_agents[identifier] = agent
        return list(unique_agents.values())

    def save_to_mongodb(self, agents):
        if agents:
            self.collection.insert_many(agents)

    def run(self):
        agents = self.fetch_agents()
        unique_agents = self.deduplicate_agents(agents)
        self.save_to_mongodb(unique_agents)
        print(f"Fetched {len(agents)} agents, removed duplicates, and saved {len(unique_agents)} to MongoDB collection '{self.collection.name}'")

if __name__ == "__main__":
    url = 'https://www.huff.com/roster/agents/0'
    scraper = AgentScraper(url)
    scraper.run()
