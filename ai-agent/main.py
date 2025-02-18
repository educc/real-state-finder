import logging
import sys

from agent import ask_agent
from mydb import MyDb

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
log = logging.getLogger(__name__)


db = MyDb("result.sqlite")

# create table main.apartments
# (
#     created_at          DATE,
# name                TEXT,
# address             TEXT,
# district            TEXT,
# construction_status TEXT,
# delivery_date       TEXT,
# price_soles         FLOAT,
# bedrooms            BIGINT,
# bathrooms           BIGINT,
# area_m2             FLOAT,
# common_area_count   BIGINT,
# rent_price_soles    BIGINT,
# investment_ratio    FLOAT,
# url                 TEXT,
# url_location        TEXT,
# builder             TEXT,
# bank                TEXT,
# phones              TEXT,
# id                  TEXT
# );


def generate_query(user_question: str) -> str:
    """"
        This funtion asks ollama to generate the SQL query
    """
    ai_response =  ask_agent(user_question)
    sql_query = ai_response["message"]["content"]
    log.info("query generated:")
    log.info(sql_query)
    return sql_query

def build_apartment_message(row: dict) -> str:
    district = row["district"]
    price_soles = round(row["price_soles"])
    name = row["name"]
    area = row["area_m2"]
    bedrooms = row["bedrooms"]
    delivery_date = row["delivery_date"]

    return f"{district} | {name} | S/ {price_soles} | {bedrooms} | {area} m2 | {delivery_date}"

def get_user_answer(query: str) -> str:
    rows = db.query(query)
    if len(rows) == 0:
        return "No encontramos departamentos para tu búsqueda."

    answer = ""
    for row in rows[0:3]:
        answer = answer + "\n" + build_apartment_message(row)
    return answer

def main():
    while(True):
        print("Qué departamento buscas:")
        user_question = input()
        #user_question = "lo mas barato en san miguel de dos dormitorios"

        if (user_question == ""):
            sys.exit(0)

        sql_query = generate_query(user_question)
        answer = get_user_answer(sql_query)
        print(answer)
    #

if __name__ == '__main__':
    main()