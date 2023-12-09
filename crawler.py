import json
import os
import time
from datetime import datetime
import requests
from bs4 import BeautifulSoup


ROOT_URL = "https://www.humblebundle.com"
DATA_DIR = "data/humblebundle"


def bundle_fullname(bundle):
    filename = f"{datetime.now().year}-{bundle['machine_name']}.json"
    fullname = f"{DATA_DIR}/{filename}"

    return fullname


def save_bundle(name, data):
    with open(name, "w", encoding="UTF8") as output:
        output.write(json.dumps(data, indent=2, sort_keys=True))


def crawl(url, element_id):
    res = requests.get(url)
    soup = BeautifulSoup(res.text, "html.parser")
    elem = soup.find("script", {"id": element_id})

    return json.loads(elem.contents[0])


def crawl_bundle(bundle):
    name = bundle_fullname(bundle)
    if os.path.exists(name):
        return

    print(f"Crawling bundle \"{bundle['name']}\"")
    data = crawl(bundle["url"], "webpack-bundle-page-data")["bundleData"]
    save_bundle(name, data)

    time.sleep(2)


def crawl_bundles():
    print("Crawling all bundles")
    return crawl(ROOT_URL + "/bundles", "landingPage-json-data")


def process_collection(bundle_data, collection):
    items = bundle_data["data"][collection]["mosaic"][0]["products"]
    for item in items:
        bundle = {
            "name": item["tile_name"],
            "machine_name": item["machine_name"],
            "url": ROOT_URL + item["product_url"]
        }
        crawl_bundle(bundle)


def process_bundles():
    bundle_data = crawl_bundles()
    process_collection(bundle_data, "books")
    process_collection(bundle_data, "games")
    process_collection(bundle_data, "software")


if __name__ == "__main__":
    if not os.path.exists(DATA_DIR):
        os.makedirs(DATA_DIR)
    process_bundles()
