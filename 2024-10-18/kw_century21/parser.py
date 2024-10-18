from scrapy import Selector
import requests
import json
from pipeline import MongoDBPipeline
from settings import HEADERS

class Parser:
    def __init__(self):
        self.pipeline = MongoDBPipeline()
        self.profile_update_count = 0

    def parse_agent_profiles(self):
        # Fetch URLs from the crawler_url collection
        agent_profiles = self.pipeline.fetch_crawler_urls()

        for profile in agent_profiles:
            profile_url = profile['profile_url']
            try:
                self.process_agent(profile_url)
            except requests.RequestException as e:
                print(f"Failed to fetch profile from {profile_url}: {e}. Skipping...")

    def process_agent(self, profile_url):
        response = requests.get(profile_url, headers=HEADERS)
        response.raise_for_status()
        sel = Selector(text=response.text)

        # XPATH
        RESULT_XPATH = '//script[1]/text()'
        NAME_XPATH = '//h1[@class="h2"]//strong/text()'
        TITLE_XPATH = '//span[@class="font-18 d-block pb-3"]/text()'
        DESCRIPTION_XPATH = '//div[@class="py-3"]/p/text()'

        result = sel.xpath(RESULT_XPATH).extract_first()
        name = sel.xpath(NAME_XPATH).extract_first()
        title = sel.xpath(TITLE_XPATH).extract_first(default="")
        description = sel.xpath(DESCRIPTION_XPATH).extract_first(default="")

        if result:
            self.update_agent_data(result, name, title, description, profile_url)

    def update_agent_data(self, result, name, title, description, profile_url):
        try:
            data = json.loads(result)
            item = self.extract_data(data, name, title, description, profile_url)
            self.pipeline.save_final_data(item)  
            self.profile_update_count += 1
            print(f"Saved agent data for {name} in final_data collection. Count: {self.profile_update_count}")
        except json.JSONDecodeError:
            print(f"Failed to decode JSON from script content for {profile_url}. Skipping...")

    def extract_data(self, data, name, title, description, profile_url):
        full_address = data.get("address", {})
        contact = data.get("contactPoint", {})
        office = data.get("department", {})

        name_parts = name.split()
        first_name, middle_name, last_name = self.split_name(name_parts)

        available_language = contact.get("availableLanguage")
        languages = [lang.strip() for lang in available_language.split(",")] if available_language else []

        office_name = office.get("name")
        image = data.get("image", " ") if data.get("image") else ""

        address = full_address.get("streetAddress")
        city = full_address.get("addressLocality")
        state = full_address.get("addressRegion")
        zipcode = full_address.get("postalCode")

        website = data.get("url", " ") if data.get("url") else ""
        email = contact.get("email") if contact.get("email") else ""

        agent_numbers = [data.get("telephone")] if data.get("telephone") else []
        office_numbers = [office.get("telephone")] if office.get("telephone") else []

       
        item = {}
        item["profile_url"] = profile_url
        item["first_name"] = first_name
        item["middle_name"] = middle_name
        item["last_name"] = last_name
        item["office_name"] = office_name
        item["title"] = title
        item["description"] = description
        item["languages"] = languages
        item["image_url"] = image
        item["website"] = website
        item["address"] = address
        item["city"] = city
        item["state"] = state
        item["zipcode"] = zipcode
        item["country"] = "United States"
        item["social"] = {}
        item["email"] = email
        item["agent_phone_numbers"] = agent_numbers
        item["office_phone_numbers"] = office_numbers

        return item

    def split_name(self, name_parts):
        if len(name_parts) == 1:
            return name_parts[0], "", ""
        elif len(name_parts) == 2:
            return name_parts[0], "", name_parts[1]
        elif len(name_parts) >= 3:
            return name_parts[0], " ".join(name_parts[1:-1]), name_parts[-1]
        return "", "", ""

def main():
    parser = Parser()
    parser.parse_agent_profiles()

if __name__ == "__main__":
    main()
