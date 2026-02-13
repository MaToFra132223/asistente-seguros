import requests
import os
import json
from dotenv import load_dotenv

load_dotenv()

class WhatsAppAPIClient:
    def __init__(self):
        self.api_token = os.getenv("WHATSAPP_API_TOKEN")
        self.phone_number_id = os.getenv("WHATSAPP_PHONE_NUMBER_ID")
        self.verify_token = os.getenv("WHATSAPP_VERIFY_TOKEN")
        self.base_url = f"https://graph.facebook.com/v21.0/{self.phone_number_id}/messages"
        
        if not all([self.api_token, self.phone_number_id]):
            print("[ERROR] Faltan credenciales de WhatsApp API en .env")

    def send_message(self, to_number, message_text):
        """
        Envía un mensaje de texto a un número de WhatsApp.
        :param to_number: Número de teléfono con código de país (sin +). Ej: 5491122334455
        :param message_text: Texto del mensaje a enviar.
        """
        headers = {
            "Authorization": f"Bearer {self.api_token}",
            "Content-Type": "application/json"
        }
        
        # [SANDBOX FIX] Argentina: Meta a veces requiere quitar el 9 después del 54
        # Comentado para probar envío directo al ID recibido
        # if to_number.startswith("549") and len(to_number) > 10:
        #    clean_number = "54" + to_number[3:]
        #    print(f"[API] Ajustando número Argentina para Sandbox: {to_number} -> {clean_number}")
        #    to_number = clean_number

        payload = {
            "messaging_product": "whatsapp",
            "to": to_number,
            "type": "text",
            "text": {"body": message_text}
        }

        try:
            response = requests.post(self.base_url, headers=headers, json=payload)
            response.raise_for_status() # Lanza excepción si hay error HTTP
            print(f"[API] Mensaje enviado a {to_number}: {message_text[:20]}...")
            return True
        except requests.exceptions.HTTPError as err:
            print(f"[ERROR] HTTP Error enviando mensaje: {err}")
            print(f"Respuesta API: {response.text}")
            return False
        except Exception as e:
            print(f"[ERROR] Error general enviando mensaje: {e}")
            return False

if __name__ == "__main__":
    # Test rápido si se ejecuta directo
    client = WhatsAppAPIClient()
    # Pide número al usuario para testear
    test_number = input("Ingresa número destino para test (format 549...): ")
    if test_number:
        client.send_message(test_number, "Hola! Esto es una prueba desde el nuevo cliente API.")
