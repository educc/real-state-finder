from dataclasses import dataclass

CONSTRUCTION_STATUS = {
    "1": "Planos",
    "2": "En construcción",
    "3": "Entregado"
}


@dataclass
class Apartment:
    name: str
    address: str
    district: str
    construction_status: str
    delivery_date: str
    price_soles: float
    bedrooms: int
    bathrooms: int
    area_m2: float
    url: str
    builder: str = ""
    bank: str = ""
    phones: str = ""
    url_location: str = ""
    id: str = ""


class AparmentFinder:

    def get_all(self) -> list[Apartment]:
        return []
