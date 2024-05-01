import json
import logging
import re

import requests
from slugify import slugify

from apartment_finder import Apartment, AparmentFinder, CONSTRUCTION_STATUS
from nexo_downloader import parse_apartments, search_and_get_html_requests
from nexo_models import ProjectInfo


def _find_by_project(url: str) -> list[Apartment]:
    html_content: str = search_and_get_html_requests(url)
    return parse_apartments(html_content)


def _get_googlemap_url(lat: str, long: str) -> str:
    return f"https://www.google.com/maps/search/?api=1&query={lat},{long}"


def _get_phones(project: ProjectInfo) -> str:
    phone_list = [project.project_cell_phone, project.project_phone, project.project_whatsapp]
    phones = [i for i in phone_list if len(i) > 0]
    return ",".join(phones)


class NexoFinder(AparmentFinder):

    def __init__(self, url: str | None = None) -> None:
        self.url = "https://nexoinmobiliario.pe/busqueda/venta-de-departamentos-en-lima-lima-1501"
        if url:
            self.url = url

    def get_all(self) -> list[Apartment]:
        raw_data: list[ProjectInfo] = self.__get_raw_data()

        items: list[Apartment] = []
        total = len(raw_data)
        for i, project in enumerate(raw_data):
            percent = round((i + 1) / total * 100)
            logging.info("Processing project %d%% (%d/%d): %s", percent, i + 1, total, project.slug)

            url: str = f"https://nexoinmobiliario.pe/proyecto/venta-de-departamento-{project.slug}"
            apartments = _find_by_project(url)

            for apartment in apartments:
                apartment.id = slugify(f"{project.slug}-{project.distrito}-{apartment.bedrooms}-{apartment.area_m2}")
                apartment.name = project.name
                apartment.address = project.direccion
                apartment.district = project.distrito
                apartment.url = url
                apartment.construction_status = CONSTRUCTION_STATUS[project.project_phase]
                apartment.url_location = _get_googlemap_url(project.coord_lat, project.long)
                apartment.builder = project.builder_name
                apartment.bank = project.finance_bank
                apartment.phones = _get_phones(project)
            items.extend(apartments)
        # end for

        return items

    def __get_raw_data(self) -> list[ProjectInfo]:
        html_text = requests.get(self.url).text

        # extract from html the json that start with var search_data=

        pattern = r"var search_data=(\[.*?\]);"
        match = re.search(pattern, html_text, re.DOTALL)
        if match:
            list_dict = json.loads(match.group(1))
            return [ProjectInfo(**item) for item in list_dict]
        return []


if __name__ == "__main__":
    with open("example.html", "r") as file:
        parse_apartments(file.read())
