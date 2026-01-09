import os
import requests

def send_whatsapp_text_safely(to_e164: str, body: str) -> None:
    token = os.getenv("WHATSAPP_TOKEN")
    phone_number_id = os.getenv("WHATSAPP_PHONE_NUMBER_ID")
    api_version = os.getenv("WHATSAPP_API_VERSION", "v18.0")
    if not token or not phone_number_id:
        return

    url = f"https://graph.facebook.com/{api_version}/{phone_number_id}/messages"
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json",
    }
    payload = {
        "messaging_product": "whatsapp",
        "to": to_e164.replace("+", ""),  # Meta örnekleri genelde ülke kodlu sayıyı + olmadan alır
        "type": "text",
        "text": {"body": body},
    }

    # Not: 24 saat penceresi dışındaysa "template message" gerekebilir.
    # MVP için sadece bildirim amaçlı deniyoruz.
    requests.post(url, headers=headers, json=payload, timeout=10)
