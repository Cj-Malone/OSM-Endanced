from scrapy.exporters import JsonLinesItemExporter
from scrapy.utils.python import to_bytes

from OSM_Enhanced.items.poi import PoiItem


class MapRouletteGeoJsonExporter(JsonLinesItemExporter):
    def export_item(self, item: PoiItem):
        if len(item.operations) == 0:
            return  # No changes, no output
        ref = "{}/{}".format(item.type, item.id)
        item_dict = {
            "type": "FeatureCollection",
            "features": [
                {
                    "type": "Feature",
                    "id": ref,
                    "geometry": item.geom,
                    "properties": item.tags,
                }
            ],
            "cooperativeWork": {
                "meta": {"version": 2, "type": 1},
                "operations": [
                    {
                        "operationType": "modifyElement",
                        "data": {
                            "id": ref,
                            "operations": [o.get_dict() for o in item.operations],
                        },
                    }
                ],
            },
        }
        data = self.encoder.encode(item_dict) + "\n"
        self.file.write(to_bytes(data, self.encoding))
