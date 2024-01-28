from OSM_Enhanced.items.poi import PoiItem


def test_get_tags():
    item = PoiItem(
        tags={
            "name": "Hello World",
            "website": "https://example.org/",
            "contact:phone": "+33 6 39 98 13 37",
        },
    )
    assert item.get_name() == "Hello World"
    assert item.get_website() == "https://example.org/"
    assert item.get_phone() == "+33 6 39 98 13 37"


def test_set_tags():
    item = PoiItem(
        tags={
            "name": "Hello World",
            "website": "https://example.org/",
            "contact:phone": "+33 6 39 98 13 37",
        }
    )
    item.set_name("Good Bye!")
    item.set_website("https://example.org/aaa")
    item.set_phone("+33 6 39 98 00 00")
    assert item.tags["name"] == "Good Bye!"
    assert item.tags["website"] == "https://example.org/aaa"
    assert item.tags["phone"] == "+33 6 39 98 00 00"
    assert "contact:phone" not in item.tags


def test_del_operations():
    item = PoiItem(
        tags={
            "name": "Hello World",
            "website": "https://example.org/",
            "contact:phone": "+33 6 39 98 13 37",
        },
    )
    item.del_tags(["name", "website", "contact:phone"])
    assert len(item.operations) == 3
    assert len(item.tags) == 0


def test_bad_website():
    item = PoiItem(tags={"website": "https://example.org/"})
    item.set_website(None)
    assert len(item.tags) == 0
