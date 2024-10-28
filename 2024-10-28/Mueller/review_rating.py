import requests
from mongoengine import connect
from settings import MONGO_URI, DB_NAME, DATA_COLLECTION
from pipeline import ProductModel

def fetch_and_update_reviews():
    connect(host=MONGO_URI, db=DB_NAME)  

    unique_ids = ProductModel.objects.distinct('unique_id')  

    for unique_id in unique_ids:
        url = f"https://api.bazaarvoice.com/data/display/0.2alpha/product/summary?PassKey=caq5uCLiy6gWz7GqQ81mhGOWABJAsK961yPzzEfe0S9Ng&productid={unique_id}&contentType=reviews,questions&reviewDistribution=primaryRating,recommended&rev=0&contentlocale=de*,de_AT"
        
        response = requests.get(url)
        if response.status_code == 200:
            data = response.json()

            review = data['reviewSummary'].get('numReviews', 0)
            rating = data['reviewSummary'].get('primaryRating', {}).get('average', 0)

            review = review if review else 0
            rating = rating if rating else 0

            ProductModel.objects(unique_id=unique_id).update_one(
                set__review=review,
                set__rating=rating
            )
            print(f'Updated {unique_id} with {review} reviews and an average rating of {rating}.')
        else:
            print(f'Failed to retrieve data for {unique_id}: {response.status_code}')

def main():
    fetch_and_update_reviews()

if __name__ == "__main__":
    main()
