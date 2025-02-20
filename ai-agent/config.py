import os
import logging

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
log = logging.getLogger(__name__)

DATABASE_SQLITE_FILENAME = os.environ.get("DB_FILENAME", "result.sqlite")