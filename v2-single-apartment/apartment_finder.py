from dataclasses import dataclass, field
import requests
import re
import json


@dataclass
class Apartment:
    name: str
    address: str
    district: str
    construction_status: str
    price_soles: float
    bedrooms: int
    bathrooms: int
    area_m2: float
    url: str


class AparmentFinder:

    def get_all(self) -> list[Apartment]:
        return []


