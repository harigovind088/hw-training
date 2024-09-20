import requests
from parsel import Selector
import json
from pymongo import MongoClient
import logging
import re


class WebParse:
    def __init__(self):
        self.client = MongoClient("mongodb://localhost:27017/")
        self.db = self.client["web_shop_crawl"]
        self.url_collection = self.db["dog_food_product_urls"]
        self.data_collection = self.db["product_data"]
        self.counter = 0

        logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
    
    def fetch_prices(self, selector):
        # Check if discount price exists
        selling_price = selector.xpath("//ins/span[@class='woocommerce-Price-amount amount']/bdi/text()[1]").get()
        selling_price = selling_price.replace(',', '').replace('\u00a0', '').strip() if selling_price else None

        if selling_price:
            price_text = selector.xpath("//del/span[@class='woocommerce-Price-amount amount']/bdi/text()[1]").get()
            price_value = price_text.replace(',', '').replace('\u00a0', '').strip() if price_text else None
        else:
            price_text = selector.xpath('//p[contains(@class,"price")]//text()').getall()
            price_value = ' '.join(price_text).strip().replace('\xa0', '').replace(' ', '')
            price_value = price_value.split('HUF')[0].strip() if 'HUF' in price_value else price_value

            # If original price is empty, handle accordingly
            if 'HUF' in price_value:
                price_value = price_value.replace('HUF', '').strip()
        
        price_value = price_value.replace('Ft', '').strip()
        
        return {
            'original_price': price_value,
            'selling_price': selling_price
        }



    def parse_product(self, response):
        selector = Selector(text=response.text)

        # Extracting new fields
        product_name = selector.xpath('//h1[contains(@class,"product_title entry-title")]//text()').getall()
        product_name = ''.join(product_name).strip()

        brand_name = selector.xpath('//td[contains(@class,"woocommerce-product-attributes-item__value")]//text()').getall()
        brand_name = ''.join(brand_name).strip()

    
        price_data = self.fetch_prices(selector)
        

        unit_price_text = selector.xpath('//p[contains(@class,"meta_wappper egysegar_wrapper")]//text()').getall()
        unit_price_text = ''.join(unit_price_text).strip()
        unit_price_parts = unit_price_text.split("Unit price:")[-1].strip() if "Unit price:" in unit_price_text else unit_price_text
        unit_price_text = unit_price_parts.split("\n")[-1].strip()


        breadcrumbs = selector.xpath("//div[@class='storefront-breadcrumb']//nav//text()[normalize-space()]").getall()
        breadcrumb_list = [crumb.strip() for crumb in breadcrumbs if crumb.strip()]
        breadcrumb_path = ''.join(breadcrumb_list)


        description_text = selector.xpath('//div[contains(@class,"the_content")]//text()').getall()
        description_text = ' '.join(text.strip() for text in description_text if text.strip())

        data = {
            "breadcrumb": breadcrumb_path,
            "product_name": product_name,
            "brand": brand_name,
            "regular_price": price_data['original_price'],
            "selling_price": price_data['selling_price'] or "",
            "price_per_unit": unit_price_text,
            "product_url": response.url,
            "product_description": description_text,
        }

        self.save_to_json(data)
        self.data_collection.update_one({"url": response.url}, {"$set": data}, upsert=True)
        self.counter += 1

    def save_to_json(self, data):
        filename = "product_food_dog.json"
        with open(filename, "a") as file:
            json.dump(data, file,  ensure_ascii=False)
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
