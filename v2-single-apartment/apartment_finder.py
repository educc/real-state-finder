import datetime
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
    created_at: datetime.date = datetime.date.today()

    @staticmethod
    def from_dict(data: dict):
        return Apartment(
            name=data.get('name', ''),
            address=data.get('address', ''),
            district=data.get('district', ''),
            construction_status=data.get('construction_status'),
            delivery_date=data.get('delivery_date', ''),
            price_soles=data.get('price_soles', 0.0),
            bedrooms=data.get('bedrooms', 0),
            bathrooms=data.get('bathrooms', 0),
            area_m2=data.get('area_m2', 0.0),
            common_area_count=data.get('common_area_count', 0),
            rent_price_soles=data.get('rent_price_soles', 0),
            investment_ratio=data.get('investment_ratio', -1),
            url=data.get('url', ''),
            url_location=data.get('url_location', ''),
            builder=data.get('builder', ''),
            bank=data.get('bank', ''),
            phones=data.get('phones', ''),
            id=data.get('id', ''),
            created_at=data.get('created_at')
        )


class AparmentFinder:

    def get_all(self) -> list[Apartment]:
        return []
