# ai-agent for depabarato.com
This is a WhatsApp AI agent to help users find the best deals on depabarato.com. This is a fastapi application that
listens to whatsapp messages and responds to them. It uses Ollama API to translate the user question to a SQL Where clause
then it queries a sqlite database to find the most cheap apartments in Lima.

## requirements
- python 3.13
- install requirements.txt `pip install -r requirements.txt`

## Environment variables
You can get the whatsapp information from https://developers.facebook.com/apps

- OLLAMA_BASE_URL: required
- WHATSAPP_VERIFY_TOKEN: required
- WHATSAPP_PHONE_NUMBER: required
- WHATSAPP_ACCESS_TOKEN: required
- DATABASE_SQLITE_FILENAME: optional (default: "result.sqlite")

## How to run
```sh
uvicorn main:app --host 0.0.0.0 --port 8000
```