import logging
import os
import time

import requests
from bs4 import BeautifulSoup
from selenium import webdriver
from slugify import slugify

from apartment_finder import Apartment
from app_config import config
from utils import to_number

CUR_DIR = os.path.dirname(__file__)
NEXO_CACHE_DIR = os.path.join(CUR_DIR, "nexo_cache")

os.makedirs(NEXO_CACHE_DIR, exist_ok=True)


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


def search_and_get_html_requests(url: str) -> str:
    cache = get_from_cache(url)
    if cache:
        return cache

    try:
        time.sleep(0.5)
        response = requests.get(url)
        html_content = response.text

        save_to_cache(url, html_content)

        return html_content
    except Exception as e:
        logging.error("Error searching for %s", url)
        logging.error(e)
        return "<html></html>"


def search_and_get_html_chrome(url: str) -> str:
    cache = get_from_cache(url)
    if cache:
        return cache

    try:
        driver = webdriver.Chrome()

        driver.get(url)

        time.sleep(2)

        html_content = driver.page_source
        driver.quit()

        save_to_cache(url, html_content)

        return html_content
    except Exception as e:
        logging.error("Error searching for %s", url)
        logging.error(e)
        return "<html></html>"


def get_from_cache(url: str) -> str | None:
    if not config.nexo_use_cache:
        return None

    name = slugify(url)
    filename = os.path.join(NEXO_CACHE_DIR, f"{name}.html")
    if os.path.exists(filename):
        with open(filename, "r") as file:
            return file.read()
    return None


def save_to_cache(url: str, html_content: str) -> None:
    name = slugify(url)
    filename = os.path.join(NEXO_CACHE_DIR, f"{name}.html")
    with open(filename, "w") as file:
        file.write(html_content)
