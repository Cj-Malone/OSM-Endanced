import pprint

import requests
from scrapy import Spider

from OSM_Enhanced.items.poi import PoiItem


class FhrsPipeline:
    def process_item(self, item: PoiItem, spider: Spider):
        if "fhrs:id" not in item.other_tags:
            return item

        resp = requests.get(
            "http://api.ratings.food.gov.uk/Establishments/{}".format(
                item.other_tags["fhrs:id"]
            ),
            headers={
                "x-api-version": "2",
                "Accept-Language": "en-GB",
                "Accept": "application/json",
            },
        )

        data = resp.json()

        if data.get("Message"):
            del item.other_tags["fhrs:id"]
            return item

        item.other_tags["fhrs:rating"] = data["RatingValue"]
        item.set_check_date(data["RatingDate"])

        if not item.postcode:
            item.postcode = data["PostCode"]

        item.sources.append(resp.url)

        return item
