from scrapy import Selector
import requests
import json
import re
from datetime import datetime
from pipeline import update_property_data, fetch_urls
from settings import headers

class PropertyUpdater:
    def __init__(self):
        self.property_documents = fetch_urls()
        self.url_count = 0

    def fetch_and_update_properties(self):
        for doc in self.property_documents:
            url = doc["url"]
            self.update_property(url)

        print(f"All data updated in MongoDB. Total URLs processed: {self.url_count}")

    def update_property(self, url):
        response = requests.get(url, headers=headers)
        sel = Selector(text=response.text)

        name = sel.xpath('//div[@class="style_brokerTextWrap___mVpP"]/p/text()').get()
        featured = sel.xpath('//div[@class="style_pdpTag__PeI2c style_feature__2uEg_"]/text()').get()

        result = sel.xpath('//script[@id="__NEXT_DATA__"]/text()').get()
        if result:
            data = json.loads(result)

            
            props = data.get('props', {}).get('pageProps', {}).get('propertyDetailsV3', {})
            property_owner = props.get('propertyOwner', {})
            property_info = props.get('propertyInfo', {})

            phone = property_owner.get('phone', '')
            rega_adv_lic_no = property_owner.get('regaAdvLicNo', '')
            fal_license_number = property_owner.get('falLicenseNumber', '')
            description = property_info.get('description', '') or ''
            dar_reference = props.get('darReference', '')
            en_user_role = property_owner.get('enUserRole', '')

           
            published_at = props.get('publishedAt', '')
            if published_at:
                published_at = datetime.fromisoformat(published_at[:-1]).date().isoformat()  
            
            property_id = str(props.get('id', ''))
            gallery_images_count = str(len(data.get('props', {}).get('pageProps', {}).get('galleryDetails', {}).get('images', {}).get('data', [])))
            user_id = property_owner.get('regaAdvertiserNumber', '') or ''
            furnishing_type = property_info.get('furnishingType', '') or ''
            expected_rent_type = property_info.get('expectedRentType', '').replace('/', '')

            attributes = props.get('attributes', [])
            bedrooms = str(next((attr['value'] for attr in attributes if attr['key'] == 'noOfBedrooms'), '')) or ''
            bathrooms = str(next((attr['value'] for attr in attributes if attr['key'] == 'noOfBathrooms'), '')) or ''

            details = next((f"{attr['value']} sqm" for attr in attributes if attr['key'] == 'builtUpArea'), 
                           next((f"{attr['value']} sqm" for attr in attributes if attr['key'] == 'carpetArea'), " "))

            description = re.sub(r'<[^>]*>|&nbsp;|\n+', ' ', description).strip()

            user_id = user_id if user_id else ""
            featured = featured if featured else ""

            property_data = {}
            property_data["id"] = property_id
            property_data["reference_number"] = dar_reference
            property_data["broker_display_name"] = name
            property_data["broker"] = name
            property_data["description"] = description
            property_data["price_per"] = expected_rent_type
            property_data["bedrooms"] = bedrooms
            property_data["bathrooms"] = bathrooms
            property_data["furnished"] = furnishing_type
            property_data["details"] = details
            property_data["number_of_photos"] = gallery_images_count
            property_data["user_id"] = user_id
            property_data["phone_number"] = phone
            property_data["depth"] = featured
            property_data["published_at"] = published_at  
            property_data["seller_role"] = en_user_role
            property_data["rega_ad_license_no"] = rega_adv_lic_no
            property_data["fal_license_number"] = fal_license_number

            update_property_data(url, property_data)
            self.url_count += 1
            print(f"Data updated for URL: {url} (Total URLs processed: {self.url_count})")

def main():
    updater = PropertyUpdater()
    updater.fetch_and_update_properties()

if __name__ == "__main__":
    main()
