import os
import google.generativeai as genai
from dotenv import load_dotenv
import configuracion as config

load_dotenv()

class AIBrain:
    def __init__(self):
        self.api_key = os.getenv("GEMINI_API_KEY")
        # Usamos el modelo que verificamos que funciona
        self.model_name = "models/gemini-flash-latest" 
        
        # Cargar Prompt base desde Configuración
        self.system_prompt = os.getenv("SYSTEM_PROMPT", config.SYSTEM_PROMPT_BASE)
        
        # Inyectar Procedimientos Estandar en el Prompt
        procedures_text = "\n\n### PROCEDIMIENTOS ESTANDAR (Usa esta informacion estrictamente cuando sea relevante):\n"
        for title, content in config.STANDARD_PROCEDURES.items():
            procedures_text += f"\n**{title}**:\n{content}\n"
            
        self.system_prompt += procedures_text
        
        # Diccionario para mantener sesiones activas por usuario: { 'user_id': chat_session }
        self.sessions = {}
        
        if not self.api_key:
            raise ValueError("GEMINI_API_KEY no encontrada en .env")
            
        genai.configure(api_key=self.api_key)
        
        # Configuración del modelo
        self.model = genai.GenerativeModel(
            model_name=self.model_name,
            system_instruction=self.system_prompt
        )

    def _get_or_create_session(self, user_id):
        """Recupera la sesión existente o crea una nueva si no existe"""
        if user_id not in self.sessions:
            print(f"[IA] Creando nueva sesión de memoria para: {user_id}")
            # Iniciamos chat vacío. La memoria se gestiona automáticamente por el objeto ChatSession de Gemini
            self.sessions[user_id] = self.model.start_chat(history=[])
        return self.sessions[user_id]

    def get_response(self, user_message, user_id="default"):
        """
        Genera una respuesta de Gemini con reintentos en caso de error de cuota (429).
        Inyecta la hora actual para decidir si mostrar contactos.
        """
        import datetime
        
        # Obtener fecha y hora actual
        now = datetime.datetime.now()
        dia_semana = now.strftime("%A") # Monday, Tuesday...
        hora_actual = now.strftime("%H:%M")
        
        # Traducir día
        dias = {"Monday": "Lunes", "Tuesday": "Martes", "Wednesday": "Miércoles", "Thursday": "Jueves", "Friday": "Viernes", "Saturday": "Sábado", "Sunday": "Domingo"}
        dia_es = dias.get(dia_semana, dia_semana)
        
        # Inyectar contexto temporal y derivaciones desde Configuración
        prompt_adicional = config.INSTRUCCIONES_DERIVACION
        
        contexto_temporal = f"\n[CONTEXTO TEMPORAL: HOY es {dia_es}, HORA: {hora_actual}. MIRA LA REGLA DE HORARIO EN LA AGENDA.]\n{prompt_adicional}\n"
        full_message = contexto_temporal + user_message

        max_retries = 3
        retry_delay = 5 

        for attempt in range(max_retries):
            try:
                # Obtener sesión específica del usuario
                chat = self._get_or_create_session(user_id)
                
                response = chat.send_message(full_message)
                return response.text
            except Exception as e:
                error_str = str(e)
                print(f"Error generando respuesta de IA (Intento {attempt+1}/{max_retries}): {error_str}", flush=True)
                
                # Chequeo basico de error de cuota
                if "429" in error_str or "Quota" in error_str:
                    if attempt < max_retries - 1:
                        wait_time = retry_delay * (attempt + 1)
                        print(f"[IA] Cuota excedida. Esperando {wait_time}s para reintentar...", flush=True)
                        import time
                        time.sleep(wait_time)
                        continue
                
                # Si no es error de cuota o ya gastamos los reintentos
                if attempt == max_retries - 1:
                    return config.MENSAJE_SATURACION
