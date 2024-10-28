import requests
from scrapy import Selector
import json
import re
from js2py import eval_js
from settings import HEADERS,SPECIAL_INFORMATION
from pipeline import MongoPipeline
from datetime import datetime

class ProductScraper:
    def __init__(self):
        self.headers = HEADERS
        self.pipeline = MongoPipeline()

    def get_urls(self):
        """Fetch URLs from the MongoDB collection using the pipeline."""
        return self.pipeline.get_urls()  

    def fetch_data(self, url):
        """Fetch the HTML content of the given URL."""
        try:
            response = requests.get(url, headers=self.headers, timeout=10)
            response.raise_for_status()
            return Selector(text=response.text)
        except requests.RequestException as e:
            print(f"Failed to fetch {url}: {e}")
            return None

    def parse_product_info(self, selector, url):
        """Parse product information from the selector."""
        if selector is None:
            print(f"Skipping URL due to fetch error: {url}")
            return

        """XPATH"""
        SCRIPT_XPATH='//component[@type="application/ld+json"]/text()'
        SCRIPT_JS_XPATH='//script[contains(text(),"window.__APP_STATE =")]/text()'
        PRODUCT_NAME_XPATH = "//h1[@class='mu-product-details-page__product-name']/text()"
        BREADCRUMBS = "//ul[@class='mu-breadcrumbs']/li/span/text()|//ul[@class='mu-breadcrumbs']/li/a/span/text()"
        PERCENTAGE_DISCOUNT = '//div[@class="mu-product-price__percentage-saving"]/strong/text()'
        PRICE_PER_UNIT = '//div[@class="mu-product-price__additional-info"]/text()[1]'
        INSTRUCTION = "//td[contains(text(), 'Nutzungshinweis')]/following-sibling::td[1]/text()"
        STORAGE_INSTRUCTION = "//td[contains(text(), 'Lagerhinweis')]/following-sibling::td[1]/text()"
        ORIGIN_COUNTRY = "//td[contains(text(), 'Herkunftsland')]/following-sibling::td[1]/text()"
        ALLERGENS = "//td[contains(text(), 'Allergenhinweis')]/following-sibling::td[1]/text()"
        AGE_RECOMMENDATIONS = "//td[contains(text(), 'Altersempfehlung ab')]/following-sibling::td[1]/text()"
        FLAVOUR = "//td[contains(text(), 'Geschmacksrichtung')]/following-sibling::td[1]/text()"
        REGION = "//td[contains(text(), 'Region')]/following-sibling::td[1]/text()"
        PACKAGING = "//td[contains(text(), 'Hundegröße')]/following-sibling::td[1]/text()"
        ORGANIC_TYPE = "//td[contains(text(), 'Bio')]/following-sibling::td[1]/text()"
        FEEDING_RECOMMENDATION = "//td[contains(text(), 'Fütterungsempfehlung')]/following-sibling::td[1]/text()"
        COLOR = "//td[contains(text(), 'Farbe')]/following-sibling::td[1]/text()"
        MODEL_NUMBER = "//td[contains(text(), 'Modellnummer')]/following-sibling::td[1]/text()"
        MATERIAL = "//td[contains(text(), 'Materialdetails')]/following-sibling::td[1]/text()"
        DOSAGE = "//td[contains(text(), 'Dosierempfehlung')]/following-sibling::td[1]/text()"
        TASTE = "//td[contains(text(), 'Geschmack')]/following-sibling::td[1]/text()"
        SIZE = "//td[contains(text(), 'Größe')]/following-sibling::td[1]/text()"
        CARE_INSTRUCTION = "//td[contains(text(), 'Pflegehinweis')]/following-sibling::td[1]/text()"
        MANUFACTURER = "//td[contains(text(), 'Hersteller')]/following-sibling::td[1]/text()"
        ALCHOL_BY_VOLUME = "//td[contains(text(), 'Lebensmittel Alkoholgehalt')]/following-sibling::td[1]/text()"
        INGREDIANTS = "//td[contains(text(), 'Inhaltsstoffe')]/following-sibling::td[1]/text()"
        WARNING = '//div[@class="mu-product-description__notice"]//text()'
        SUITABLE_FOR = "//td[contains(text(), 'Geeignet')]/following-sibling::td[1]/text()"
        GRAPE_VARIETY = "//td[contains(text(), 'Rebsorte')]/following-sibling::td[1]/text()"
        ROW_XPATH = '//div[@id="nutrition"]//tr'
        LABEL_XPATH = './/td[@class="mu-table__cell mu-table__cell--label"]/text()'
        VALUE_XPATH = './/td[2]/text()'
        SPECIAL_INFO = '//div[@id="features"]//tr'

       
        product_name = selector.xpath(PRODUCT_NAME_XPATH).extract_first()
        breadcrumbs = selector.xpath(BREADCRUMBS).extract()
        percentage_discount = selector.xpath(PERCENTAGE_DISCOUNT).extract_first()
        price_per_unit = selector.xpath(PRICE_PER_UNIT).extract_first()
        instructions =selector.xpath(INSTRUCTION).extract_first()
        storage_instructions =selector.xpath(STORAGE_INSTRUCTION).extract_first()
        country_of_origin =selector.xpath(ORIGIN_COUNTRY).extract_first()
        allergens =selector.xpath(ALLERGENS).extract_first()
        age_recommendations =selector.xpath(AGE_RECOMMENDATIONS).extract_first()
        flavour =selector.xpath(FLAVOUR).extract_first()
        region =selector.xpath(REGION).extract_first()
        packaging =selector.xpath(PACKAGING).extract_first()
        organictype = selector.xpath(ORGANIC_TYPE).extract_first()
        feeding_recommendation =selector.xpath(FEEDING_RECOMMENDATION).extract_first()
        color =selector.xpath(COLOR).extract_first()
        model_number =selector.xpath(MODEL_NUMBER).extract_first()
        material =selector.xpath(MATERIAL).extract_first()
        dosage_recommendation =selector.xpath(DOSAGE).extract_first()
        tasting_note =selector.xpath(TASTE).extract_first()
        size =selector.xpath(SIZE).extract_first()
        care_instructions =selector.xpath(CARE_INSTRUCTION).extract_first()
        manufacturer_address =selector.xpath(MANUFACTURER).extract_first()
        alchol_by_volume = selector.xpath(ALCHOL_BY_VOLUME).extract()
        ingrediants = selector.xpath(INGREDIANTS).extract()
        warning = selector.xpath(WARNING).extract()
        suitable_for = selector.xpath(SUITABLE_FOR).extract_first()
        grape_variety = selector.xpath(GRAPE_VARIETY).extract_first()
        in_stock = selector.xpath(SCRIPT_XPATH).extract_first()
        description = selector.xpath(SCRIPT_XPATH).extract_first()
        brand_name = selector.xpath(SCRIPT_XPATH).extract_first()
        

        script_js = selector.xpath(SCRIPT_JS_XPATH).extract_first()
        j_string = eval_js(script_js)
        product = j_string.to_dict()

        """Cleaning Stage"""
        product_json = json.loads(product['modules']['pdp']['product'])
        
        #price_related_info
        reg_price = product_json.get("priceInfo", {}).get("price", "")
        sell_price = product_json.get("priceInfo", {}).get("price", "")
        original_price = product_json.get("priceInfo", {}).get("savings", {}).get("originalPrice", "")
        Aktion= product_json.get("showSpecialPriceLabel", "")
        offer = product_json.get("priceInfo", {}).get("savings", {}).get("percentage", "")

        if Aktion == True and offer == "":
            regular_price = ""
            selling_price = reg_price
            price_was = ""
            promotion_price = sell_price
            promotion_description= "AKTION"

        elif offer == "":
            regular_price = reg_price
            selling_price = reg_price
            price_was = ""
            promotion_price = ""
            promotion_description= ""
        else:
            regular_price = original_price
            selling_price = original_price
            price_was = original_price
            promotion_price = sell_price
            promotion_description= f"Sie sparen {offer}%"
        

        item_features = product['modules']['pdp']['itemFeatures']
        inhalt_value = next((item['value'] for item in item_features if item['name'] == 'Inhalt'), None)
        grammage_quantity, grammage_unit = inhalt_value.split()

        variant = re.sub(r'\s+', ' ', inhalt_value.strip())

        #unique_id
        unique_id = product_json['articleNumber']
        #product_name
        product_name = re.sub(r'\s+', ' ', product_name.strip())

        #images & file_names  
        article_number = product_json['articleNumber']
        image_data = []
        for index, image in enumerate(product_json['assets']):
            image_url = image['image']['zoom'] if 'image' in image and 'zoom' in image['image'] else ""
            
            file_name = f"{article_number}_{index + 1}.png" if image_url else ""
            
            image_data.append({"image_url": image_url, "file_name": file_name})
        image_urls = [img['image_url'] for img in image_data[:6]]
        file_names = [img['file_name'] for img in image_data[:6]]

        image_url_1=image_urls[0] if len(image_urls) > 0 else ""
        file_name_1=file_names[0] if len(file_names) > 0 else ""
        image_url_2=image_urls[1] if len(image_urls) > 1 else ""
        file_name_2=file_names[1] if len(file_names) > 1 else ""
        image_url_3=image_urls[2] if len(image_urls) > 2 else ""
        file_name_3=file_names[2] if len(file_names) > 2 else ""
        image_url_4=image_urls[3] if len(image_urls) > 3 else ""
        file_name_4=file_names[3] if len(file_names) > 3 else ""
        image_url_5=image_urls[4] if len(image_urls) > 4 else ""
        file_name_5=file_names[4] if len(file_names) > 4 else ""
        image_url_6=image_urls[5] if len(image_urls) > 5 else ""
        file_name_6=file_names[5] if len(file_names) > 5 else ""

        #description
        if description:
            description = json.loads(description)
            description = description.get('description', '')
        else:
            description = ''
        #brand
        if brand_name:
            brand_name = json.loads(brand_name)
            brand = brand_name.get('brand', {}).get('name', '')
        else:
            brand = ''

        #breadcrumbs& producthierarchy
        breadcrumb_list = [crumb.strip() for crumb in breadcrumbs if crumb.strip()]

        hierarchy_levels = breadcrumb_list + [""] * (7 - len(breadcrumb_list))
        breadcrumb_path = '> '.join(breadcrumb_list)
        product_hierarchy = [hierarchy_levels[i] if hierarchy_levels[i] else "" for i in range(7)]
        producthierarchy_level1, producthierarchy_level2, producthierarchy_level3, producthierarchy_level4, producthierarchy_level5, producthierarchy_level6, producthierarchy_level7 = product_hierarchy

        percentage_discount = percentage_discount if percentage_discount else ""
        price_per_unit = (price_per_unit.replace("inkl. gesetzl. MwSt.", "").strip() if price_per_unit else "")
        instructions = re.sub(r'\s+', ' ', instructions.strip()) if instructions else ""
        storage_instructions = re.sub(r'\s+', ' ', storage_instructions.strip()) if storage_instructions else ""
        country_of_origin = re.sub(r'\s+', ' ', country_of_origin.strip()) if country_of_origin else ""
        allergens = re.sub(r'\s+', ' ', allergens.strip()) if allergens else ""
        age_recommendations = re.sub(r'\s+', ' ', age_recommendations.strip()) if age_recommendations else ""
        flavour = re.sub(r'\s+', ' ', flavour.strip()) if flavour else ""
        region = re.sub(r'\s+', ' ', region.strip()) if region else ""
        packaging = re.sub(r'\s+', ' ', packaging.strip()) if packaging else ""
        organictype = "Organic" if organictype else "Non-Organic"
        feeding_recommendation = re.sub(r'\s+', ' ', feeding_recommendation.strip()) if feeding_recommendation else ""
        color = re.sub(r'\s+', ' ', color.strip()) if color else ""
        model_number = re.sub(r'\s+', ' ', model_number.strip()) if model_number else ""
        material = re.sub(r'\s+', ' ', material.strip()) if material else ""
        dosage_recommendation = re.sub(r'\s+', ' ', dosage_recommendation.strip()) if dosage_recommendation else ""
        tasting_note = re.sub(r'\s+', ' ', tasting_note.strip()) if tasting_note else ""
        size = re.sub(r'\s+', ' ', size.strip()) if size else ""
        care_instructions = re.sub(r'\s+', ' ', care_instructions.strip()) if care_instructions else ""
        manufacturer_address = re.sub(r'\s+', ' ', manufacturer_address.strip()) if manufacturer_address else ""
        alchol_by_volume = alchol_by_volume if alchol_by_volume else ""

        site_shown_uom = re.sub(r'\s+', ' ', inhalt_value.strip())

        warning= warning if warning else ""
        warning = ' '.join([text.strip() for text in warning if text.strip()])

        suitable_for= suitable_for if suitable_for else ""
        suitable_for = re.sub(r'\s+', ' ', suitable_for.strip())

        ingrediants = [ingredient.strip() for ingredient in ingrediants if ingredient.strip()]
        ingrediants = ", ".join(ingrediants) if ingrediants else ""

        grape_variety= grape_variety if grape_variety else ""
        grape_variety = re.sub(r'\s+', ' ', grape_variety.strip())

        #in-stock
        availability = (
            json.loads(in_stock)['offers'][0].get('availability')
            if in_stock and 'offers' in json.loads(in_stock) and json.loads(in_stock)['offers'] 
            else None
        )
        instock = True if availability and "InStock" in availability else False

        product_key = re.sub(r'\s+', ' ', unique_id.strip())
        product_unique_key = product_key.replace("Art.Nr.", "").strip()
        product_unique_key += 'P'

        product = json.loads(j_string['modules']['pdp']['product'])
        available_quantities = product['availableQuantitiesInStore']
        available_count = len(available_quantities)

        extraction_date = datetime.now().strftime("%Y-%m-%d")


        
        #Nutrition_information
        nutrition_info = {}
        rows = selector.xpath(ROW_XPATH)

        for row in rows:
            label = row.xpath(LABEL_XPATH).get(default='').strip()
            value = row.xpath(VALUE_XPATH).get(default='').strip()
            
            key = f'{label}'
            nutrition_info[key] = value

        #Special_information
        special_info = {}
        rows = selector.xpath(SPECIAL_INFO)

        for row in rows:
            label = row.xpath('.//td[@class="mu-table__cell mu-table__cell--label"]/text()').get(default='').strip()
            value = row.xpath('.//td[2]/text()').get(default='').strip()
            
            key = None
            for k, mapped_label in SPECIAL_INFORMATION.items():
                if label == mapped_label:
                    key = k
                    break  
            
            if key is not None:  
                special_info[key] = value
            else:  
                special_info[label] = value


        item = {}  
        item["unique_id"] = unique_id  
        item["competitor_name"] = "mueller"
        item["store_name"] = ""
        item["store_addressline1"] = ""
        item["store_addressline2"] = ""
        item["store_suburb"] = ""
        item["store_state"] = ""
        item["store_postcode"] = ""
        item["store_addressid"] = ""
        item["extraction_date"] = extraction_date
        item["product_name"] = product_name  
        item["brand"] = brand
        item["brand_type"] = ""
        item["grammage_quantity"] = grammage_quantity
        item["grammage_unit"] = grammage_unit
        item["producthierarchy_level1"] = producthierarchy_level1
        item["producthierarchy_level2"] = producthierarchy_level2
        item["producthierarchy_level3"] = producthierarchy_level3
        item["producthierarchy_level4"] = producthierarchy_level4
        item["producthierarchy_level5"] = producthierarchy_level5
        item["producthierarchy_level6"] = producthierarchy_level6
        item["producthierarchy_level7"] = producthierarchy_level7
        item["regular_price"] = regular_price
        item["selling_price"] = selling_price
        item["price_was"] = price_was
        item["promotion_price"] = promotion_price
        item["promotion_valid_from"] = ""
        item["promotion_valid_upto"] = ""
        item["promotion_type"] = ""
        item["percentage_discount"] = percentage_discount
        item["promotion_description"] = promotion_description
        item["package_sizeof_sellingprice"] = ""
        item["per_unit_sizedescription"] = ""
        item["price_valid_from"] = ""
        item["price_per_unit"] = price_per_unit
        item["multi_buy_item_count"] = ""
        item["multi_buy_items_price_total"] = ""
        item["currency"] = "EUR"
        item["breadcrumb"] = breadcrumb_path
        item["pdp_url"] = url
        item["variants"] = variant
        item["product_description"] = description
        item["instructions"] = instructions
        item["storage_instructions"] = storage_instructions
        item["preparationinstructions"] = ""
        item["instructionforuse"] = instructions
        item["country_of_origin"] = country_of_origin
        item["allergens"] = allergens
        item["age_of_the_product"] = ""
        item["age_recommendations"] = age_recommendations
        item["flavour"] = flavour
        item["nutritions"] = ""
        item["nutritional_information"] = nutrition_info
        item["vitamins"] = ""
        item["labelling"] = ""
        item["grade"] = ""
        item["region"] = region
        item["packaging"] = packaging
        item["receipies"] = "" 
        item["processed_food"] = ""
        item["barcode"] = ""
        item["frozen"] = ""
        item["chilled"] = ""
        item["organictype"] = organictype
        item["cooking_part"] = ""
        item["handmade"] = ""
        item["max_heating_temperature"] = ""
        item["special_information"] = special_info
        item["label_information"] = ""
        item["dimensions"] = ""
        item["special_nutrition_purpose"] = ""
        item["feeding_recommendation"] = feeding_recommendation
        item["warranty"] = ""
        item["color"] = color
        item["model_number"] = model_number
        item["material"] = material
        item["usp"]=""
        item["dosage_recommendation"] = dosage_recommendation
        item["tasting_note"] = tasting_note
        item["food_preservation"] = ""
        item["size"] = size
        item["rating"] = ""
        item["review"] = ""
        item["file_name_1"] = file_name_1  
        item["image_url_1"] = image_url_1  
        item["file_name_2"] = file_name_2  
        item["image_url_2"] = image_url_2  
        item["file_name_3"] = file_name_3  
        item["image_url_3"] = image_url_3  
        item["file_name_4"] = file_name_4  
        item["image_url_4"] = image_url_4 
        item["file_name_5"] = file_name_5  
        item["image_url_5"] = image_url_5  
        item["file_name_6"] = file_name_6  
        item["image_url_6"] = image_url_6
        item["competitor_product_key"] = ""
        item["fit_guide"] = ""
        item["occasion"] = ""
        item["material_composition"] = ""
        item["style"] = ""
        item["care_instructions"] = care_instructions
        item["heel_type"] = ""
        item["heel_height"] = ""
        item["upc"] = ""
        item["features"] = ""
        item["dietary_lifestyle"] = ""
        item["manufacturer_address"] = manufacturer_address
        item["importer_address"] = ""
        item["distributor_address"] = ""
        item["vinification_details"] = ""
        item["recycling_information"] = ""
        item["return_address"] = ""
        item["alchol_by_volume"] = alchol_by_volume
        item["beer_deg"] = ""
        item["netcontent"] = ""
        item["netweight"] = ""
        item["site_shown_uom"] = site_shown_uom
        item["ingredients"] = ingrediants
        item["random_weight_flag"] = ""
        item["instock"] = instock
        item["promo_limit"] = ""
        item["product_unique_key"] = product_unique_key
        item["multibuy_items_pricesingle"] = ""
        item["perfect_match"] = ""
        item["servings_per_pack"] = ""
        item["warning"] =   warning
        item["suitable_for"] = suitable_for
        item["standard_drinks"] = ""
        item["environmental"] = ""
        item["grape_variety"] = grape_variety
        item["retail_limit"] = available_count 
        self.pipeline.save_product(item)

def main():
    scraper = ProductScraper()
    urls = scraper.get_urls()

    for url in urls:
        selector = scraper.fetch_data(url)
        scraper.parse_product_info(selector, url)

if __name__ == "__main__":
    main()