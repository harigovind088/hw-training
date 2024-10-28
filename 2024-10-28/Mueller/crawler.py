from scrapy import Selector
import requests
from settings import URL, HEADERS
from pipeline import MongoPipeline

def main():
    response = requests.get(URL, headers=HEADERS)
    sel = Selector(text=response.text)

    """XPATH"""
    URL_XPATH = '//url/loc/text()'

    urls = sel.xpath(URL_XPATH).extract()[:2000]

    # Save URLs to MongoDB using the pipeline
    pipeline = MongoPipeline()
    pipeline.save_urls(urls)

    print(f"Extracted {len(urls)} URLs and saved to MongoDB.")

if __name__ == "__main__":
    main()