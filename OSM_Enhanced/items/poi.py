from dataclasses import dataclass
from enum import StrEnum
from typing import Dict


class OperationType(StrEnum):
    SET_TAGS = "setTags"
    UN_SET_TAGS = "unsetTags"


class Operation:
    operation: OperationType
    tags: Dict[str, str]
    keys: [str]

    def __init__(
        self, operation: OperationType, tags: Dict[str, str] = None, keys: [str] = None
    ):
        self.operation = operation
        self.tags = tags
        self.keys = keys

    def __repr__(self) -> str:
        return "Operation({}, {}, {})".format(self.operation, self.tags, self.keys)


@dataclass
class PoiItem:
    type: str
    id: int
    timestamp: str
    version: int
    geom = None
    tags: Dict[str, str]

    operations: [Operation]

    sources: [str]

    def __init__(
        self,
        type: str = "node",
        id: int = -1,
        timestamp: str = "",
        version: int = 1,
        geom=None,
        tags: Dict[str, str] = {},
    ):
        self.type = type
        self.id = id
        self.timestamp = timestamp
        self.version = version
        self.geom = geom
        self.tags = tags

        self.operations = []

        self.sources = [self.get_uri()]

    def set_tag(self, key: str, value: str):
        if value is None:
            self.del_tags([key])
        elif self.tags.get(key) != value:
            self.tags[key] = value
            self.operations.append(Operation(OperationType.SET_TAGS, tags={key: value}))

    def del_tags(self, keys: [str]):
        for key in keys:
            if self.tags.get(key):
                del self.tags[key]
                self.operations.append(Operation(OperationType.UN_SET_TAGS, keys=[key]))

    def get_name(self) -> str | None:
        return self.tags.get("name")

    def set_name(self, name: str):
        if name != self.get_name():
            self.set_tag("name", name)

    def get_website(self) -> str | None:
        return (
            self.tags.get("website")
            or self.tags.get("contact:website")
            or self.tags.get("url")
        )

    def set_website(self, website: str):
        if website != self.get_website():
            self.set_tag("website", website)
            self.del_tags(["contact:website", "url"])

    def get_phone(self) -> str | None:
        return self.tags.get("phone") or self.tags.get("contact:phone")

    def set_phone(self, phone: str):
        if phone != self.get_phone():
            self.set_tag("phone", phone)
            self.del_tags(["contact:phone"])

    def get_email(self) -> str | None:
        return self.tags.get("email") or self.tags.get("contact:email")

    def set_email(self, email: str):
        if email != self.get_email():
            self.set_tag("email", email)
            self.del_tags(["contact:email"])

    def get_postcode(self) -> str | None:
        return self.tags.get("addr:postcode") or self.tags.get("postal_code")

    def set_postcode(self, postcode: str):
        if postcode != self.get_postcode():
            self.set_tag("addr:postcode", postcode)
            self.del_tags(["postal_code"])

    def get_instagram(self) -> str | None:
        return self.tags.get("contact:instagram") or self.tags.get("instagram")

    def set_instagram(self, instagram: str):
        if instagram != self.get_instagram():
            self.set_tag("contact:instagram", instagram)
            self.del_tags(["instagram"])

    def get_facebook(self) -> str | None:
        return self.tags.get("contact:facebook") or self.tags.get("facebook")

    def set_facebook(self, facebook: str):
        if facebook != self.get_instagram():
            self.set_tag("contact:facebook", facebook)
            self.del_tags(["facebook"])

    def get_check_date(self) -> str | None:
        return self.tags.get("check_date") or self.tags.get("survey:date")

    def set_check_date(self, check_date: str):
        if check_date > self.get_check_date():
            self.set_tag("check_date", check_date)

    def get_uri(self) -> str:
        return "https://www.openstreetmap.org/{}/{}/history/{}".format(
            self.type, self.id, self.version
        )
