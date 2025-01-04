import concurrent.futures
import json
import logging
import os
import re

import requests
from slugify import slugify

from apartment_finder import Apartment, AparmentFinder, CONSTRUCTION_STATUS
from app_config import is_test, thread_size
from nexo_downloader import parse_apartments, search_and_get_html_requests
from nexo_models import ProjectInfo

CUR_DIR = os.path.dirname(__file__)
RENT_JSON_FILE = os.path.join(CUR_DIR, "lima-rent.json")

log = logging.getLogger(__name__)


def _find_by_project(url: str) -> list[Apartment]:
    html_content: str = search_and_get_html_requests(url)
    return parse_apartments(html_content)


def _get_googlemap_url(lat: str, long: str) -> str:
    return f"https://www.google.com/maps/search/?api=1&query={lat},{long}"


def _get_phones(project: ProjectInfo) -> str:
    phone_list = [project.project_cell_phone, project.project_phone, project.project_whatsapp]
    phones = [i for i in phone_list if len(i) > 0]
    return ",".join(phones)


def _get_rent_map_by_district() -> dict[str, dict[str, int]]:
    data = []
    with open(RENT_JSON_FILE, "r") as file:
        data = json.load(file)

    result = {}
    for item in data:
        district = item["district"]
        if district not in result:
            result[district] = {}

        result[district][item["bedrooms"]] = item["rentPrice"]
    return result


class NexoFinder(AparmentFinder):

    def __init__(self, url: str | None = None) -> None:
        self.url = "https://nexoinmobiliario.pe/busqueda/venta-de-departamentos-en-lima-lima-1501"
        if url:
            self.url = url
        self.rent_map = _get_rent_map_by_district()

    def get_all(self) -> list[Apartment]:
        def find_apartment(project: ProjectInfo) -> (list[Apartment], str):
            url: str = f"https://nexoinmobiliario.pe/proyecto/venta-de-departamento-{project.slug}"
            return project, _find_by_project(url), url

        def find_apartments_from_list(raw_data: list[ProjectInfo]):
            for i, project in enumerate(raw_data):
                percent = round((i + 1) / total * 100)
                logging.info("Processing project %d%% (%d/%d): %s", percent, i + 1, total, project.slug)

                url: str = f"https://nexoinmobiliario.pe/proyecto/venta-de-departamento-{project.slug}"
                yield project, _find_by_project(url), url

        # end
        raw_data: list[ProjectInfo] = self.__get_raw_data()
        if is_test() and len(raw_data) > 0:
            log.info(f"Config test=true, using first project: {raw_data[0].slug}")
            raw_data = raw_data[0:1]

        items: list[Apartment] = []
        total = len(raw_data)

        log.info(f"Finding data from {total} projects")

        with concurrent.futures.ThreadPoolExecutor(max_workers=thread_size()) as executor:
            futures = [executor.submit(find_apartment, project) for project in raw_data]

            i = 0
            for future in concurrent.futures.as_completed(futures):
                project, apartments, url = future.result()

                percent = round((i + 1) / total * 100)
                logging.info("Processing project %d%% (%d/%d): %s", percent, i + 1, total, project.slug)

                for apartment in apartments:
                    self.__add_project_data_to_apartment(apartment, project, url)
                items.extend(apartments)
                i = i + 1
        # end with

        return items

    def __get_raw_data(self) -> list[ProjectInfo]:
        html_text = requests.get(self.url).text

        # extract from html the json that start with var search_data=

        pattern = r"var search_data=(\[.*?\]);"
        match = re.search(pattern, html_text, re.DOTALL)
        if match:
            list_dict = json.loads(match.group(1))
            return [ProjectInfo.from_dict(item) for item in list_dict]
        return []

    def __add_project_data_to_apartment(self, apartment: Apartment, project: ProjectInfo, url: str) -> None:
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
        apartment.rent_price_soles = self.rent_map.get(apartment.district, {}).get(apartment.bedrooms, -1)

        if apartment.rent_price_soles:
            try:
                apartment.investment_ratio = round(apartment.rent_price_soles / apartment.price_soles * 100, 2)
            except ZeroDivisionError:
                apartment.investment_ratio = -1


if __name__ == "__main__":
    with open("example.html", "r") as file:
        parse_apartments(file.read())
