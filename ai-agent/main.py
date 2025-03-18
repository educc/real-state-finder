import logging
from datetime import datetime, timedelta
from typing import Optional, List
from urllib.parse import urlencode

from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import PlainTextResponse

from config import WHATSAPP_VERIFY_TOKEN
from depabarato_agent import find_apartments
from whatsapp_client import whastapp_client

log = logging.getLogger(__name__)

app = FastAPI()


LAST_MSG_EXPIRATION_MINUTES = 15
users_last_message: dict[str, datetime] = {}

WELCOME_MESSAGE = "".join([
    "Hola, soy David el asistente virtual de depabarato.com\n",
    "Yo puedo ayudarte a buscar el departamento más barato en Lima según tus necesidades\n",
    "\n",
    "Ejemplos de consultas de nuestros usuarios:\n",
    "- quiero un depa en san miguel\n",
    "- un depa en Lince con tres dormitorios\n",
    "- busco depa en San Isidro de al menos 100 m2\n",
    "- en San Martin de Porras con 3 cuartos\n",
    "- mínimo 70 m2 y 3 cuartos\n",
    "\n",
    "Dime tu consulta en un solo mensaje y buscaré el departamento más barato para ti",
])


def __is_first_message(phone: str) -> bool:
    """
    Returns True if there is no stored last message timestamp or if the last
    message was sent more than the specified number of minutes ago.
    """

    global users_last_message
    now = datetime.now()

    last_msg_time = users_last_message.get(phone, datetime(2000, 1,1))
    last_msg_plus_exp_time = last_msg_time + timedelta(minutes=LAST_MSG_EXPIRATION_MINUTES)

    users_last_message[phone] = now
    if last_msg_plus_exp_time < now:
        return True
    return False

def __build_message_for_apartment(apartment: dict) -> str:
    def __build_google_search_url(text):
        base_url = "https://www.google.com/search?"
        query_params = {'q': text}
        url = base_url + urlencode(query_params)
        return url

    url = __build_google_search_url("proyecto " + apartment['name'] + " en Lima")

    response = ""
    response += f"{apartment['district']} - {apartment['name']}\n"
    response += f"S/ {int(apartment['price_soles'])}   {int(apartment['area_m2'])} m2 \n"
    response += f"{apartment['bedrooms']} 🛏️\n"
    response += f"{url}️\n"
    return response

def find_apartments_user_reply(user_question: str) -> str:
    """
    Find the apartments that match the user question
    :param user_question:
    :return:
    """
    try:

        has_error, apartments = find_apartments(user_question)
        if has_error:
            return "Lo siento, no pude encontrar departamentos para ti."

        if apartments is None or len(apartments) == 0:
            return "Lo siento, no pude encontrar departamentos para ti."

        response = "Aquí tienes los departamentos que encontré para ti:\n\n"
        for apartment in apartments:
            response += __build_message_for_apartment(apartment) + "\n"
        response += "Seguiré aquí para más consultas..."
        return response
    except Exception as ex:
        log.error(f"At find_apartments_user_reply, error={ex}")
        return "Oops, algo inesperado pasó, por favor escriba nuevamente su consulta"


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
    log.info(f"GET request: {request.url}")
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
    log.info(f"POST request: {request.url}")
    body = await request.json()
    messages = get_messages_from_whatsapp(body)
    if not messages:
        logging.error("No messages found")
        return PlainTextResponse(content="", status_code=200)

    log.debug(f"messages: {messages}")
    to_phone = messages[0].get("from")
    log.info(f"message={messages[0]}, from={to_phone}")

    if __is_first_message(to_phone):
        whastapp_client.send_text(WELCOME_MESSAGE, to_phone)
        return

    user_question = messages[0].get("text", {}).get("body")
    user_reply = find_apartments_user_reply(user_question)
    log.debug(f"user_reply: {user_reply}")
    whastapp_client.send_text(user_reply, to_phone)


@app.post("/api/depabarato", response_class=PlainTextResponse)
async def handle_post(request: Request):
    """
    The question coming from the body payload.
    """
    log.info(f"POST request: {request.url}")
    body = await request.json()
    user_question = body.get("question")
    if not user_question:
        log.error("No user question found in the request")
        return PlainTextResponse(content="No user question found in the request", status_code=400)

    user_reply = find_apartments_user_reply(user_question)
    log.debug(f"user_reply: {user_reply}")
    return PlainTextResponse(content=user_reply, status_code=200)
