import requests

from config import WHATSAPP_PHONE_NUMBER_ID, WHATSAPP_ACCESS_TOKEN


class WhatsappClientError(Exception):
    def __init__(self, message: str):
        super().__init__(message)
        self.name = 'WhatsappClientError'

class WhatsappClient:
    def __init__(self, phone_number: str, access_token: str):
        self.phone_number = phone_number
        self.access_token = access_token

    def send_text(self, message: str, to_phone: str) -> None:
        url = f"https://graph.facebook.com/v16.0/{self.phone_number}/messages"
        body = {
            "messaging_product": "whatsapp",
            "recipient_type": "individual",
            "to": to_phone,
            "type": "text",
            "text": {
                "preview_url": False,
                "body": message
            }
        }
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.access_token}"
        }
        response = requests.post(url, headers=headers, json=body)
        if response.status_code != 200:
            msg = f"Error sending whatsapp message: {response.text}"
            raise WhatsappClientError(msg)


whastapp_client = WhatsappClient(WHATSAPP_PHONE_NUMBER_ID, WHATSAPP_ACCESS_TOKEN)