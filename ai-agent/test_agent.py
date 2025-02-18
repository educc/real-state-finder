import dataclasses
import json

from agent import ask_agent, ask_agent_content_json
from mydb import MyDb

DATASET_FILENAME = "./dataset/questions.json"

db = MyDb("result.sqlite")

@dataclasses.dataclass
class DatasetItem:
    question: str
    expected: str
    expected_item: str

def read_dataset() -> list[DatasetItem]:
    items = []
    with open(DATASET_FILENAME) as f:
        json_data = json.load(f)
        for it in json_data:
            item = DatasetItem(**it)
            if item.question != "":
                items.append(item)
    return items


def clean_llm_response(llm_response: str) -> str:
    # llm_response = llm_response.lower()
    # llm_response = llm_response.strip()
    # llm_response = llm_response.replace("where", "")
    # llm_response = llm_response.replace("`", "")
    return llm_response

def build_apartment_message(row: dict) -> str:
    district = row["district"]
    price_soles = round(row["price_soles"])
    name = row["name"]
    area = row["area_m2"]
    bedrooms = row["bedrooms"]
    delivery_date = row["delivery_date"]

    return f"{district} | {name} | S/ {price_soles} | {bedrooms} | {area} m2 | {delivery_date}"

def execute_query(where_clause: str):
    final_where_clause = clean_llm_response(where_clause)
    sql = f"select * from apartments where {final_where_clause} order by price_soles asc"
    print(f"final query: {sql}")
    data = db.query(sql)
    if data is None:
        return (True, None)

    if data and len(data) > 0:
        apartment_msg = build_apartment_message(data[0])
        return (False, apartment_msg)
    return (False, None)

def main():
    list_dataset = read_dataset()

    success_query_count = 0
    success_result_count = 0
    for item in list_dataset:
        question = item.question
        response: dict = ask_agent_content_json(question)
        where_clause = response["where_clause"]
        (has_error, db_response) = execute_query(where_clause)
        if not has_error:
            success_query_count += 1

        right_result = db_response == item.expected_item
        if right_result:
            success_result_count += 1

        print(f"user question: {question}")
        print(f"LLM response: {where_clause}")
        print(f"Query result: {db_response}")
        print(f"has_error: {has_error}")
        print(f"right result: {right_result}")
        print("-------")
    #

    success_ratio = success_query_count / len(list_dataset)
    success_ratio = round(success_ratio, 2)*100


    success_result_ratio = success_result_count / len(list_dataset)
    success_result_ratio = round(success_result_ratio, 2)*100
    print(f"Success query ratio: {success_query_count}/{len(list_dataset)} = {success_ratio}%")
    print(f"Success result ratio: {success_result_count}/{len(list_dataset)} = {success_result_ratio}%")
#

if __name__ == "__main__":
    main()