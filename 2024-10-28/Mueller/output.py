import pandas as pd
from pymongo import MongoClient
from settings import MONGO_URI, DB_NAME, DATA_COLLECTION
from pipeline import MongoPipeline

def main():
    client = MongoClient(MONGO_URI)
    db = client[DB_NAME]
    collection = db[DATA_COLLECTION]

    data = list(collection.find({}, {"_id": 0}))  

    df = pd.DataFrame(data)

    if 'nutritional_information' in df.columns:
        df['nutritional_information'] = df['nutritional_information'].apply(
            lambda x: "" if isinstance(x, dict) and not x else x
        )

    if 'special_information' in df.columns:
        df['special_information'] = df['special_information'].apply(
            lambda x: "" if isinstance(x, dict) and not x else x
        )

    df.to_csv(f"DataHut_AT_Mueller_PriceExtractions_20241031.CSV", sep='|', index=False)

if __name__ == "__main__":
    main()
