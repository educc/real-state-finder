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


def __build_dict_from_apartment(item: Apartment) -> dict:
    url = __build_google_search_url("proyecto " + item.name + " en Lima")

    return {
        "created_at": item.created_at,
        "name": item.name,
        "district": item.district,
        "price_soles": item.price_soles,
        "area_m2": item.area_m2,
        "delivery_date": item.delivery_date,
        "address": item.address,
        "bedrooms": item.bedrooms,
        "rent_price_soles": item.rent_price_soles,
        "url": url,
        "url_maps": item.url_location
    }


def __write_json_vip_file(data: list[dict], filename_json: str):
    new_data = []
    for item in data:
        new_list = []
        for apartment in item["list"]:
            new_apartment = __build_dict_from_apartment(apartment)
            new_apartment["phones"] = apartment.phones
            new_list.append(new_apartment)
        item["list"] = new_list
        new_data.append(item)

    with open(filename_json, "w", encoding="utf-8") as my_file:
        json.dump(new_data, my_file)


def __write_json_file(data: list[Apartment], filename_json: str):
    log.info(f"Write JSON to file '{filename_json}'")

    new_data = []
    for item in data:
        new_data.append(__build_dict_from_apartment(item))

    with open(filename_json, "w", encoding="utf-8") as my_file:
        json.dump(new_data, my_file)


def __calculation_investment_ratio(it: Apartment) -> float:
    rent_price = it.rent_price_soles or 1_000_000
    price_soles = it.price_soles or 1
    anual_rent_price = rent_price * 12
    investment_ratio = anual_rent_price / price_soles
    return investment_ratio


def __get_n_cheapest_apartment(size: int, db: MyDb) -> list[Apartment]:
    log.info(f"Getting {size} cheapest apartments")
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

    result = [it for it in data if __calculation_investment_ratio(it) <= 0.20]
    return result[0:size]


def __get_n_cheapest_apartment_by_district(district: str, size: int, db: MyDb) -> list[Apartment]:
    log.info(f"Getting {size} cheapest apartments by district {district}")
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
                and district = '{district}'
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

    log.info(sql)
    data_raw = db.query(sql)
    data = [Apartment.from_dict(it) for it in data_raw]

    result = [it for it in data if __calculation_investment_ratio(it) <= 0.20]
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

    # [2] Generating vip

    vip_list = []
    vip_list.append({
        "group": "Todo Lima",
        "district": "todo Lima",
        "list": top5
    })

    lima_top = [
        "San Isidro",
        "Miraflores",
        "Barranco",
        "San Borja",
        "Santiago De Surco",
    ]

    for district in lima_top:
        rows = __get_n_cheapest_apartment_by_district(district, 5, db)
        if len(rows) > 0:
            vip_list.append({
                "group": "Lima TOP",
                "district": district,
                "list": rows
            })
    #

    lima_centro = [
        "Cercado de lima",
        "Lince",
        "San Miguel",
        "Pueblo Libre",
        "La Victoria",
        "Magdalena Del Mar",
        "Jesus Maria",
    ]

    for district in lima_centro:
        rows = __get_n_cheapest_apartment_by_district(district, 5, db)
        if len(rows) > 0:
            vip_list.append({
                "group": "Lima Centro",
                "district": district,
                "list": rows
            })
    #

    filename = os.path.join(output_directory, "vip.json")
    __write_json_vip_file(vip_list, filename)
