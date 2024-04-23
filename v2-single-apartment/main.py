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
    write_excel(data)


if __name__ == "__main__":
    main()
