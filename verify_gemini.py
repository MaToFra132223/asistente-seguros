import os
import google.generativeai as genai
from dotenv import load_dotenv
import time

load_dotenv()

api_key = os.getenv("GEMINI_API_KEY")
if not api_key:
    print("ERROR: No se encontro la GEMINI_API_KEY")
    exit(1)

genai.configure(api_key=api_key)

# Lista ampliada de modelos a probar
candidates = [
    "models/gemini-1.5-flash",
    "models/gemini-1.5-flash-latest",
    "models/gemini-1.5-pro",
    "models/gemini-pro",
    "models/gemini-1.0-pro",
    "models/gemini-flash-latest"
]

available = [m.name for m in genai.list_models()]
print(f"Modelos disponibles en la cuenta: {len(available)}")

success = False

for model_name in candidates:
    # Verificar si el modelo existe en la lista (o intentar usarlo directamente si se sabe que existe pero no sale en la lista por alguna razon)
    # Algunos alias como gemini-pro a veces no salen en list_models pero funcionan.
    
    print(f"\nProbando modelo: {model_name}...")
    try:
        model = genai.GenerativeModel(model_name)
        response = model.generate_content("Responde 'OK'.")
        if response and response.text:
            print(f"EXITO: Funciono con {model_name}. Respuesta: {response.text.strip()}")
            success = True
            break
    except Exception as e:
        print(f"FALLO con {model_name}: {e}")
        # Si es un error de cuota (429), seguimos al siguiente.
        if "429" in str(e):
            print("  -> Limite de cuota o no disponible en free tier. Probando siguiente...")
        elif "404" in str(e):
             print("  -> Modelo no encontrado. Probando siguiente...")
        else:
             print("  -> Error desconocido. Probando siguiente...")

if success:
    exit(0)
else:
    print("\n❌ FALLARON TODOS LOS MODELOS.")
    exit(1)
