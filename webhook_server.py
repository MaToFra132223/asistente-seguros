from flask import Flask, request, jsonify
import os
import re
import sys
import io
from dotenv import load_dotenv
from ai_brain import AIBrain
from whatsapp_api_client import WhatsAppAPIClient
import configuracion as config

# Forzar UTF-8 en Windows para logs
if sys.stdout.encoding != 'utf-8':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

load_dotenv()

app = Flask(__name__)

# Config
VERIFY_TOKEN = os.getenv("WHATSAPP_VERIFY_TOKEN", "my_secure_verify_token")

# Initialize components
print("[INIT] Inicializando componentes...")
try:
    brain = AIBrain()
    print("[INIT] OK - Cerebro IA conectado.")
except Exception as e:
    print(f"[ERROR] CRITICO - Fallo al conectar IA: {e}")
    brain = None

client = WhatsAppAPIClient()

# Cache de mensajes procesados para evitar duplicados (WhatsApp a veces reintenta)
processed_messages = set()

@app.route("/", methods=["GET"])
def home():
    return "WhatsApp AI Bot Server is Running!"

@app.route("/webhook", methods=["GET"])
def verify_webhook():
    mode = request.args.get("hub.mode")
    token = request.args.get("hub.verify_token")
    challenge = request.args.get("hub.challenge")

    if mode and token:
        if mode == "subscribe" and token == VERIFY_TOKEN:
            print("[INFO] Webhook verificado correctamente!")
            return challenge, 200
        else:
            print("[ERROR] Falló la verificación del token.")
            return "Verification token mismatch", 403
    return "Hello world", 200

@app.route("/webhook", methods=["POST"])
def receive_message():
    try:
        body = request.get_json()
        
        # Verificar si es un evento de mensaje
        if body.get("object") == "whatsapp_business_account":
            for entry in body.get("entry", []):
                for change in entry.get("changes", []):
                    value = change.get("value", {})
                    
                    if "messages" in value:
                        for message in value["messages"]:
                            msg_id = message.get("id")
                            
                            # Evitar duplicados
                            if msg_id in processed_messages:
                                continue
                            processed_messages.add(msg_id)
                            
                            # Extraer datos
                            from_number = message["from"] # Ej: 5493406...
                            msg_type = message.get("type")
                            
                            if msg_type == "text":
                                msg_body = message["text"]["body"]
                                print(f"\n[MSG] Recibido de {from_number}: {msg_body}")
                                
                                # Procesar con IA
                                if brain:
                                    process_and_reply(from_number, msg_body)
                                else:
                                    print("[ERROR] IA no disponible, no se responde.")
                            else:
                                print(f"[INFO] Mensaje recibido tipo {msg_type}, ignorado por ahora.")
                    
                    elif "statuses" in value:
                        # Log de estados (enviado, entregado, leido)
                        for status in value["statuses"]:
                            print(f"[STATUS] Mensaje {status['status']} (ID: {status['id']})")
                                
            return jsonify({"status": "received"}), 200
        else:
            return "Not a WhatsApp API event", 404

    except Exception as e:
        print(f"[ERROR] Procesando webhook: {e}")
        return "Internal Server Error", 500

def process_and_reply(user_phone, user_message):
    try:
        # 1. Generar respuesta
        print(f"[IA] Generando respuesta para {user_phone}...")
        reply = brain.get_response(user_message, user_id=user_phone)
        print(f"[IA] Respuesta: {reply[:50]}...")
        
        # 2. Enviar respuesta
        client.send_message(user_phone, reply)
        
        # 3. Chequear lógica de Derivación (Human Handover)
        match = re.search(r"\[DERIVAR: (.*?)(?: \| (.*?))?\]", reply)
        if match:
            contacto_destino = match.group(1).strip()
            resumen = match.group(2)
            
            print(f"[DERIVACION] Detectada orden de envío a: {contacto_destino}")
            
            # En API Oficial, necesitamos el numero real del empleado en formato internacional
            # Asumimos que contacto_destino es un nombre, habría que mapearlo a numero.
            # Por ahora, enviamos AL MISMO NUMERO (o a un admin hardcodeado si tuviéramos)
            # para demostrar funcionalidad, o intentamos enviar al numero si parece numero.
            
            # TODO: Definir numero de admin/empleados en .env
            # Por simplicidad, avisamos en consola y al usuario
            client.send_message(user_phone, "Bot: (Simulacion) He derivado tu caso a un humano.")
            
    except Exception as e:
        print(f"[ERROR] Fallo en flujo de respuesta: {e}")

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    
    # Auto-start ngrok if strictly local
    if "RENDER" not in os.environ and "RAILWAY" not in os.environ:
        try:
            from pyngrok import ngrok
            # Set auth token if available in env, otherwise manual might be needed
            auth = os.getenv("NGROK_AUTH_TOKEN")
            if auth:
                ngrok.set_auth_token(auth)
            
            public_url = ngrok.connect(port).public_url
            print(f"\n[NGROK] Tunnel Online: {public_url}")
            print(f"[META] Copia esta URL y ponla en 'Callback URL' en el panel de Meta.")
            print(f"[META] Verify Token: {VERIFY_TOKEN}\n")
        except Exception as e:
            print(f"[WARN] No se pudo iniciar ngrok automaticamente: {e}")
            print("Ejecuta 'ngrok http 5000' en otra terminal manualmente.")

    # use_reloader=False para evitar doble inicializacion de la IA al guardar cambios
    app.run(host="0.0.0.0", port=port, debug=True, use_reloader=False)
