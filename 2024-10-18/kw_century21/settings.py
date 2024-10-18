from datetime import datetime

CLIENT_NAME = "kw"
PROJECT = "century21"
FREQUENCY = "monthly"
CURRENT_DATE = datetime.now().strftime("%Y_%m_%d")
MONGO_DB = f"{CLIENT_NAME}_{FREQUENCY}_{CURRENT_DATE}"
MONGO_COLLECTION_URL = f"{PROJECT}_url"
MONGO_COLLECTION_DATA = f"{PROJECT}_data"

HEADERS = {
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7",
    "Accept-Language": "en-GB,en-US;q=0.9,en;q=0.8",
    "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/128.0.0.0 Safari/537.36",
}

URL = "https://www.century21.com/c21sitemaps/sitemapc21agents1.xml"
