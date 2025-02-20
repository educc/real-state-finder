import logging
import sys

from depabarato_agent import find_apartments
from llm_client import ask_agent
from mydb import db

log = logging.getLogger(__name__)

def log_apartment(user_question: str) -> str:
    """"
        This funtion asks ollama to generate the SQL query
    """
    has_error, rows =  find_apartments(user_question)
    if has_error or rows is None:
        log.error("Error finding apartments")
        return

    if len(rows) == 0:
        log.info("No apartments found")

    first = rows[0]
    log.info(build_apartment_message(first))

def build_apartment_message(row: dict) -> str:
    district = row["district"]
    price_soles = round(row["price_soles"])
    name = row["name"]
    area = row["area_m2"]
    bedrooms = row["bedrooms"]
    delivery_date = row["delivery_date"]

    return f"{district} | {name} | S/ {price_soles} | {bedrooms} | {area} m2 | {delivery_date}"


def main():
    while(True):
        print("Qué departamento buscas:")
        user_question = input()

        if (user_question == ""):
            sys.exit(0)

        log_apartment(user_question)
    #

if __name__ == '__main__':
    main()