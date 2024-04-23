import json
import logging
import re
import time
from dataclasses import dataclass, field

import requests
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.by import By

from apartment_finder import Apartment, AparmentFinder
from app_config import config
from utils import to_number


def parse_apartments(html_content: str) -> list[Apartment]:
    try:
        soup = BeautifulSoup(html_content, 'html.parser')

        # To find elements by CSS selector
        elements = soup.select('.Project-available-model .bottom-info')

        result: list[Apartment] = []
        for element in elements:
            bedroom = int(element.select(".bedroom")[0].text.strip())
            area_str = element.select(".area")[0].text.strip()
            price_str = element.select(".price")[0].text.strip()

            price = to_number(price_str)
            if "$" in price_str:
                price = price * config.exchange_rate_pen_usd
                price = round(price, 2)

            result.append(Apartment(
                name="",
                address="",
                district="",
                construction_status="",
                price_soles=price,
                bedrooms=bedroom,
                bathrooms=0,
                area_m2=to_number(area_str),
                url=""
            ))

        logging.info("Found %d apartments", len(result))
        return result
    except Exception as e:
        logging.error("Error parsing apartments")
        logging.error(e)
        return []


def search_and_get_html_v2(slug: str) -> str:
    try:
        driver = webdriver.Chrome()

        url: str = f"https://nexoinmobiliario.pe/proyecto/venta-de-departamento-{slug}"

        logging.info("Searching for: %s", url)

        driver.get(url)

        time.sleep(2)

        html_content = driver.page_source
        driver.quit()
        return html_content
    except Exception as e:
        logging.error("Error searching for %s", slug)
        logging.error(e)
        return "<html></html>"


def search_and_get_html(slug: str) -> str:
    # Set up the WebDriver to use Chrome
    try:
        driver = webdriver.Chrome()

        search_text: str = f"{slug} site: nexoinmobiliario.pe"
        driver.get("https://www.google.com/search?q=" + search_text)

        # Wait for the page to load
        time.sleep(2)

        logging.info("Searching for: %s", search_text)

        # Click on the first search result
        results = driver.find_elements(By.TAG_NAME, 'a')
        for it in results:
            link = it.get_attribute('href')
            if link is not None and slug in link and "https://nexoinmobiliario.pe" in link:
                it.click()
                break
        # end-for

        time.sleep(2)

        html_content = driver.page_source
        driver.quit()
        return html_content
    except Exception as e:
        logging.error("Error searching for %s", slug)
        logging.error(e)
        return "<html></html>"


@dataclass
class ProjectInfo:
    area_max: str | None = None
    area_min: str | None = None
    bathroom_max: str | None = None
    bathroom_min: str | None = None
    builder_name: str | None = None
    builder_slug: str | None = None
    cantidad: str | None = None
    cintillo_principal: str | None = None
    coin: str | None = None
    coord_lat: str | None = None
    direccion: str | None = None
    distrito: str | None = None
    dpto_project: str | None = None
    finance_bank: str | None = None
    gallery: list[str] = field(default_factory=list)
    gallery_big: list[str] = field(default_factory=list)
    gallery_xm: list[str] = field(default_factory=list)
    image: str | None = None
    important_level: str | None = None
    is_featured: str | None = None
    keyword: str | None = None
    logo_empresa: str | None = None
    long: str | None = None
    min_price: str | None = None
    name: str | None = None
    parking_max: str | None = None
    parking_min: str | None = None
    project_cell_phone: str | None = None
    project_contact: str | None = None
    project_email: str | None = None
    project_id: str | None = None
    project_phase: str | None = None
    project_phone: str | None = None
    project_whatsapp: str | None = None
    provincia_project: str | None = None
    room_max: str | None = None
    room_min: str | None = None
    services: str | None = None
    slug: str | None = None
    socio_asei: str | None = None
    tiene_promo_fn: str | None = None
    tour_virtual: str | None = None
    type_project: str | None = None
    url: str | None = None
    url_video: str | None = None
    val_price1: str | None = None
    val_price2: str | None = None
    visibility_ferianexo: str | None = None
    visibility_in_feria_nexo: str | None = None
    visibility_semananexo: str | None = None

    def __post_init__(self):
        # Convert comma-separated strings to lists
        self.gallery = self.gallery.split(',') if self.gallery else []
        self.gallery_xm = self.gallery_xm.split(',') if self.gallery_xm else []
        self.gallery_big = self.gallery_big.split(
            ',') if self.gallery_big else []


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
            logging.info("Processing project %d/%d: %s", i + 1, total, project.slug)
            apartments = self.__find_by_project(project)
            for apartment in apartments:
                apartment.name = project.name
                apartment.address = project.direccion
                apartment.district = project.distrito
                apartment.url = project.url
                apartment.construction_status = project.project_phase
            items.extend(apartments)

        return items

    def __find_by_project(self, project: ProjectInfo) -> list[Apartment]:
        html_content: str = search_and_get_html_v2(project.slug)
        return parse_apartments(html_content)

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
