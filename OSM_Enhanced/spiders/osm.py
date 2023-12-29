from pathlib import Path
from typing import Any

from scrapy import Spider
from scrapy.http import Response

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

            yield item
