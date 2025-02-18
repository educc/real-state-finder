import logging
import sqlite3
from dataclasses import asdict, fields
from sqlite3 import Error
from typing import get_type_hints

log = logging.getLogger(__name__)


def insert_sql(dataclass, instance_list):
    table_name = dataclass.__name__.lower()
    field_names = [f.name for f in fields(dataclass)]
    columns = ', '.join(field_names)

    placeholders = ', '.join(['?' for _ in field_names])
    sql = f"INSERT INTO {table_name} ({columns}) VALUES ({placeholders});"

    sql_statements = []
    for instance in instance_list:
        values = tuple(asdict(instance).values())
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

    table_name = dataclass.__name__.lower()
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
            conn.row_factory = sqlite3.Row
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
            log.error(e)
        finally:
            conn.close()

    def query(self, sql: str) -> list[dict]:
        conn = self.__create_connection()
        try:
            cursor = conn.cursor()
            cursor.execute(sql)
            rows = cursor.fetchall()
            return [dict(row) for row in rows]  # convert each row to a dictionary
        except Error as e:
            log.error("At getting all")
            log.error(e)
        finally:
            conn.close()
        return None

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
            log.error("At executing sql")
            log.error(e)
        finally:
            conn.close()

    def single(self, sql: str) -> object:
        conn = self.__create_connection()
        try:
            rows = self.query(sql)
            if not rows:
                return None
            return rows[0]
        except Error as e:
            log.error("At single sql")
            log.error(e)
        finally:
            conn.close()

    def count(self, dataclass):
        table_name = dataclass.__name__
        conn = self.__create_connection()
        try:
            sql = f"SELECT COUNT(*) as total FROM {table_name};"
            return self.single(sql)["total"]
        except Error as e:
            log.error("At count sql")
            log.error(e)
        finally:
            conn.close()

    def all(self, dataclass):
        table_name = dataclass.__name__
        conn = self.__create_connection()
        try:
            sql = f"SELECT * FROM {table_name};"
            rows = self.query(sql)
            return [dataclass(**row) for row in rows]
        except Error as e:
            log.error("At getting all")
            log.error(e)
        finally:
            conn.close()

    def insert_all(self, dataclass, instance_list):
        if not isinstance(instance_list, list) or not all(isinstance(i, dataclass) for i in instance_list):
            raise ValueError("A list of instances of the specified dataclass is required.")

        sql_statements = insert_sql(dataclass, instance_list)

        conn = self.__create_connection()
        try:
            cursor = conn.cursor()
            for sql, values in sql_statements:
                cursor.execute(sql, values)
            conn.commit()
        except Error as e:
            log.error("At inserting all instances")
            log.error(e)
        finally:
            conn.close()
    #
