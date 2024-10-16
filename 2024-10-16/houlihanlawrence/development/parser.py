import requests
import re
from pipeline import MongoDBPipeline
from scrapy import Selector
from bs4 import BeautifulSoup
from settings import HEADERS

class AgentBioParser:
    def __init__(self):
        self.pipeline = MongoDBPipeline()

    def parse_bio(self, bio_url):
        bio_response = requests.get(bio_url, headers=HEADERS)
        bio_sel = Selector(text=bio_response.text)

        office_name = bio_sel.xpath('//div[@class="rng-bio-account-info"]/h3/text()').get()
        
        description_html = bio_sel.xpath('//div[@class="copy"]').get() or ''
        soup = BeautifulSoup(description_html, 'html.parser')
        description = soup.get_text(separator=' ', strip=True)

        website = bio_sel.xpath('//a[@class="site-text-link"]/@href').get() or ''
        email_script_src = bio_sel.xpath('//script[contains(@src, "https://www.testimonialtree.com/widgets/")]//@src').get() or ''
        email = ''
        if email_script_src:
            email_match = re.search(r'email=([^&]+)', email_script_src)
            if email_match:
                email = email_match.group(1)

        facebook_url = bio_sel.xpath('//li[@class="social-facebook"]/a/@href').get() or ''
        twitter_url = bio_sel.xpath('//li[@class="social-twitter"]/a/@href').get() or ''
        linkedin_url = bio_sel.xpath('//li[@class="social-linkedin"]/a/@href').get() or ''
        instagram_url = bio_sel.xpath('//li[@class="social-instagram"]/a/@href').get() or ''

        address, city, state, zipcode = '', '', '', ''
        if website:
            address_response = requests.get(website, headers=HEADERS)
            address_sel = Selector(text=address_response.text)
            address = address_sel.xpath('//ul[@class="no-bullet"]/li[2]/text()').get()
            city_state_zip = address_sel.xpath('//ul[@class="no-bullet"]/li[3]/text()').get()

            if city_state_zip:
                city_state_zip_parts = city_state_zip.split(',')
                city = city_state_zip_parts[0].strip()
                state_zip = city_state_zip_parts[1].strip().split(' ')
                state = state_zip[0]
                zipcode = state_zip[1] if len(state_zip) > 1 else ''

        data = {
            "office_name": office_name,
            "description": description,
            "website": website,
            "email": email,
            "country": "United States",
            "address": address,
            "city": city,
            "state": state,
            "zipcode": zipcode,
            "social": {
                "facebook_url": facebook_url,
                "twitter_url": twitter_url,
                "linkedin_url": linkedin_url,
                "instagram_url": instagram_url,
                "other_urls": []
            }
        }
        return data

    def update_agent_data(self):
        profile_urls = self.pipeline.fetch_profile_urls()
        url_count = 0

        for agent in profile_urls:
            bio_url = agent.get('profile_url')
            if bio_url:
                data = self.parse_bio(bio_url)
                self.pipeline.update_agent(bio_url, data)
                url_count += 1
                print(f"Updated data for profile URL: {bio_url} (Count: {url_count})")

        print(f"Total profile URLs processed: {url_count}")

def main():
    parser = AgentBioParser()
    parser.update_agent_data()

if __name__ == "__main__":
    main()
