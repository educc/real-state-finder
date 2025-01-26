import json
import logging
import os
from urllib.parse import urlencode

from apartment_finder import Apartment
from mydb import MyDb

log = logging.getLogger(__name__)


def __build_google_search_url(text):
    base_url = "https://www.google.com/search?"
    query_params = {'q': text}
    url = base_url + urlencode(query_params)
    return url


def __write_json_file(data: list[Apartment], filename_json: str):
    log.info(f"Write JSON to file '{filename_json}'")

    new_data = []
    for item in data:
        url = __build_google_search_url("proyecto " + item.name + " en Lima")
        new_data.append(
            {
                "created_at": item.created_at,
                "name": item.name,
                "district": item.district,
                "price_soles": item.price_soles,
                "area_m2": item.area_m2,
                "delivery_date": item.delivery_date,
                "address": item.address,
                "bedrooms": item.bedrooms,
                "rent_price_soles": item.rent_price_soles,
                "url": url
            }
        )

    with open(filename_json, "w", encoding="utf-8") as myfile:
        json.dump(new_data, myfile)


def __get_n_cheapest_apartment(size: int, db: MyDb) -> list[Apartment]:
    row = db.query("select max(created_at) as latest from apartment")

    sql = f"""
        WITH RankedApartments AS (
            SELECT
                *,
                ROW_NUMBER() OVER (PARTITION BY name ORDER BY price_soles) AS rn
            FROM
                apartment
            WHERE
                rent_price_soles > 0
              $CREATED_CLAUSE
        )
        SELECT *
        FROM RankedApartments
        WHERE rn = 1
        ORDER BY price_soles
        LIMIT {size * 2};
    """
    if len(row) > 0:
        sql = sql.replace("$CREATED_CLAUSE", f" AND created_at = '{row[0]["latest"]}'")
    data_raw = db.query(sql)
    data = [Apartment.from_dict(it) for it in data_raw]

    def calculation_investment_ratio(it: Apartment) -> float:
        rent_price = it.rent_price_soles or 1_000_000
        price_soles = it.price_soles or 1
        anual_rent_price = rent_price * 12
        investment_ratio = anual_rent_price / price_soles
        return investment_ratio

    result = [it for it in data if calculation_investment_ratio(it) <= 0.20]
    return result[0:size]


def generate_reports(output_directory: str, database_filename: str) -> None:
    """
    Generate several files for each report configured
    :param output_directory:
    :param database_filename: to read the data
    :return:
    """
    log.info(f"Generating reports from SQLite database '{database_filename}'")

    db = MyDb(database_filename)

    # [1] Generating top 5 apartments (1 bedroom)

    filename = os.path.join(output_directory, "top.json")
    top5 = __get_n_cheapest_apartment(5, db)
    __write_json_file(top5, filename)
