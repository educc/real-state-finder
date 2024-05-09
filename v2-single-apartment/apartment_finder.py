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
    common_area_count: int = 0
    rent_price_soles: int = 0
    investment_ratio: float = -1
    url: str = ""
    url_location: str = ""
    builder: str = ""
    bank: str = ""
    phones: str = ""
    id: str = ""


class AparmentFinder:

    def get_all(self) -> list[Apartment]:
        return []
