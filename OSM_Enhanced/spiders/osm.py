from pathlib import Path
from typing import Any

from scrapy import Request, Spider
from scrapy.http import Response
from twisted.python.failure import Failure

from OSM_Enhanced.items.poi import PoiItem


class OsmSpider(Spider):
    name = "osm"

    def __init__(self, file_path: str = None, *args, **kwargs):
        super(OsmSpider, self).__init__(*args, **kwargs)
        self.start_urls = [Path(file_path).absolute().as_uri()]

    def parse(self, response: Response, **kwargs: Any) -> Any:
        for poi in response.json()["elements"]:
            item = PoiItem(
                poi["type"],
                poi["id"],
                poi.get("timestamp"),
                poi.get("version"),
                poi.get("geometry"),
                poi["tags"],
            )

            if item.website and not "brand:wikidata" in item.other_tags:
                yield Request(
                    item.website,
                    self.parse_website,
                    meta={"item": item},
                    errback=self.website_fail,
                )
            else:
                yield item

    def parse_website(self, response: Response, **kwargs: Any) -> Any:
        item = response.meta["item"]

        item.website = response.url

        if not item.phone:
            if phone := response.xpath(
                '//a[contains(@href, "tel:")][@href]/@href'
            ).get():
                item.phone = phone.removeprefix("tel:")

        if not item.email:
            if email := response.xpath(
                '//a[contains(@href, "mailto:")][@href]/@href'
            ).get():
                item.email = email.removeprefix("mailto:")

        if not item.instagram:
            item.instagram = response.xpath(
                '//a[contains(@href, "instagram.com/")][@href]/@href'
            ).get()

        if not item.facebook:
            item.facebook = response.xpath(
                '//a[contains(@href, "facebook.com/")][@href]/@href'
            ).get()

        item.sources.append(response.url)

        yield item

    def website_fail(self, failure: Failure):
        item = failure.request.meta["item"]
        item.website = None
        yield item
