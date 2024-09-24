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
        self.url_collection = self.db["dog_food_product_urls_two"]
        self.data_collection = self.db["product_data_test_two"]
        self.counter = 0

        logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
    
    def fetch_prices(self, selector):
        selling_price = selector.xpath("//ins/span[@class='woocommerce-Price-amount amount']/bdi/text()[1]").extract_first()
        selling_price = selling_price.replace(',', '').replace('\u00a0', '').replace(' ', '').strip() if selling_price else None

        if selling_price:
            try:
                selling_price = float(selling_price)  
            except ValueError:
                selling_price = None  

            price_text = selector.xpath("//del/span[@class='woocommerce-Price-amount amount']/bdi/text()[1]").extract_first()
            price_value = price_text.replace(',', '').replace('\u00a0', '').replace(' ', '').strip() if price_text else None
        else:
            price_text = selector.xpath('//p[contains(@class,"price")]//text()').extract()
            price_value = ' '.join(price_text).strip().replace('\xa0', '').replace(' ', '')
            price_value = price_value.split('HUF')[0].strip() if 'HUF' in price_value else price_value

           
            if 'HUF' in price_value:
                price_value = price_value.replace('HUF', '').strip()
        
        price_value = price_value.replace('Ft', '').strip()

        original_price = float(price_value) if price_value else None

        return {
            'original_price': original_price,
            'selling_price': selling_price
        }





    def parse_product(self, response):
        selector = Selector(text=response.text)

        
        product_name = selector.xpath('//h1[contains(@class,"product_title entry-title")]//text()').extract()
        product_name = ''.join(product_name).strip()

        brand_name = selector.xpath('//td[contains(@class,"woocommerce-product-attributes-item__value")]//text()').extract()
        brand_name = ''.join(brand_name).strip()

        
        unique_id = selector.xpath("//p[@class='meta_wappper sku_wrapper']/span[@class='sku']/text()").extract_first()
        unique_id = unique_id.strip() if unique_id else None


        price_data = self.fetch_prices(selector)
        
       
        
        unit_price_text = selector.xpath('//span[contains(@class,"egysegar")]//text()').extract_first()
        unit_price_text = unit_price_text.strip() if unit_price_text else None 

        
        if unit_price_text:
            unit_price_text = unit_price_text.replace('\n', '')


        
        breadcrumbs = selector.xpath("//div[@class='storefront-breadcrumb']//nav//text()[normalize-space()]").extract()
        breadcrumb_list = [crumb.strip() for crumb in breadcrumbs if crumb.strip() and crumb.strip() != '/']
        breadcrumb_path = '> '.join(breadcrumb_list)  

        
        hierarchy_levels = breadcrumb_list + [""] * (5 - len(breadcrumb_list))  

        
        description_text = selector.xpath('//div[contains(@class,"the_content")]//text()').extract()
        description_text = ' '.join(text.strip() for text in description_text if text.strip())

        
        image_urls = selector.xpath("//div[contains(@class, 'woocommerce-product-gallery')]//img/@data-large_image").extract()

        
        data = {
            "breadcrumb": breadcrumb_path,
            "product_name": product_name,
            "brand": brand_name,
            "unique_id": unique_id,  
            "regular_price": price_data['original_price'],
            "selling_price": price_data['selling_price'] or "",
            "price_per_unit": unit_price_text,
            "product_url": response.url,
            "product_description": description_text,
            "producthierarchy_level1": hierarchy_levels[0],
            "producthierarchy_level2": hierarchy_levels[1],
            "producthierarchy_level3": hierarchy_levels[2],
            "producthierarchy_level4": hierarchy_levels[3],
            "producthierarchy_level5": hierarchy_levels[4],
            "image_urls": image_urls,  
        }

        self.save_to_json(data)
        self.data_collection.update_one({"url": response.url}, {"$set": data}, upsert=True)
        self.counter += 1


    def save_to_json(self, data):
        filename = "result.json"
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
