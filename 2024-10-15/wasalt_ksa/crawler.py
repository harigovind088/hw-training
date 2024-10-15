from scrapy import Selector
import requests
import json
from urllib.parse import urlparse
from datetime import datetime
from pipeline import save_property_data
from settings import headers, sale_url, rent_url

class PropertyFetcher:
    def __init__(self, url, category_name):
        self.url = url
        self.category_name = category_name
        self.property_info = []

    def fetch_properties(self):
        parsed_url = urlparse(self.url)
        category_path = parsed_url.path

        for page in range(1, 36):
            response = requests.get(f"{self.url}?page={page}", headers=headers)
            sel = Selector(text=response.text)

            result = sel.xpath('//script[2]/text()').get()
            if not result:
                break  

            data = json.loads(result)
            properties = data.get("itemListElement", [])

            for item in properties:
                property_data = {}
                property_data["id"] = ""
                property_data["reference_number"] = ""
                property_data["url"] = item["mainEntity"]["url"]
                property_data["broker_display_name"] = ""
                property_data["broker"] = ""
                property_data["category"] = self.category_name
                property_data["category_url"] = category_path
                property_data["title"] = item["mainEntity"]["name"]
                property_data["description"] = ""
                property_data["location"] = item["mainEntity"]["address"]["addressLocality"]
                property_data["price"] = str(item["mainEntity"]["offers"][0]["priceSpecification"].get("price", ""))
                property_data["currency"] = item["mainEntity"]["offers"][0]["priceSpecification"].get("priceCurrency", "")
                property_data["price_per"] = ""
                property_data["bedrooms"] = ""
                property_data["bathrooms"] = ""
                property_data["furnished"] = ""
                property_data["rera_permit_number"] = ""
                property_data["dtcm_licence"] = ""
                property_data["scraped_ts"] = datetime.now().strftime("%Y-%m-%d")
                property_data["amenities"] = ""
                property_data["details"] = ""
                property_data["agent_name"] = ""
                property_data["number_of_photos"] = ""
                property_data["user_id"] = ""
                property_data["phone_number"] = ""
                property_data["date"] = datetime.now().strftime("%Y-%m-%d")
                property_data["depth"] = ""
                property_data["sub_category_1"] = "Residential"
                property_data["property_type"] = item["mainEntity"]["@type"][1]
                property_data["sub_category_2"] = ""
                property_data["published_at"] = ""
                property_data["iteration_number"] = datetime.now().strftime("%Y_%m")
                property_data["longitude"] = item["mainEntity"]["geo"]["longitude"]
                property_data["latitude"] = item["mainEntity"]["geo"]["latitude"]
                property_data["seller_role"] = ""
                property_data["project"] = ""
                property_data["rega_ad_license_no"] = ""
                property_data["fal_license_number"] = ""

                self.property_info.append(property_data)
                save_property_data(property_data)

            print(f"Fetched {len(properties)} properties from {self.category_name} - Page {page}")

            if len(self.property_info) >= 1000:
                break

        return self.property_info

def main():
    all_properties = []
    rent_fetcher = PropertyFetcher(rent_url, "rent")
    sale_fetcher = PropertyFetcher(sale_url, "sale")

    all_properties.extend(rent_fetcher.fetch_properties())
    all_properties.extend(sale_fetcher.fetch_properties())

    print(f"Total properties fetched: {len(all_properties)}")

if __name__ == "__main__":
    main()
