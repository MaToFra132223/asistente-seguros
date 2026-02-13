print("DEBUG: Starting main.py")
import os
import time
from dotenv import load_dotenv
print("DEBUG: Imported dotenv")
from whatsapp_client import WhatsAppClient
print("DEBUG: Imported WhatsAppClient")
from ai_brain import AIBrain
print("DEBUG: Imported AIBrain")

# Cargar configuración
load_dotenv()
print("DEBUG: Loaded dotenv")
# Forzar salida UTF-8 para Windows
import sys
import io
if sys.stdout.encoding != 'utf-8':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
print("DEBUG: Setup stdout (UTF-8 forced)")

HEADLESS = os.getenv("HEADLESS", "False").lower() == "true"
print(f"DEBUG: HEADLESS={HEADLESS}")


import datetime

def log(message):
    timestamp = datetime.datetime.now().strftime("%H:%M:%S")
    print(f"[{timestamp}] {message}", flush=True)

import configuracion as config

def main():
    log(f"[BOT] Iniciando Asistente de {config.NOMBRE_AGENCIA}...")
    
    # 1. Inicializar Cerebro IA
    brain = None
    try:
        brain = AIBrain()
        log("[OK] Cerebro IA conectado.")
    except Exception as e:
        log(f"[ERROR] Error critico conectando IA: {e}")
        return

    # 2. Inicializar Cliente WhatsApp
    client = WhatsAppClient(headless=HEADLESS)
    
    try:
        client.start()
        client.wait_for_login()
        
        log("\n[BOT] El bot esta activo. Presiona Ctrl+C para detenerlo.")
        
        # Bucle principal
        processed_messages = set()
        last_known_msg = None
        
        while True:
            try:
                # Heartbeat (sin log para no ensuciar, o solo cada X tiempo)
                print(".", end="", flush=True)
    
                # 1. Buscar mensajes no leídos (Esto cambia el chat activo si encuentra uno)
                badge_found = client.check_unread_messages()
                if badge_found:
                    # Esperar a que cargue el mensaje tras el click
                    time.sleep(1)
                    
                # 2. Leer estado actual del chat (haya badge o no)
                current_msg = client.get_last_incoming_message()
                
                # Solo obtenemos el TITULO de forma pasiva para el loop
                chat_title = client.get_active_chat_title()
                
                should_reply = False
                
                if current_msg:
                    # CASO A: Abrimos un chat porque tenía badge -> RESPONDER SI O SI
                    if badge_found:
                        log(f"[TRIGGER] Badge encontrado. Respondiendo a: {current_msg[:20]}...")
                        should_reply = True
                        
                    # CASO B: Estamos en un chat abierto y el mensaje CAMBIÓ -> RESPONDER
                    elif last_known_msg is not None and current_msg != last_known_msg:
                        log(f"[TRIGGER] Mensaje nuevo detectado en chat activo: {current_msg[:20]}...")
                        should_reply = True
                    
                    # Actualizar nuestro conocimiento del estado actual
                    last_known_msg = current_msg
                    
                    if should_reply:
                        log(f"Recopilando info de contacto de {chat_title}...")
                        chat_info = client.get_active_chat_info()
                        chat_title = chat_info["title"]
                        chat_phone = chat_info["phone"]
                        
                        log(f"Recibido de {chat_title} ({chat_phone}): {current_msg}")
                        
                        # 3. Procesar con IA
                        log(f"Generando respuesta para {chat_title}...")
                        start_ai = time.time()
                        reply = brain.get_response(current_msg, user_id=chat_title)
                        log(f"Respuesta generada en {time.time() - start_ai:.2f}s")
                        
                        # 4. Enviar respuesta al CLIENTE
                        client.send_message(reply)
                        
                        # 5. Chequear SEÑAL DE DERIVACIÓN
                        import re
                        match = re.search(r"\[DERIVAR: (.*?)(?: \| (.*?))?\]", reply)
                        if match:
                            contacto_destino = match.group(1).strip()
                            resumen = match.group(2) 
                            
                        # --- NUEVO: Lógica de enfriamiento (Cooldown) ---
                        # Evitar repetir la misma derivación al mismo contacto para el mismo cliente en 8 horas.
                        import datetime
                        
                        # Estructura: {(chat_title, contacto_destino): timestamp}
                        if not hasattr(main, "derivation_history"):
                            main.derivation_history = {}
                            
                        key = (chat_title, contacto_destino)
                        now = datetime.datetime.now()
                        cooldown_hours = 8
                        
                        should_send_derivation = True
                        
                        if key in main.derivation_history:
                            last_time = main.derivation_history[key]
                            if (now - last_time).total_seconds() < (cooldown_hours * 3600):
                                should_send_derivation = False
                                log(f"[DERIVACIÓN SKIP] Ya se derivó a {contacto_destino} para {chat_title} hace menos de {cooldown_hours}hs.")
                        
                        if should_send_derivation:
                            log(f"[DERIVACIÓN] Detectada orden de envío a: {contacto_destino} (Resumen: {resumen})")
                            
                            # Preparar mensaje para el empleado
                            base_msg = f"⚠️ *Nuevo Mensaje de Cliente*\n\n*Cliente:* {chat_title}\n*Tel:* {chat_phone}"
                            if resumen:
                                base_msg += f"\n*Asunto:* {resumen}"
                            base_msg += f"\n*Dice:* {current_msg}"
                            
                            mensaje_interno = base_msg
                            
                            # Ejecutar reenvío
                            exito = client.search_chat_and_send(contacto_destino, mensaje_interno)
                            
                            if exito:
                                # Actualizar historial
                                main.derivation_history[key] = now
                                log(f"[DERIVACIÓN] Mensaje reenviado exitosamente a {contacto_destino}")
                                log(f"[BOT] Volviendo al chat del cliente: {chat_title}...")
                                client.open_chat(chat_title)
                                pass 
    
                        # Esperar un momento para asegurar envío
                        time.sleep(2)
                
                time.sleep(1)

            except KeyboardInterrupt:
                raise # Re-raise para salir del loop principal
            except Exception as e:
                 log(f"[ERROR LOOP] Error recuperable en bucle principal: {e}")
                 time.sleep(2) # Esperar un poco antes de reintentar
            
    except KeyboardInterrupt:
        log("\nDeteniendo el bot...")
    except Exception as e:
        try:
            log(f"\n[ERROR] Error en el proceso principal: {str(e).encode('utf-8', errors='replace').decode('utf-8')}")
        except:
             print(f"\n[ERROR] Error en el proceso principal (unicode error)")
    finally:
        log("Cerrando recursos...")
        client.close()

if __name__ == "__main__":
    main()
