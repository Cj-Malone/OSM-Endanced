from dataclasses import dataclass
from typing import Dict, Union


@dataclass
class PoiItem:
    type: str
    id: int
    timestamp: str
    version: int
    geom = None
    other_tags: Dict[str, str]

    sources: [str]

    name: Union[str, None] = None
    check_date: Union[str, None] = None

    website: Union[str, None] = None
    phone: Union[str, None] = None
    email: Union[str, None] = None

    postcode: Union[str, None] = None

    instagram: Union[str, None] = None
    facebook: Union[str, None] = None

    def __init__(
        self,
        type: str,
        id: int,
        timestamp: str,
        version: int,
        geom,
        tags: Dict[str, str],
    ):
        self.type = type
        self.id = id
        self.timestamp = timestamp
        self.version = version
        self.geom = geom
        self.other_tags = tags

        self.name = self.other_tags.pop("name")
        self.check_date = self.other_tags.pop(
            "check_date", self.other_tags.pop("survey:date", None)
        )

        self.website = self.other_tags.pop(
            "website",
            self.other_tags.pop("contact:website", self.other_tags.pop("url", None)),
        )
        self.phone = self.other_tags.pop(
            "phone", self.other_tags.pop("contact:phone", None)
        )
        self.email = self.other_tags.pop(
            "email", self.other_tags.pop("contact:email", None)
        )

        self.postcode = self.other_tags.pop(
            "addr:postcode", self.other_tags.pop("postal_code", None)
        )

        self.instagram = self.other_tags.pop(
            "contact:instagram", self.other_tags.pop("instagram", None)
        )
        self.facebook = self.other_tags.pop(
            "contact:facebook", self.other_tags.pop("facebook", None)
        )

        self.sources = [self.get_uri()]

    def get_last_modified(self) -> str:
        return self.check_date or self.timestamp

    def set_check_date(self, check_date: str, latest: bool = True):
        if not latest or not self.check_date:
            self.check_date = check_date
        else:
            # TODO
            if check_date > self.check_date:
                self.check_date = check_date

    def get_uri(self) -> str:
        return "https://www.openstreetmap.org/{}/{}#{}".format(
            self.type, self.id, self.version
        )
