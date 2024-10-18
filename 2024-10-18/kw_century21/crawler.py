from scrapy import Selector
import requests
from pipeline import MongoDBPipeline
from settings import HEADERS, URL

class Crawler:
    def __init__(self):
        self.pipeline = MongoDBPipeline()
        self.profile_url_count = 0

    def fetch_agent_urls(self):
        response = requests.get(URL, headers=HEADERS)
        sel = Selector(text=response.text)
        URL_XPATH = '//url/loc/text()'

        urls = sel.xpath(URL_XPATH).extract()[:2000]

        for result in urls:
            self.profile_url_count += 1
            print(f"{self.profile_url_count}: Fetched URL: {result}")
            self.pipeline.save_crawler_url(result)  

        print(f"Total fetched profile URLs: {self.profile_url_count}")
        print("Profile URLs saved to crawler_url collection in MongoDB.")

def main():
    crawler = Crawler()
    crawler.fetch_agent_urls()

if __name__ == "__main__":
    main()
