import logging
import os

from apartment_finder import Apartment
from mydb import MyDb, create_table_sql, insert_sql
from nexo_finder import NexoFinder

logging.basicConfig(format='%(asctime)s - %(name)s - %(message)s', level=logging.INFO)
log = logging.getLogger(__name__)

CUR_DIR = os.path.dirname(__file__)
NEXO_CACHE_DIR = os.path.join(CUR_DIR, "nexo_web")
DB_FILE = os.path.join(NEXO_CACHE_DIR, "nexo_web.sqlite3")

os.makedirs(NEXO_CACHE_DIR, exist_ok=True)


class ApartmentDb:

    def __init__(self):
        self.db: MyDb = ApartmentDb.__setup_db()

    @staticmethod
    def __setup_db() -> MyDb:
        log.info("Setting up DB")
        db = MyDb(DB_FILE)

        scripts: list[str] = [
            create_table_sql(Apartment),
            "CREATE INDEX IF NOT EXISTS idx_apartment_id ON Apartment(id);",
        ]

        db.setup_db(scripts)
        return db

    def add(self, fn_get_apartments):
        if self.db.count(Apartment) > 0:
            log.info("Apartments already loaded. Skipping...")
            return

        apartments = fn_get_apartments()
        total = len(apartments)

        current = 1
        for sql, values in insert_sql(Apartment, apartments):
            self.db.execute(sql, values)
            log.info("Loading apartments %d/%d", current, total)
            current += 1


def main():
    db = ApartmentDb()

    nexo = NexoFinder()
    db.add(lambda: nexo.get_all())


if __name__ == "__main__":
    # TODO: issue, the loading is duplicating the apartments in sqlite3
    main()
