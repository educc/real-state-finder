import logging

import pandas as pd

from apartment_finder import AparmentFinder
from nexo_finder import NexoFinder

logging.basicConfig(format='%(asctime)s - %(message)s', level=logging.INFO)


def write_excel(data: list, file_name: str = 'output.xlsx'):
    df = pd.DataFrame(data)
    df.to_excel(file_name, index=False)


def main():
    finder: AparmentFinder = NexoFinder()
    data = finder.get_all()
    # sorting data by price_soles column asc
    data = sorted(data, key=lambda x: x.price_soles)
    write_excel(data)


if __name__ == "__main__":
    main()
