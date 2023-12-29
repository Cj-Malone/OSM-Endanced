import requests
from scrapy import Selector, Spider

from OSM_Enhanced.items.poi import PoiItem


class WebsitePipeline:
    def process_item(self, item: PoiItem, spider: Spider):
        if not item.website:
            return item
        if "brand:wikidata" in item.other_tags:
            return item

        resp = requests.get(item.website)
        if resp.status_code != 200:
            # item.website = None
            return item

        sel = Selector(text=resp.text)

        if not item.phone:
            if phone := sel.xpath('//a[contains(@href, "tel:")][@href]/@href').get():
                item.phone = phone.removeprefix("tel:")
        if not item.email:
            if email := sel.xpath('//a[contains(@href, "mailto:")][@href]/@href').get():
                item.email = email.removeprefix("mailto:")

        if not item.instagram:
            item.instagram = sel.xpath(
                '//a[contains(@href, "instagram.com/")][@href]/@href'
            ).get()
        if not item.facebook:
            item.facebook = sel.xpath(
                '//a[contains(@href, "facebook.com/")][@href]/@href'
            ).get()

        item.sources.append(resp.url)

        return item
