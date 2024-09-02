import requests
from parsel import Selector
from pymongo import MongoClient

class WebCrawl:
    def __init__(self):
        self.base_url = "https://www.mytheresa.com"
        self.start_url = f"{self.base_url}/int_en/men/shoes.html"
        self.client = MongoClient("mongodb://localhost:27017/")
        self.db = self.client["web_crawl"]
        self.collection = self.db["product_urls"]

    def fetch(self):
        url = self.start_url
        while url:
            print(f"Fetching {url}")
            response = requests.get(url)
            selector = Selector(text=response.text)

            product_urls_type1 = selector.xpath('//div[@class="list__container"]//div[contains(@class, "item") and contains(@class, "item--sale")]//a[contains(@class, "item__link")]/@href').getall()
            product_urls_type2 = selector.xpath('//div[@class="list__container"]//div[contains(@class, "item") and not(contains(@class, "item--sale"))]//a[contains(@class, "item__link")]/@href').getall()

            product_urls = [self.base_url + path for path in product_urls_type1 + product_urls_type2]

            for url in product_urls:
                self.collection.update_one({"url": url}, {"$set": {"url": url}}, upsert=True)

            next_page_url = selector.xpath("//a[contains(@class, 'pagination__item') and contains(@class, 'pagination__item__text') and @data-label='nextPage']/@href").get()            
            if next_page_url:
                url = self.base_url + next_page_url
            else:
                url = None

if __name__ == "__main__":
    crawler = WebCrawl()
    crawler.fetch()
