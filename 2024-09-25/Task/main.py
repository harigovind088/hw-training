from pymongo import MongoClient

class MongoDBManager:
    def __init__(self, uri, db_name):
        self.client = MongoClient(uri)
        self.db = self.client[db_name]

    def copy_collection(self, source_collection_name, target_collection_name):
        
        source_collection = self.db[source_collection_name]
        target_collection = self.db[target_collection_name]

        documents = list(source_collection.find())  
        
        new_documents = []
        for doc in documents:
            image_urls = doc.get('image_urls', [])
            new_doc = {**doc, "currency": "HUF"}  

            for index, image_url in enumerate(image_urls, start=1):
                file_extension = '.jpg' if image_url.endswith('.jpg') else '.png' if image_url.endswith('.png') else '.jpg'
                new_doc[f'file_name_{index}'] = f"{doc.get('unique_id', 'default_id')}_{index}{file_extension}"
                new_doc[f'image_url_{index}'] = image_url

            new_documents.append(new_doc)

        if new_documents:  
            target_collection.insert_many(new_documents)

           
            for doc in new_documents:
                output_lines = []
                for key in doc:
                    if key.startswith('image_url_') and doc[key]:  
                        index = key.split('_')[-1] 
                        file_name = doc.get(f'file_name_{index}')
                        output_lines.append(file_name)

                print("Data Copied Successfully..")


if __name__ == "__main__":
    uri = "mongodb://localhost:27017/"
    db_name = "web_shop_crawl"
    
    manager = MongoDBManager(uri, db_name)
    manager.copy_collection("product_data_test_two", "product_data_copied_mongodb")
