import logging
import sqlite3
from dataclasses import asdict, fields
from sqlite3 import Error
from typing import get_type_hints

log = logging.getLogger(__name__)


def insert_sql(dataclass, instances):
    table_name = dataclass.__name__
    field_names = [f.name for f in fields(dataclass)]
    columns = ', '.join(field_names)

    sql_statements = []
    for instance in instances:
        placeholders = ', '.join(['?' for _ in field_names])
        values = tuple(asdict(instance).values())
        sql = f"INSERT INTO {table_name} ({columns}) VALUES ({placeholders});"
        sql_statements.append((sql, values))

    return sql_statements


def create_table_sql(dataclass):
    type_mapping = {
        str: "TEXT",
        int: "INTEGER",
        float: "REAL",
    }

    columns = []
    for field in fields(dataclass):
        field_type = get_type_hints(dataclass)[field.name]
        sql_type = type_mapping.get(field_type, "TEXT")
        columns.append(f"{field.name} {sql_type}")

    table_name = dataclass.__name__
    columns_sql = ", ".join(columns)
    return f"CREATE TABLE IF NOT EXISTS {table_name} ({columns_sql});"


class MyDb:

    def __init__(self, filename: str):
        if not filename:
            raise ValueError("Filename for MyDb is required")

        self.filename_db = filename

    def __create_connection(self):
        try:
            conn = sqlite3.connect(self.filename_db)
            return conn
        except Error as e:
            log.error("At creating connection")
            log.error(e)

    def setup_db(self, sql_script_list: list[str]):
        conn = self.__create_connection()
        try:
            cursor = conn.cursor()
            for sql in sql_script_list:
                cursor.execute(sql)
        except Error as e:
            print(e)
        finally:
            conn.close()

    def query(self, sql: str) -> list[dict]:
        conn = self.__create_connection()
        try:
            cursor = conn.cursor()
            cursor.execute(sql)
            rows = cursor.fetchall()
            return rows
        except Error as e:
            log.error("At getting all")
            log.error(e)
        finally:
            conn.close()

    def execute(self, sql: str, values=None) -> None:
        conn = self.__create_connection()
        try:
            cursor = conn.cursor()
            if values:
                cursor.execute(sql, values)
            else:
                cursor.execute(sql)
            conn.commit()
        except Error as e:
            log.error("At executing parametrized query")
            log.error(e)
        finally:
            conn.close()
