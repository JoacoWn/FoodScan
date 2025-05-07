import google.generativeai as genai
import os
import json
from PIL import Image
from src.config import GEMINI_API_KEY, GEMINI_MODEL_NAME, CONFIDENCE_THRESHOLD_VIOLATION, CONFIDENCE_THRESHOLD_PLATE

class GeminiAnalyzer:
    def __init__(self):
        if not GEMINI_API_KEY or GEMINI_API_KEY == "TU_API_KEY_DE_GEMINI":
            raise ValueError("La clave de API de Gemini no está configurada. Por favor, edita src/config.py.")
        genai.configure(api_key=GEMINI_API_KEY)
        self.model = genai.GenerativeModel(GEMINI_MODEL_NAME)
        print("DEBUG (GeminiAnalyzer): Cliente Gemini inicializado con éxito.")

    def _generate_prompt(self):
        """Genera el prompt para la detección de infracciones, incluyendo color y marca."""
        # Definimos el prompt como una lista de líneas para evitar problemas con las triple comillas
        prompt_lines = [
            "Eres un asistente experto en normas de tránsito chilenas, especializado en la detección de estacionamiento ilegal en entornos urbanos como Temuco.",
            "Tu tarea es analizar la siguiente imagen e identificar **todos los vehículos que estén cometiendo una infracción de estacionamiento** de acuerdo a la legislación chilena.",
            "Considera las siguientes infracciones comunes:",
            "- Estacionar en doble fila.",
            "- Estacionar sobre la acera (vereda) o cualquier área peatonal.",
            "- Estacionar en pasos de peatones (pasos de cebra) o cruces peatonales.",
            "- Estacionar en ciclovías o áreas destinadas exclusivamente para bicicletas.",
            "- Estacionar en zonas de no estacionar (señalizadas con letreros o demarcación amarilla en el bordillo).",
            "- Bloquear entradas de garaje, rampas de acceso para personas con movilidad reducida o grifos.",
            "- Estacionar a menos de 5 metros de una esquina o de un paradero de transporte público.",
            "- Estacionar en zonas de carga y descarga fuera del horario permitido o sin autorización.",
            "- Estacionar obstruyendo el tránsito (por ejemplo, en un carril de circulación).",
            "",
            "Para cada vehículo infractor que identifiques, proporciona la siguiente información:",
            "- **\"infraccion_detectada\"**: `true` (siempre que se detecte una infracción).",
            "- **\"tipo_infraccion\"**: Una descripción concisa del tipo de infracción (ej. \"Doble fila\", \"Sobre acera\", \"Paso peatones\", \"Bloqueando entrada de garaje\", \"Zona no estacionar\").",
            "Si hay múltiples razones, elige la más grave o evidente.",
            "- **\"patente\"**: La patente (placa) del vehículo en formato CHILENO (ej. 'ABCD-12', 'ABCD-123', 'AABB-11').",
            "Si la patente no es claramente legible o no está visible, usa `null`.",
            "- **\"color_vehiculo\"**: El color predominante del vehículo (ej. \"rojo\", \"azul\", \"gris\", \"negro\", \"blanco\", \"amarillo\", \"verde\", \"café\", \"plateado\").",
            "Si no es discernible, usa `null`.",
            "- **\"marca_vehiculo\"**: La marca del vehículo (ej. \"Toyota\", \"Ford\", \"BMW\", \"Hyundai\", \"Chevrolet\", \"Kia\", \"Mercedes-Benz\", \"Volkswagen\").",
            "Si no es discernible o no estás seguro, usa `null`.",
            "- **\"confianza_infraccion\"**: Un valor `float` (0.0-1.0) que represente la confianza en la detección de la infracción (1.0 = muy seguro).",
            "- **\"confianza_patente\"**: Un valor `float` (0.0-1.0) que represente la confianza en la legibilidad de la patente (1.0 = muy seguro).",
            "Si \"patente\" es `null`, este valor debe ser `0.0`.",
            "",
            "**Formato de respuesta:** Debes responder con un array JSON.",
            "Cada objeto en el array representa un vehículo infractor detectado.",
            "Si no se detecta **ninguna infracción** de estacionamiento, devuelve un array JSON vacío: `[]`.",
            "```json",
            "[",
            "  {",
            "    \"infraccion_detectada\": true,",
            "    \"tipo_infraccion\": \"Sobre acera\",",
            "    \"patente\": \"HJ-GH-98\",",
            "    \"color_vehiculo\": \"gris\",",
            "    \"marca_vehiculo\": \"Nissan\",",
            "    \"confianza_infraccion\": 0.95,",
            "    \"confianza_patente\": 0.88",
            "  },",
            "  {",
            "    \"infraccion_detectada\": true,",
            "    \"tipo_infraccion\": \"Doble fila\",",
            "    \"patente\": null,",
            "    \"color_vehiculo\": \"blanco\",",
            "    \"marca_vehiculo\": null,",
            "    \"confianza_infraccion\": 0.82,",
            "    \"confianza_patente\": 0.0",
            "  }",
            "]",
            "```",
            "Asegúrate de que la salida sea **únicamente el array JSON**, sin texto adicional."
        ]
        return "\n".join(prompt_lines)

    def analyze_image(self, image_path):
        """
        Analiza una imagen usando la API de Gemini para detectar infracciones de estacionamiento,
        incluyendo color y marca del vehículo. Retorna una lista de diccionarios con los resultados de la detección.
        """
        if not os.path.exists(image_path):
            print(f"ERROR (GeminiAnalyzer): La imagen no existe en la ruta especificada: {image_path}")
            return []

        try:
            img = Image.open(image_path).convert('RGB')
            prompt = self._generate_prompt()
            try:
                response = self.model.generate_content([prompt, img])
                text_response = response.text.strip()
            except Exception as e:
                print(f"ERROR (GeminiAnalyzer): Fallo en la llamada a generate_content de Gemini para {os.path.basename(image_path)}: {e}")
                return []

            try:
                # Modificación para manejar mejor las respuestas que incluyen 'json' o '```json'
                if text_response.startswith("```json"):
                    text_response = text_response.replace("```json", "").replace("```", "").strip()
                elif text_response.startswith("json"): # Considerar si solo empieza con 'json'
                    text_response = text_response[len("json"):].strip()
                elif text_response.endswith("```"): # Asegurar que se remuevan los ``` finales
                    text_response = text_response.replace("```", "").strip()


                data = json.loads(text_response)

                if not isinstance(data, list):
                    print(f"[{os.path.basename(image_path)}] ERROR: Respuesta inesperada del modelo (no es una lista): {data}")
                    return []

                processed_results = []
                for item in data:
                    if isinstance(item, dict) and item.get("infraccion_detectada", False):
                        confianza_infraccion = item.get("confianza_infraccion", 0.0)
                        if confianza_infraccion >= CONFIDENCE_THRESHOLD_VIOLATION:
                            processed_results.append({
                                "infraccion_detectada": True,
                                "tipo_infraccion": item.get("tipo_infraccion", "desconocido"),
                                "patente": item.get("patente", "no_visible"),
                                "color_vehiculo": item.get("color_vehiculo", "desconocido"),
                                "marca_vehiculo": item.get("marca_vehiculo", "desconocida"),
                                "confianza_infraccion": float(confianza_infraccion),
                                "confianza_patente": float(item.get("confianza_patente", 0.0))
                            })
                        else:
                            print(f"[{os.path.basename(image_path)}] INFO: Infracción detectada pero con confianza ({confianza_infraccion:.2f}) bajo el umbral ({CONFIDENCE_THRESHOLD_VIOLATION}).")
                    else:
                        print(f"[{os.path.basename(image_path)}] INFO: Elemento no válido en la respuesta del modelo o no es infracción: {item}")
                return processed_results

            except json.JSONDecodeError as json_error:
                print(f"[{os.path.basename(image_path)}] ERROR: No se pudo parsear la respuesta JSON de Gemini: {json_error}")
                print(f"Respuesta cruda de Gemini: {text_response}")
                return []
            except Exception as parse_e:
                print(f"[{os.path.basename(image_path)}] ERROR: Error inesperado al procesar la respuesta de Gemini: {parse_e}")
                print(f"Respuesta cruda de Gemini: {text_response}")
                return []
        except Exception as e:
            print(f"ERROR (GeminiAnalyzer): Error general al analizar la imagen {image_path}: {e}")
            return []