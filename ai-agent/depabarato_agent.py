import logging

from llm_client import ask_agent_content_json
from mydb import db

log = logging.getLogger(__name__)


def clean_llm_response(llm_response: str) -> str:
    # llm_response = llm_response.lower()
    # llm_response = llm_response.strip()
    # llm_response = llm_response.replace("where", "")
    # llm_response = llm_response.replace("`", "")
    return llm_response

def __is_safe_where_clause(where_clause: str) -> bool:
    """
    Check if the where clause is safe
    :param where_clause:
    :return:
    """
    lower_where = where_clause.lower()
    if "drop" in lower_where or "delete" in lower_where or "update" in lower_where:
        return False
    return True


def __get_n_cheapest_apartment(where_clause: str, size: int) -> list[dict]:
    sql = f"""
        WITH RankedApartments AS (
            SELECT
                *,
                ROW_NUMBER() OVER (PARTITION BY name ORDER BY price_soles) AS rn
            FROM
                apartment
            WHERE {where_clause}
        )
        SELECT *
        FROM RankedApartments
        WHERE rn = 1
        ORDER BY price_soles
        LIMIT {size};
    """
    log.debug(f"final query: {sql}")
    return db.query(sql)

def __execute_query(where_clause: str) -> tuple[bool, list[dict]]:
    """
    Execute the query in the database
    :param where_clause:
    :return: true if there is an error, false otherwise, and the data
    """
    log.info(f"where_clause: {where_clause}")
    if __is_safe_where_clause(where_clause) is False:
        log.info(f"The where clause is not safe. where_clause={where_clause}")
        return (True, None)

    final_where_clause = clean_llm_response(where_clause)
    data = __get_n_cheapest_apartment(final_where_clause, 3)
    if data is None:
        return (True, None)

    if data and len(data) > 0:
        return (False, data)
    return (False, None)

def find_apartments(user_question: str) -> tuple[bool, list[dict]]:
    """
    Find the apartments that match the user question
    :param user_question:
    :return:
    """
    response = ask_agent_content_json(user_question)
    where_clause = response["where_clause"]
    return __execute_query(where_clause)