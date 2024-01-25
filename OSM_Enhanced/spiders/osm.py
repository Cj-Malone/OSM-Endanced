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

            if (website := item.get_website()) and "brand:wikidata" not in item.tags:
                yield Request(
                    website,
                    self.parse_website,
                    meta={"item": item},
                    errback=self.website_fail,
                )
            else:
                yield item

    def parse_website(self, response: Response, **kwargs: Any) -> Any:
        item = response.meta["item"]

        item.set_website(response.url)

        if not item.get_phone():
            if phone := response.xpath(
                '//a[contains(@href, "tel:")][@href]/@href'
            ).get():
                item.set_phone(phone.removeprefix("tel:"))

        if not item.get_email():
            if email := response.xpath(
                '//a[contains(@href, "mailto:")][@href]/@href'
            ).get():
                item.set_email(email.removeprefix("mailto:"))

        if not item.get_instagram():
            if ig := response.xpath(
                '//a[contains(@href, "instagram.com/")][@href]/@href'
            ).get():
                item.set_instagram(ig)

        if item.get_facebook():
            if fb := response.xpath(
                '//a[contains(@href, "facebook.com/")][@href]/@href'
            ).get():
                item.set_facebook(fb)

        item.sources.append(response.url)

        yield item

    def website_fail(self, failure: Failure):
        item = failure.request.meta["item"]
        item.set_website(None)
        yield item
