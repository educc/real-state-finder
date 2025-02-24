import argparse
import logging
import os
from dataclasses import dataclass, asdict
from logging.handlers import RotatingFileHandler

import pandas as pd

from apartment_finder import Apartment, AparmentFinder
from app_config import set_config, AppConfig, config
from mydb import MyDb, create_table_sql
from nexo_finder import NexoFinder
from reporting import generate_reports

LOG_DIR = os.getenv("V2_SINGLE_APARTMENT_LOG_DIR", "/var/log")
os.makedirs(LOG_DIR, exist_ok=True)

# Set up logging
log_file = os.path.join(LOG_DIR, "v2-single-apartment.log")
formatter = logging.Formatter('%(levelname)s - %(asctime)s [%(name)s]  - %(message)s', datefmt='%Y-%m-%d %H:%M:%S')

file_handler = RotatingFileHandler(log_file, maxBytes=5 * 1024 * 1024, backupCount=0)
file_handler.setFormatter(formatter)

logging.basicConfig(level=logging.INFO,
                    handlers=[file_handler],
                    )

log = logging.getLogger(__name__)


@dataclass
class AppArgs:
    output_type: str
    output_dir: str
    test: bool = False
    use_cache: bool = False


def write_excel(excel_filename: str, data: list[Apartment]):
    log.info(f"Writing data to Excel: {excel_filename}")
    df = pd.DataFrame(data)
    df.to_excel(excel_filename, index=False)


def write_sqlite(db_filename: str, data: list[Apartment]):
    log.info(f"Writing data to SQLite: {db_filename}")
    db = MyDb(db_filename)
    sql_table = create_table_sql(Apartment)
    db.execute(sql_table)
    db.insert_all(Apartment, data)


def set_new_config(args: AppArgs):
    new_config = AppConfig(**asdict(config))
    new_config.test = args.test
    new_config.nexo_use_cache = args.use_cache
    set_config(new_config)

    log.info(f"Using config: {new_config}")


def main(args: AppArgs):
    set_new_config(args)
    # [1] Finding data
    finder: AparmentFinder = NexoFinder()
    data = finder.get_all()

    # sorting data by price_soles column asc
    data = sorted(data, key=lambda x: x.price_soles)
    #
    # # [2] writing data
    excel_filename = os.path.join(args.output_dir, 'result.xlsx')
    sqlite_filename = os.path.join(args.output_dir, 'result.sqlite')

    if args.output_type == "all":
        write_excel(excel_filename, data)
        write_sqlite(sqlite_filename, data)
    elif args.output_type == "sqlite3":
        write_sqlite(sqlite_filename, data)
    elif args.output_type == "excel":
        write_excel(excel_filename, data)

    # [3] Generating reports
    generate_reports(args.output_dir, sqlite_filename)


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
    parser.add_argument("--only-report", action="store_true",
                        help="Only generates the reports, no data is fetched",
                        default=False)
    args = parser.parse_args()

    if args.only_report:
        generate_reports(args.output_dir, "result.sqlite")
        exit(0)

    app_args = AppArgs(
        output_type=args.output,
        output_dir=args.output_dir,
        test=args.test,
        use_cache=args.use_cache
    )
    main(app_args)
