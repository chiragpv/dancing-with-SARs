from dataclasses import dataclass
from enum import Enum


class SiteKey(str, Enum):
    BRAHMAPUTRA = "brahmaputra"
    WAYANAD = "wayanad"
    AMAZON = "amazon"
    LADAKH = "ladakh"


@dataclass(frozen=True)
class Site:
    key: SiteKey
    name: str
    latitude: float
    longitude: float
    description: str
