import logging
from typing import Optional, List

from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import PlainTextResponse

from config import WHATSAPP_VERIFY_TOKEN
from depabarato_agent import find_apartments
from whatsapp_client import whastapp_client

log = logging.getLogger(__name__)

app = FastAPI()


def find_apartments_user_reply(user_question: str) -> str:
    """
    Find the apartments that match the user question
    :param user_question:
    :return:
    """
    has_error, apartments = find_apartments(user_question)
    if has_error:
        return "Lo siento, no pude encontrar apartamentos para ti."

    if len(apartments) == 0:
        return "Lo siento, no pude encontrar apartamentos para ti."

    first = apartments[0]
    response = "Aquí tienes los apartamentos que encontré para ti:\n"
    response += f"Proyecto: {first['name']}\n"
    response += f"Distrito: {first['district']}\n"
    response += f"Precio: S/ {first['price_soles']}\n"
    response += f"Dormitorios: {first['bedrooms']}\n"
    response += f"Área: {first['area_m2']} m2\n"
    return response


def get_messages_from_whatsapp(body: dict) -> Optional[List[dict]]:
    """
    Extracts messages from the incoming body.
    This function simulates the validation and extraction of WhatsApp messages.
    """
    try:
        entries = body.get("entry", [])
        messages = []
        for entry in entries:
            changes = entry.get("changes", [])
            for change in changes:
                # Assuming your message schema is nested under 'value.messages'
                value = change.get("value", {})
                msgs = value.get("messages", [])
                for msg in msgs:
                    msg_type = msg.get("type")
                    if msg_type in ("text", "image"):
                        messages.append(msg)
                    else:
                        logging.info("Invalid message type: %s", msg_type)
        return messages if messages else None
    except Exception as e:
        logging.error("Error parsing messages: %s", e)
        return None

# --- FastAPI Endpoints ---

@app.get("/api/webhooks/whatsapp", response_class=PlainTextResponse)
async def handle_get(request: Request):
    """
    Endpoint used to verify the webhook.
    WhatsApp sends 'hub.verify_token' and expects the same 'hub.challenge' back.
    """
    hub_verify_token = request.query_params.get("hub.verify_token")
    hub_challenge = request.query_params.get("hub.challenge")
    if hub_verify_token == WHATSAPP_VERIFY_TOKEN:
        return PlainTextResponse(content=hub_challenge, status_code=200)
    else:
        logging.error("Invalid token, verifyToken=%s", hub_verify_token)
        raise HTTPException(status_code=403, detail="Forbidden")

@app.post("/api/webhooks/whatsapp", response_class=PlainTextResponse)
async def handle_post(request: Request):
    """
    Receives messages when someone sends a WhatsApp message.
    Processes text and image messages and dispatches them to the sales bot.
    """
    body = await request.json()
    messages = get_messages_from_whatsapp(body)
    if not messages:
        logging.error("No messages found")
        return PlainTextResponse(content="", status_code=200)

    log.info(f"messages: {messages}")
    to_phone = messages[0].get("from")
    user_question = messages[0].get("text", {}).get("body")

    user_reply = find_apartments_user_reply(user_question)

    log.info(f"user_reply: {user_reply}")
    whastapp_client.send_text(user_reply, to_phone)