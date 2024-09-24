#Category: Dog food
import requests
from parsel import Selector
from pymongo import MongoClient
import logging

class WebCrawl:
    def __init__(self):
        self.start_url = "https://webshop.fressnapf.hu/termekkategoria/kutya/kutyaeledelek/"
        self.client = MongoClient("mongodb://localhost:27017/")
        self.db = self.client["web_shop_crawl"]
        self.collection = self.db["dog_food_product_urls_two"]
        
        logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

    def fetch(self):
        url = self.start_url
        while url:
            logging.info(f"Fetching {url}")
            response = requests.get(url)
            selector = Selector(text=response.text)

        
            product_urls = selector.xpath('//a[contains(@class,"woocommerce-LoopProduct-link woocommerce-loop-product__link")]/@href').extract()
            
            for url in product_urls:
                self.collection.update_one({"url": url}, {"$set": {"url": url}}, upsert=True)

            next_page_url = selector.xpath("//a[contains(@class, 'page-numbers') and contains(@class, 'next')]/@href").extract_first()            
            if next_page_url:
                url = next_page_url 
            else:
                url = None

if __name__ == "__main__":
    crawler = WebCrawl()
    crawler.fetch()