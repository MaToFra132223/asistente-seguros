from playwright.sync_api import sync_playwright
import os
import time

import sys
import io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

def diagnose():
    user_data_dir = os.path.join(os.getcwd(), "whatsapp_session_v5")
    print(f"Usando directorio de sesión: {user_data_dir}")
    
    with sync_playwright() as p:
        browser = p.chromium.launch_persistent_context(
            user_data_dir,
            headless=False,
            args=["--start-maximized", "--disable-blink-features=AutomationControlled"]
        )
        
        page = browser.pages[0] if browser.pages else browser.new_page()
        page.goto("https://web.whatsapp.com")
        
        print("Esperando carga inicial...")
        # time.sleep(10) # Reemplazado por espera manual
        
        input("\n⚠️  POR FAVOR: Abre un chat en WhatsApp Web y LUEGO presiona ENTER aquí en la terminal...")
        
        print("\n--- Analisis de Chat Activo ---")
        # Click en el primer chat
        chat_rows = page.locator('div[role="row"]')
        print(f"Filas de chat encontradas: {chat_rows.count()}")
        
        # Buscar mensajes (incondicionalmente)
        msg_in = page.locator('div.message-in')
        count = msg_in.count()
        print(f"Mensajes 'message-in' encontrados: {count}")
        
        if count > 0:
            print("Analizando estructura del primer mensaje para encontrar el Panel Principal...")
            first_msg = msg_in.first
            # Subir niveles para encontrar el contenedor principal
            parent = first_msg.locator('xpath=..')
            
            print(f"Parent Class: {parent.get_attribute('class')}")
            
            # Analizar el ultimo mensaje para ver como extraer el texto
            last_msg = msg_in.last
            print("\n--- Analisis del Ultimo Mensaje ---")
            print(f"HTML del ultimo mensaje (primeros 500 chars):\n{last_msg.evaluate('el => el.innerHTML')[:500]}")
            
            # Probar selectores de texto
            text_sel = last_msg.locator('.selectable-text span, .copyable-text span')
            if text_sel.count() > 0:
                print(f"Texto detectado (con selector actual): '{text_sel.first.inner_text()}'")
            else:
                print("⚠️ NO se detectó texto con selectores usuales (.selectable-text, .copyable-text)")
        
        # Verificar caja de texto (Input)
        print("\n--- Analisis de Caja de Texto (Input) ---")
        input_box = page.locator('footer div[contenteditable="true"]')
        print(f"Caja de texto encontrada en footer: {input_box.count()}")
        if input_box.count() == 0:
                print("ALERTA: No se encuentra la caja de texto en el footer.")
                footer = page.locator('footer')
                if footer.count() > 0:
                    print(f"HTML del footer:\n{footer.evaluate('el => el.innerHTML')[:1000]}")
        
        # Verificar Badges de No Leidos
        print("\n--- Analisis de Badges (Sidebar) ---")
        print("Buscando filas de chat en el panel izquierdo (role='row')...")
        chat_rows = page.locator('div[role="row"]') # Ajustar si es necesario
        print(f"Filas encontradas: {chat_rows.count()}")
        
        if chat_rows.count() > 0:
            print("Dumpeando HTML de las primeras 3 filas para buscar diferencias (badges):")
            for i in range(min(3, chat_rows.count())):
                row_html = chat_rows.nth(i).evaluate('el => el.innerHTML')
                print(f"\n[Fila {i}] HTML parcial:\n{row_html[:1000]}")
                # Buscamos numeros o indicaciones de no leido
                if "aria-label" in row_html:
                    aria_labels = []
                    parts = row_html.split('aria-label=')
                    for part in parts[1:]: # Skip first part
                         # Extract content inside quotes
                         if '"' in part:
                             aria_labels.append(part.split('"')[1])
                         elif "'" in part:
                             aria_labels.append(part.split("'")[1])
                    print(f"   -> Aria-labels en fila {i}: {aria_labels}")

        # Buscamos cualquier span con aria-label que contenga "unread" o "no leído"
        badges = page.locator('span[aria-label*="unread"], span[aria-label*="no leido"], span[aria-label*="No leído"]')
        print(f"Badges encontrados con selector clásico: {badges.count()}")
        
        # Buscar por color verde (clase aproximada o estilo) es dificil, pero listemos aria-labels generales
        all_arias = page.locator('span[aria-label]').all()
        print("Listando primeros 10 aria-labels encontrados en la pagina:")
        for i, el in enumerate(all_arias[:10]):
                try:
                    print(f" - {el.get_attribute('aria-label')}")
                except: pass

        browser.close()

if __name__ == "__main__":
    diagnose()
