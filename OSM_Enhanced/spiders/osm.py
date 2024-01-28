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
            geom = poi.get("geometry")
            if not geom:
                if center := poi.get("center"):  # way/relation
                    geom = {
                        "type": "Point",
                        "coordinates": [center.get("lon", 0), center.get("lat", 0)],
                    }
                else:  # node
                    geom = {
                        "type": "Point",
                        "coordinates": [poi.get("lon", 0), poi.get("lat", 0)],
                    }

            item = PoiItem(
                poi["type"],
                poi["id"],
                poi.get("timestamp"),
                poi.get("version"),
                geom,
                poi["tags"],
            )

            if (
                (website := item.get_website())
                and not item.is_atp_domain()
                and not item.is_full()
            ):
                yield Request(
                    website,
                    self.parse_website,
                    meta={"item": item},
                    errback=self.website_fail,
                    headers={"Upgrade-Insecure-Requests": 1},
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

        if not item.get_facebook():
            if fb := response.xpath(
                '//a[contains(@href, "facebook.com/")][@href]/@href'
            ).get():
                item.set_facebook(fb)

        if not item.get_twitter():
            if twitter := response.xpath(
                '//a[contains(@href, "twitter.com/")][@href]/@href'
            ).get():
                item.set_twitter(twitter)

        item.sources.append(response.url)

        yield item

    def website_fail(self, failure: Failure):
        item = failure.request.meta["item"]
        item.set_website(None)
        yield item
