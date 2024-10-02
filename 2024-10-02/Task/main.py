from scrapy import Selector
import requests
from pymongo import MongoClient

class AgentData:
    def __init__(self, base_url, mongo_uri, db_name, collection_name):
        self.base_url = base_url
        self.headers = {
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7",
            "Accept-Language": "en-GB,en-US;q=0.9,en;q=0.8",
            "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/128.0.0.0 Safari/537.36",
            "sec-ch-ua": "\"Chromium\";v=\"128\", \"Not;A=Brand\";v=\"24\", \"Google Chrome\";v=\"128\"",
            "sec-ch-ua-mobile": "?0",
            "sec-ch-ua-platform": "\"Linux\""
        }
        self.results = []
        self.seen_profiles = set()  

        self.client = MongoClient(mongo_uri)
        self.db = self.client[db_name]
        self.collection = self.db[collection_name]

    def fetch_agents(self, pages):
        for page_number in range(1, pages + 1):
            url = f'{self.base_url}{page_number}'
            response = requests.get(url=url, headers=self.headers)
            selector = Selector(text=response.text)
            self.extract_agent_info(selector)

    def extract_agent_info(self, selector):
        agent_list = selector.xpath('//div[contains(@class,"listing-box")]')
        for agent in agent_list:
            profile_url = agent.xpath('.//div[contains(@class,"listing-box-image")]/a/@href').get()

            if profile_url:
                if profile_url in self.seen_profiles:
                    continue
                self.seen_profiles.add(profile_url)

                full_name = agent.xpath('.//div[contains(@class,"listing-box-title")]/h2/a/text()').get()
                name_parts = full_name.split()

                first_name = name_parts[0] if len(name_parts) > 0 else ""
                middle_name = " ".join(name_parts[1:-1]) if len(name_parts) > 2 else ""
                last_name = name_parts[-1] if len(name_parts) > 1 else ""
                
                title = agent.xpath('.//div[contains(@class,"listing-box-title")]/h3/text()').get()
                title = title.replace('\u00ae', '').strip() if title else ""

                office_numbers = [phone.strip() for phone in agent.xpath(".//div[contains(@class,'listing-box-content')]/p/a[3]/text()").extract() if phone.strip()]
                agent_numbers = [phone.strip() for phone in agent.xpath(".//div[contains(@class,'listing-box-content')]/p/a[5]/text()").extract() if phone.strip()]
                website = agent.xpath(".//p/a[contains(@href, 'ewm.com')]/@href").extract_first()
                website = website.strip() if website else ""

                email = agent.xpath(".//div[contains(@class,'listing-box-content')]//a[contains(@href, 'emailme')]/@href").extract_first()
                email = email.split(':')[-1].strip() if email and '@' in email else ''

                languages = agent.xpath('.//div[contains(@class,"listing-box-content")]/p//a[contains(@href, "#")]/i[contains(@class, "fa-comments-o")]/following-sibling::text()').getall() or []
                languages = [lang.strip().replace("Speaks: ", "") for lang in languages if lang.strip()]
                languages = ', '.join(languages)

                social_links = {
                    "facebook": "",
                    "twitter": "",
                    "linkedin": "",
                    "other": []
                }

                social_media_elements = agent.xpath('.//ul[@class="listing-box-social"]/li/a')
                for link in social_media_elements:
                    href = link.xpath('@href').get()
                    if href:
                        link_text = link.xpath('text()').get()
                        if "facebook" in href:
                            social_links["facebook"] = href
                        elif "twitter" in href:
                            social_links["twitter"] = href
                        elif "linkedin" in href:
                            social_links["linkedin"] = href
                        else:
                            social_links["other"].append(href)

                if website:
                    agent_info = {
                        "first_name": first_name,
                        "middle_name": middle_name,
                        "last_name": last_name,
                        "Title": title,
                        "Image_url": agent.xpath('.//div[contains(@class,"listing-box-image")]/img/@src').get() or "",
                        "Office_phone_numbers": office_numbers,
                        "Agent_phone_numbers": agent_numbers,
                        "Profile_url": profile_url,
                        "Email": email,
                        "Website": website,
                        "Office_Name": agent.xpath('.//div[contains(@class,"listing-box-title")]/h6/text()').get() or "",
                        "Languages": languages,
                        "Social_link": social_links,
                        "Country": "United States"  
                    }
                    self.collection.insert_one(agent_info)  

if __name__ == "__main__":
    base_url = 'https://www.ewm.com/agents.php?page='
    mongo_uri = 'mongodb://localhost:27017/' 
    db_name = 'agents_db'  
    collection_name = 'second'  
    agent_data = AgentData(base_url, mongo_uri, db_name, collection_name)
    agent_data.fetch_agents(pages=13)
