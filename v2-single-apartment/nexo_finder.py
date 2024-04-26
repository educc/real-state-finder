import json
import logging
import re

import requests

from apartment_finder import Apartment, AparmentFinder
from nexo_downloader import parse_apartments, search_and_get_html_requests
from nexo_models import ProjectInfo


def _find_by_project(url: str) -> list[Apartment]:
    html_content: str = search_and_get_html_requests(url)
    return parse_apartments(html_content)


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
                apartment.name = project.name
                apartment.address = project.direccion
                apartment.district = project.distrito
                apartment.url = url
                apartment.construction_status = project.project_phase
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
