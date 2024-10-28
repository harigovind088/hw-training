# pipeline.py
from mongoengine import Document, DynamicDocument, StringField, connect
from settings import MONGO_URI, DB_NAME, URL_COLLECTION, DATA_COLLECTION

# Connect to MongoDB with updated DB name
connect(host=MONGO_URI, db=DB_NAME)  

# Define the URL model
class URLModel(Document):
    pdp_url = StringField(required=True)

    meta = {'collection': URL_COLLECTION}  

# Define the Product model
class ProductModel(DynamicDocument):
    unique_id = StringField(required=True)
    product_name = StringField(required=True)

    meta = {'collection': DATA_COLLECTION}  

class MongoPipeline:
    def save_urls(self, urls):
        """Save a list of URLs to the MongoDB collection."""
        url_docs = [URLModel(pdp_url=url) for url in urls]
        URLModel.objects.insert(url_docs)  
        print(f"Saved {len(urls)} URLs to MongoDB using MongoEngine.")

    def save_product(self, product_data):
        """Save a product's data to the MongoDB collection."""
        product = ProductModel(**product_data)
        product.save()
        print("Product data saved to MongoDB.")

    def get_urls(self):
        """Fetch URLs from the MongoDB collection."""
        urls = []
        try:
            cursor = URLModel.objects.all()  
            for document in cursor:
                urls.append(document.pdp_url)  
        except Exception as e:
            print(f"Error fetching URLs: {e}")
        return urls
