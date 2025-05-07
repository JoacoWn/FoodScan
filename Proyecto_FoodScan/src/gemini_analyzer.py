import google.generativeai as genai
import os
import json
from PIL import Image
from config import GEMINI_API_KEY, GEMINI_MODEL_NAME

class GeminiAnalyzer:
    def __init__(self):
        if not GEMINI_API_KEY or GEMINI_API_KEY == "TU_API_KEY_GEMINI_AQUI":
            raise ValueError("Configura tu clave de API de Gemini en config.py")
        genai.configure(api_key=GEMINI_API_KEY)
        self.model = genai.GenerativeModel(GEMINI_MODEL_NAME)
        print("✅ GeminiAnalyzer inicializado correctamente.")

    def _generate_prompt(self):
        return (
            "Eres un nutricionista experto. Analiza esta imagen de comida y responde en formato JSON. "
            "Para cada alimento visible, entrega los siguientes datos nutricionales aproximados por porción:\n"
            "- 'alimento' (nombre)\n"
            "- 'calorias' (kcal)\n"
            "- 'proteinas' (g)\n"
            "- 'grasas' (g)\n"
            "- 'carbohidratos' (g)\n\n"
            "Ejemplo de salida:\n"
            "[{\"alimento\": \"Plátano\", \"calorias\": 89, \"proteinas\": 1.1, \"grasas\": 0.3, \"carbohidratos\": 22.8}]\n"
            "No entregues texto adicional, solo el array JSON como respuesta."
        )

    def analyze_image(self, image_path):
        if not os.path.exists(image_path):
            print(f"[ERROR] Imagen no encontrada: {image_path}")
            return []

        try:
            img = Image.open(image_path).convert("RGB")
            prompt = self._generate_prompt()
            response = self.model.generate_content([prompt, img])
            raw_text = response.text.strip()

            # Limpiar si viene con "```json"
            if raw_text.startswith("```json"):
                raw_text = raw_text.replace("```json", "").replace("```", "").strip()

            data = json.loads(raw_text)

            if not isinstance(data, list):
                print(f"[{os.path.basename(image_path)}] ⚠️ La respuesta no es una lista válida: {data}")
                return []

            alimentos = []
            for item in data:
                if isinstance(item, dict) and "alimento" in item:
                    alimentos.append({
                        "alimento": item.get("alimento", "desconocido"),
                        "calorias": float(item.get("calorias", 0)),
                        "proteinas": float(item.get("proteinas", 0)),
                        "grasas": float(item.get("grasas", 0)),
                        "carbohidratos": float(item.get("carbohidratos", 0))
                    })

            return alimentos

        except Exception as e:
            print(f"[{os.path.basename(image_path)}] ❌ Error al analizar con Gemini: {e}")
            return []
