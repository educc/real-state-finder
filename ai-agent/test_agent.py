import dataclasses
import json

from depabarato_agent import find_apartments

DATASET_FILENAME = "./dataset/questions.json"

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

def build_apartment_message(row: dict) -> str:
    district = row["district"]
    price_soles = round(row["price_soles"])
    name = row["name"]
    area = row["area_m2"]
    bedrooms = row["bedrooms"]
    delivery_date = row["delivery_date"]

    return f"{district} | {name} | S/ {price_soles} | {bedrooms} | {area} m2 | {delivery_date}"

def build_apartment_message_first(db_response: list[dict] | None) -> str:
    if db_response is None:
        return "NOT_FOUND"
    if len(db_response) == 0:
        return "NOT_FOUND"
    return build_apartment_message(db_response[0])

def main():
    list_dataset = read_dataset()

    success_query_count = 0
    success_result_count = 0
    for item in list_dataset:
        question = item.question
        (has_error, db_response) = find_apartments(question)
        first_item = build_apartment_message_first(db_response)
        if not has_error:
            success_query_count += 1

        right_result = first_item == item.expected_item
        if right_result:
            success_result_count += 1

        print(f"user question: {question}")
        print(f"Query result: {first_item}")
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