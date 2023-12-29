from urllib.parse import quote, urlencode

import requests
from scrapy import Spider

from OSM_Enhanced.items.poi import PoiItem


class WikidataPipeline:
    def process_item(self, item: PoiItem, spider: Spider):
        if "brand:wikidata" not in item.other_tags:
            return item

        resp = requests.get(
            "https://query.wikidata.org/sparql?query={}".format(
                quote(
                    "SELECT ?brand ?logo ?website WHERE {\n"
                    + "VALUES ?brand { wd:"
                    + item.other_tags["brand:wikidata"]
                    + " }\n"
                    + "OPTIONAL { ?brand wdt:P154 ?logo }\n"
                    + "OPTIONAL { ?brand wdt:P856 ?website }\n"
                    + "} LIMIT 1"
                )
            ),
            headers={"Accept": "application/sparql-results+json"},
        )
        if resp.status_code != 200:
            return item
        data = resp.json()["results"]["bindings"][0]

        if "brand:logo" not in item.other_tags:
            item.other_tags["brand:logo"] = data.get("logo", {}).get("value")
        if "brand:website" not in item.other_tags:
            item.other_tags["brand:website"] = data.get("website", {}).get("value")

        item.sources.append(data["brand"]["value"])

        return item
