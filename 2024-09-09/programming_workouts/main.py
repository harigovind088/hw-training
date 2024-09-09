import requests
from parsel import Selector
import json

class WebCrawl:
    def __init__(self):
        self.base_url = "https://www.mytheresa.com"
        self.start_url = "https://www.mytheresa.com/euro/en/men/shoes"  
        self.counter = 0
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:130.0) Gecko/20100101 Firefox/130.0',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/png,image/svg+xml,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
        }

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

        if self.counter < 1000:
            self.save_to_json(data)
            self.counter += 1

    def save_to_json(self, data):
        filename = "main_updated.json"
        with open(filename, "a") as file:
            json.dump(data, file, ensure_ascii=False)
            file.write("\n")

    def fetch(self):
        url = self.start_url
        while url and self.counter < 1000:
            print(f"Fetching {url}")
            response = requests.get(url, headers=self.headers)
            selector = Selector(text=response.text)

            product_urls_type1 = selector.xpath('//div[@class="list__container"]//div[contains(@class, "item") and contains(@class, "item--sale")]//a[contains(@class, "item__link")]/@href').getall()
            product_urls_type2 = selector.xpath('//div[@class="list__container"]//div[contains(@class, "item") and not(contains(@class, "item--sale"))]//a[contains(@class, "item__link")]/@href').getall()

            product_urls = product_urls_type1 + product_urls_type2

            for index, path in enumerate(product_urls):
                product_url = self.base_url + path
                print(f"Fetching product {product_url}")
                product_response = requests.get(product_url, headers=self.headers)
        
                self.parse_product(product_response)

                if self.counter >= 1000:
                    print("Reached the response limit of 1000. Stopping the scraper.")
                    return

            # next_page_url = selector.xpath('//div[contains(@class, "loadmore__button")]//a/@href').get()            
            next_page_url = selector.xpath("//a[contains(@class, 'button') and contains(@class, 'button--active')]/@href").get()  
                      
            
            if next_page_url:
                url = self.base_url + next_page_url
            else:
                url = None

if __name__ == "__main__":
    run = WebCrawl()
    run.fetch()
