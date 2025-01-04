import argparse
import logging
import os
from dataclasses import dataclass, asdict

import pandas as pd

from apartment_finder import AparmentFinder
from app_config import set_config, AppConfig, config
from nexo_finder import NexoFinder

logging.basicConfig(format='%(asctime)s - %(message)s', level=logging.INFO)
log = logging.getLogger(__name__)


@dataclass
class AppArgs:
    output_type: str
    output_dir: str
    test: bool = False
    use_cache: bool = False


def write_data(data: list, args: AppArgs):
    def write_excel(data: list):
        filename = os.path.join(args.output_dir, "result.xlsx")
        log.info(f"Writing data to Excel: {filename}")
        df = pd.DataFrame(data)
        df.to_excel(filename, index=False)

    def write_sqlite(data: list):
        filename = os.path.join(args.output_dir, "result.sqlite")
        log.info(f"Writing data to SQLite3: {filename}")

        url_connection = f"sqlite:///{filename}"
        df = pd.DataFrame(data)
        df.to_sql("apartments", url_connection, if_exists="replace", index=False)

    if args.output_type == "all":
        write_excel(data)
        write_sqlite(data)
    elif args.output_type == "sqlite3":
        write_sqlite(data)
    elif args.output_type == "excel":
        write_excel(data)


def set_new_config(args: AppArgs):
    new_config = AppConfig(**asdict(config))
    new_config.test = args.test
    new_config.nexo_use_cache = args.use_cache
    set_config(new_config)

    log.info(f"Using config: {new_config}")


def main(args: AppArgs):
    set_new_config(args)
    finder: AparmentFinder = NexoFinder()
    data = finder.get_all()
    # sorting data by price_soles column asc
    data = sorted(data, key=lambda x: x.price_soles)
    write_data(data, args)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Process some integers.')
    parser.add_argument('-o', '--output', type=str, choices=['all', 'sqlite3', 'excel'],
                        help='Output format (default: excel)', default='excel')
    parser.add_argument('-od', '--output-dir', type=str, help='Directory to save the output files', default='.')
    parser.add_argument("--use-cache", action="store_true",
                        help="When true, the html scrapped are saved to re-use next run.", default=False)
    parser.add_argument("--test", action="store_true",
                        help="Only process one single record to finish quickly and check if everything works as expected",
                        default=False)
    args = parser.parse_args()

    app_args = AppArgs(
        output_type=args.output,
        output_dir=args.output_dir,
        test=args.test,
        use_cache=args.use_cache,
    )
    main(app_args)
