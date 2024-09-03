import requests
from parsel import Selector
import json
from pymongo import MongoClient
import logging

class WebParse:
    def __init__(self):
        self.client = MongoClient("mongodb://localhost:27017/")
        self.db = self.client["web_crawl"]
        self.url_collection = self.db["product_urls"]
        self.data_collection = self.db["product_data"]
        self.counter = 0

        logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

    def clean_data(self, value):
        if value:
            value = value.strip()
            value = value.replace("Item number: ", "")
            value = value.replace('<span class="pricing__prices__price"> <!-- -->', '')  
            value = value.replace('</span>', '')
            value = value.replace('â¬', '€') 
        return value

    def parse_product(self, response):
        selector = Selector(text=response.text)

        other_images = selector.xpath('//div[@class="photocarousel__items"]//img/@src').getall()
        unique_image_urls = list(set(img_url.strip() for img_url in other_images))

        offer_price = self.clean_data(selector.xpath('//span[contains(@class, "pricing__prices__value--discount")]/span[contains(@class, "pricing__prices__price")]').get())
        discount = self.clean_data(selector.xpath('//span[@class="pricing__info__percentage"]/text()').get())
        offer_price = offer_price if offer_price else ""
        discount = discount if discount else ""

        data = {
            "breadcrumb": [breadcrumb.strip() for breadcrumb in selector.xpath('//div[@class="breadcrumb"]//a/text()').getall()],
            "image_url": selector.xpath('//img[@class="product__gallery__carousel__image"]/@src').get(),
            "brand": self.clean_data(selector.xpath('//div[contains(@class, "product__area__branding__designer")]/a[contains(@class, "product__area__branding__designer__link")]/text()').get()),
            "product_name": self.clean_data(selector.xpath('//div[@class="product__area__branding__name"]/text()').get()),
            "listing_price": self.clean_data(selector.xpath('//span[contains(@class, "pricing__prices__value--original")]/span[contains(@class, "pricing__prices__price")]').get()),
            "offer_price": offer_price,
            "discount": discount,
            "product_id": self.clean_data(selector.xpath('//div[@class="accordion__body__content"]//li[last()]/text()').get()),
            "sizes": [size.strip() for size in selector.xpath('//span[contains(@class, "sizeitem__label")]/text()').getall()],
            "description": self.clean_data(' '.join(selector.xpath('//div[@class="accordion__body__content"]//li/text()').getall())),
            "other_images": unique_image_urls
        }

        
        self.save_to_json(data)
        self.data_collection.update_one({"url": response.url}, {"$set": data}, upsert=True)
        self.counter += 1
            
    def save_to_json(self, data):
        filename = "result.json"
        with open(filename, "a") as file:
            json.dump(data, file, ensure_ascii=False)
            file.write("\n")        

    def parse_products(self):
        urls = self.url_collection.find()
        
        for record in urls:
            url = record["url"]
            if not url:
                continue
            logging.info(f"Fetching product {url}")
            response = requests.get(url)
            self.parse_product(response)

            
        logging.info("Completed parsing process....")    

if __name__ == "__main__":
    parser = WebParse()
    parser.parse_products()
