# ai-agent for depabarato.com
This is a WhatsApp AI agent to help users find the best deals on depabarato.com

## requirements
- python 3.13
- install requirements.txt `pip install -r requirements.txt`

## Environment variables
You can get the whatsapp information from https://developers.facebook.com/apps
- DATABASE_SQLITE_FILENAME: optional (default: "result.sqlite")
- WHATSAPP_VERIFY_TOKEN: required
- WHATSAPP_PHONE_NUMBER: required
- WHATSAPP_ACCESS_TOKEN: required

## How to run
- `python main.py`