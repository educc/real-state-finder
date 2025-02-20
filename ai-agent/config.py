import os
import logging
import sys
import requests

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
log = logging.getLogger(__name__)

OLLAMA_BASE_URL = os.environ.get("OLLAMA_BASE_URL", "http://localhost:11434")
DATABASE_SQLITE_FILENAME = os.environ.get("DB_FILENAME", "result.sqlite")
WHATSAPP_VERIFY_TOKEN = os.environ.get("WHATSAPP_VERIFY_TOKEN")
WHATSAPP_PHONE_NUMBER_ID = os.environ.get("WHATSAPP_PHONE_NUMBER_ID")
WHATSAPP_ACCESS_TOKEN = os.environ.get("WHATSAPP_ACCESS_TOKEN")

if not OLLAMA_BASE_URL:
    log.error("OLLAMA_BASE_URL is not set")
    sys.exit(-1)

if not WHATSAPP_VERIFY_TOKEN:
    log.error("WHATSAPP_VERIFY_TOKEN is not set")
    sys.exit(-1)

if not WHATSAPP_PHONE_NUMBER_ID:
    log.error("WHATSAPP_PHONE_NUMBER_ID is not set")
    sys.exit(-1)

if not WHATSAPP_ACCESS_TOKEN:
    log.error("WHATSAPP_ACCESS_TOKEN is not set")
    sys.exit(-1)

def __url_must_works(url: str) -> bool:
    try:
        requests.get(url, timeout=5)
    except requests.exceptions.RequestException as e:
        log.error(f"Could not connect to {url}, error: {e}")
        sys.exit(-1)

__url_must_works(OLLAMA_BASE_URL)