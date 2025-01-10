import argparse
import ftplib
import json
import logging
import os
import sqlite3
import sys
from dataclasses import dataclass

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)
log = logging.getLogger(__name__)


@dataclass
class AppArgs:
    filename_sqlite3_db: str
    ftp_server: str
    ftp_user: str
    ftp_password: str
    ftp_filename: str


def __write_json_file(data: list[dict], filename_json: str):
    log.info(f"Write JSON to file '{filename_json}'")

    new_data = []
    for item in data:
        new_data.append(
            {
                "created_at": item.get("created_at"),
                "name": item.get("name"),
                "district": item.get("district"),
                "price_soles": item.get("price_soles"),
                "area_m2": item.get("area_m2"),
            }
        )

    with open(filename_json, "w", encoding="utf-8") as myfile:
        json.dump(data, myfile)


def __query_data_sqlite3(database_path, query) -> list[dict]:
    log.info(f"Query data from SQLite database '{database_path}'")
    conn = sqlite3.connect(database_path)

    try:
        cursor = conn.cursor()
        cursor.execute(query)

        columns = [description[0] for description in cursor.description]
        results = []
        for row in cursor.fetchall():
            row_dict = {columns[i]: row[i] for i in range(len(columns))}
            results.append(row_dict)
        return results

    except sqlite3.Error as e:
        log.error(f"SQLite3 query error: {query} - Error: {e}")

    finally:
        conn.close()


def __upload_file(filename: str, args: AppArgs):
    log.info(f"Uploading file '{filename}'")
    ftp = ftplib.FTP()
    try:
        ftp.connect(args.ftp_server, 21)  # TODO> replace to FTPS
        ftp.login(args.ftp_user, args.ftp_password)
        with open(filename, "rb") as file:
            ftp.storbinary(f"STOR {args.ftp_filename}", file)
        log.info(f"File uploaded successfully: {filename}")
    except ftplib.all_errors as e:
        log.error(f"FTP error during upload: {e}")
    finally:
        ftp.quit()


def main(args: AppArgs):
    log.info(f"Arguments used are: {args}")

    # check if file exists
    if not os.path.exists(args.filename_sqlite3_db):
        log.error(f"SQLite3 DB file not found: {args.filename_sqlite3_db}")
        sys.exit(1)

    sql = "select * from apartments order by investment_ratio DESC limit 5"
    data = __query_data_sqlite3(args.filename_sqlite3_db, sql)

    log.info(f"Query result count: {len(data)}")

    tmp_filename = "apartment_list.json"
    __write_json_file(data, tmp_filename)
    __upload_file(tmp_filename, args)

    os.remove(tmp_filename)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Process apartment data using SQLite3 and FTP."
    )

    # Add arguments to the parser
    parser.add_argument(
        "--sqlite-db", type=str, required=True, help="Path to the SQLite3 database file"
    )
    parser.add_argument(
        "--ftp-user", type=str, required=True, help="FTP username for uploading data"
    )
    parser.add_argument(
        "--ftp-password",
        type=str,
        required=True,
        help="FTP password for uploading data",
    )
    parser.add_argument(
        "--ftp-filename",
        type=str,
        required=True,
        help="Filename to use when uploading data",
    )
    parser.add_argument(
        "--ftp-server",
        type=str,
        required=True,
        help="FTP server address",
    )

    # Parse arguments
    args = parser.parse_args()

    # Call the main function with parsed arguments
    main(
        AppArgs(
            filename_sqlite3_db=args.sqlite_db,
            ftp_user=args.ftp_user,
            ftp_password=args.ftp_password,
            ftp_filename=args.ftp_filename,
            ftp_server=args.ftp_server,
        )
    )
