from playwright.sync_api import sync_playwright
import time
import os
import re

class WhatsAppClient:
    DEFAULT_TIMEOUT = 5000 # 5 segundos para evitar congelamientos

    def __init__(self, headless=False):
        self.headless = headless
        self.playwright = None
        self.browser = None
        self.page = None
        self.user_data_dir = os.path.join(os.getcwd(), "whatsapp_session_v5")

    def start(self):
        """Inicia el navegador y carga WhatsApp Web"""
        print(f"Iniciando WhatsApp Client (Headless: {self.headless})...")
        self.playwright = sync_playwright().start()
        
        if not os.path.exists(self.user_data_dir):
            os.makedirs(self.user_data_dir)
            
        self.browser = self.playwright.chromium.launch_persistent_context(
            self.user_data_dir,
            headless=self.headless,
            args=["--start-maximized", "--disable-blink-features=AutomationControlled"]
        )
        
        self.page = self.browser.pages[0] if self.browser.pages else self.browser.new_page()
        self.page.set_default_timeout(self.DEFAULT_TIMEOUT) # Timeout por defecto para todo
        
        try:
            self.page.goto("https://web.whatsapp.com", timeout=60000) # Carga inicial puede tardar más
            print("Cargando WhatsApp Web...")
        except Exception as e:
            print(f"Error cargando pagina (timeout?): {e}")
        
    def wait_for_login(self):
        """Espera a que el usuario escanee el QR"""
        print("Esperando inicio de sesion...")
        try:
            # Esperar a que aparezca la lista de chats o el buscador
            # Usamos un timeout largo aqui porque depende del usuario
            self.page.wait_for_selector('div[contenteditable="true"][data-tab="3"]', timeout=300000) # 5 min max
            print("[OK] Sesion iniciada correctamente!")
        except Exception as e:
            print(f"Error esperando login (o ya logueado?): {e}")

    def check_unread_messages(self):
        """Busca chats con mensajes no leídos"""
        try:
            # Buscar badges verdes o con digitos
            # Selector optimizado para encontrar burbujas de notificacion
            # Agregamos 'no leído' en minuscula y plurales
            unread_badges = self.page.locator('span[aria-label*="unread"], span[aria-label*="no leido"], span[aria-label*="No leído"], span[aria-label*="no leído"], span[aria-label*="mensajes no leídos"]')
            
            if unread_badges.count() == 0:
                # Fallback: Buscar iconos verdes genéricos
                # A veces es un div con color verde, difícil de dar con selector exacto sin clase
                # print("[DEBUG] No unread badges found (primary selector)")
                pass

            count = unread_badges.count()
            # print(f"[DEBUG] Badges found: {count}") 
            if count > 0:
                print(f"[INFO] Se encontraron {count} chats con mensajes sin leer.")
                
                # ESTRATEGIA MAS ROBUSTA:
                # En lugar de buscar badges y luego padres, buscamos FILAS que contengan badges.
                # Definimos el selector de badges de nuevo para usarlo en el filtro
                badge_selector = 'span[aria-label*="unread"], span[aria-label*="no leido"], span[aria-label*="No leído"], span[aria-label*="no leído"], span[aria-label*="mensajes no leídos"]'
                
                # Buscamos todas las filas que tengan un badge dentro
                rows_with_unread = self.page.locator('div[role="row"]').filter(has=self.page.locator(badge_selector))
                
                if rows_with_unread.count() > 0:
                    print("Clickeando fila del chat con mensaje nuevo...")
                    # Clickeamos la primera fila encontrada
                    rows_with_unread.first.click(timeout=2000, force=True)
                    
                    if self.wait_for_chat_to_load():
                         return True
                    else:
                         print("[WARN] Se clickeó fila pero no detectamos chat abierto.")
                         return False
                else:
                    print("[WARN] Se detectaron badges pero no filas contenedoras (extraño). Intentando click directo en badge...")
                    try:
                        badge = unread_badges.first
                        badge.click(timeout=2000, force=True)
                    except: pass
                    return self.wait_for_chat_to_load()
            
            return False
        except Exception as e:
            return False

    def wait_for_chat_to_load(self, timeout=5000):
        """Espera a que un chat se abra correctamente (buscando panel main o header)"""
        try:
             # Buscamos #main o un elemento clave del chat activo
             self.page.wait_for_selector('#main', timeout=timeout)
             return True
        except:
             return False

    def get_last_incoming_message(self):
        """Lee el último mensaje recibido del chat abierto"""
        try:
            # 1. Identificar el Panel Principal
            main_panel = self.page.locator('#main')
            if main_panel.count() == 0:
                return None # No hay chat abierto

            # 2. Buscar mensajes
            # Intentamos buscar burbujas de mensaje entrante (message-in)
            messages = main_panel.locator('div.message-in')
            
            # Si no hay 'message-in', buscamos filas genéricas de mensajes
            if messages.count() == 0:
                # Buscamos todos los 'role="row"' dentro del main panel que NO sean salientes
                # message-out suele tener clases distintas.
                # Esta es una heurística: buscar divs con texto
                all_rows = main_panel.locator('div[role="row"]')
                if all_rows.count() > 0:
                    messages = all_rows
            
            count = messages.count()
            if count > 0:
                # Tomar el último
                last_msg = messages.nth(count - 1)
                
                # Extraer texto de .selectable-text o .copyable-text
                text_elem = last_msg.locator('.selectable-text span, .copyable-text span').first
                if text_elem.count() > 0:
                    text = text_elem.inner_text()
                    # print(f"[DEBUG] Last msg text (span): {text[:20]}...")
                    return text
                
                # Fallback: todo el texto del row
                text = last_msg.inner_text()
                # print(f"[DEBUG] Last msg text (full row): {text[:20]}...")
                return text
            
            # print("[DEBUG] No messages found in main panel")
            return None
            
        except Exception as e:
            print(f"Error leyendo mensaje: {e}")
            return None

    def open_chat(self, contact_name):
        """Busca y abre un chat por nombre, SIN enviar mensaje"""
        try:
            print(f"[BOT] Abriendo chat con: {contact_name}...")
            
            # 1. Buscar caja de busqueda (Panel Izq)
            search_box = self.page.locator('div[contenteditable="true"][data-tab="3"]')
            if search_box.count() == 0:
                 # Fallback
                 search_box = self.page.locator('div[id="side"] div[contenteditable="true"]')
            
            search_box.click(timeout=self.DEFAULT_TIMEOUT)
            # Limpiar y escribir
            search_box.fill(contact_name)
            time.sleep(1.0) # Esperar resultados
            search_box.press("Enter")
            
            # Esperar a que cargue el main panel
            try:
                self.page.wait_for_selector('#main', timeout=self.DEFAULT_TIMEOUT)
                return True
            except:
                print(f"[WARN] No se detectó apertura del chat '#main' para {contact_name}")
                return False
                
        except Exception as e:
            print(f"[ERROR] Fallo al abrir chat {contact_name}: {e}")
            return False

    def send_message(self, text):
        """Envía un mensaje al chat YA abierto"""
        try:
            # Footer / Caja de texto (data-tab=10 es comun para input de msg)
            box = self.page.locator('footer div[contenteditable="true"][data-tab="10"]')
            
            if box.count() == 0:
                # Fallback generico
                box = self.page.locator('#main footer div[contenteditable="true"]')
            
            box.click(timeout=self.DEFAULT_TIMEOUT)
            box.fill(text)
            time.sleep(0.5)
            box.press("Enter")
            print(f"[BOT] > {text}")
            return True
        except Exception as e:
            print(f"Error enviando mensaje: {e}")
            return False

    def get_active_chat_title(self):
        """Obtiene el título del chat abierto"""
        try:
            # Estrategia 1: Header principal -> Span con Title
            header_title = self.page.locator('#main header span[title]').first
            if header_title.count() > 0:
                return header_title.inner_text()
            
            # Estrategia 2: Header -> Div clickable -> span (común en perfiles de empresa)
            header_clickable = self.page.locator('#main header div[role="button"]').first
            if header_clickable.count() > 0:
                 # Buscar cualquier texto visible grande dentro
                 spans = header_clickable.locator('span[dir="auto"]')
                 if spans.count() > 0:
                     return spans.first.inner_text()

            # Estrategia 3: Buscar cualquier texto en el header que parezca un nombre
            # (Excluyendo "en línea", "escribiendo...", etc)
            header_text = self.page.locator('#main header').inner_text()
            lines = header_text.split('\n')
            if lines:
                return lines[0] # La primera línea suele ser el nombre

        except Exception as e:
            print(f"[WARN] Error leyendo titulo chat: {e}")
        return "Desconocido"

    def get_active_chat_info(self):
        """Devuelve info extra (telefono) si es posible"""
        info = {"title": self.get_active_chat_title(), "phone": "Desconocido"}
        # Logica simplificada para no complicar el fix
        # Si el titulo ya es numero, usarlo
        if re.search(r'\+\d', info["title"]):
            info["phone"] = info["title"]
        return info

    def search_chat_and_send(self, contact_name, message):
        """Wrapper de compatibilidad: abre y envía"""
        if self.open_chat(contact_name):
            return self.send_message(message)
        return False

    def close(self):
        if self.browser:
            self.browser.close()
        if self.playwright:
            self.playwright.stop()
