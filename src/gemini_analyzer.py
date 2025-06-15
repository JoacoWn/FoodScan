import os
import io
import json
import base64
import requests
import re  # <-- Add this import for more robust JSON parsing

from PIL import Image
from src.config import OPENROUTER_API_KEY, OPENROUTER_URL, GEMINI_MODEL_NAME


class GeminiAnalyzer:
    def __init__(self):
        if not OPENROUTER_API_KEY:
            raise ValueError(
                "OPENROUTER_API_KEY no está configurado. Asegúrate de que config.py lo cargue correctamente.")

        print(f"Configurando para OpenRouter con modelo '{GEMINI_MODEL_NAME}' en URL '{OPENROUTER_URL}'.")

    def analyze_image(self, image_path):
        """
        Analiza una imagen utilizando la API de OpenRouter (para Gemini) y extrae información de los alimentos.
        Intenta identificar alimentos, estimar su cantidad en gramos y sus nutrientes.
        Devuelve la respuesta en un formato estructurado (diccionario) listo para ser procesado.
        """
        try:
            pil_image = Image.open(image_path)
            img_byte_arr = io.BytesIO()
            pil_image.save(img_byte_arr, format='JPEG')  # Guardar como JPEG para consistencia
            image_data = img_byte_arr.getvalue()
            base64_image = base64.b64encode(image_data).decode('utf-8')

            image_url_data = f"data:image/jpeg;base64,{base64_image}"

            # --- PROMPT MEJORADO SIGNIFICATIVAMENTE ---
            prompt = (
                "Eres un experto en nutrición y reconocimiento de alimentos. Tu tarea es analizar detalladamente la imagen de comida proporcionada. "
                "**Debes identificar el nombre típico o general del plato si es un conjunto (ej. 'Chorrillana', 'Ensalada César', 'Tazón de Avena').** "
                "Si no es un plato combinado, usa el nombre del único alimento (ej. 'Manzana Roja'). "
                "Luego, **desglosa el plato en CADA UNO DE SUS INGREDIENTES INDIVIDUALES PRINCIPALES Y ESPECÍFICOS** visibles."
                "Para CADA ingrediente individual identificado (ej. 'carne de res', 'papas fritas', 'cebolla acaramelizada', 'huevo frito' para una chorrillana): "
                "1. Proporciona su 'nombre' (lo más específico posible, en español, ej. 'Filete de Res', 'Papas Fritas Caseras')."
                "2. Estima su 'cantidad_g' (peso aproximado en gramos, número entero). "
                "3. Estima sus valores nutricionales: 'calorias', 'proteinas' (g), 'grasas' (g), y 'carbohidratos' (g) **para esa 'cantidad_g' estimada**."
                "4. Indica con un booleano 'es_estimado' (true/false) si estas estimaciones son aproximadas basadas en la IA."
                "Finalmente, calcula y proporciona también las 'calorias_totales', 'proteinas_totales', 'grasas_totales', y 'carbohidratos_totales' del **plato completo** (sumatoria de todos los ingredientes)."

                "La respuesta debe ser EXCLUSIVAMENTE un objeto JSON válido, sin ningún texto adicional antes o después, y debe seguir esta estructura EXACTA:"
                "\n```json\n"  # <-- Importante pedir el formato en un bloque de código JSON
                "{\n"
                "  \"nombre_general_comida\": \"Nombre típico del plato (ej. Chorrillana Clásica, Desayuno con Huevos y Tocino)\",\n"
                "  \"calorias_totales\": float,\n"
                "  \"proteinas_totales\": float,\n"
                "  \"grasas_totales\": float,\n"
                "  \"carbohidratos_totales\": float,\n"
                "  \"alimentos_detallados\": [\n"
                "    {\n"
                "      \"nombre\": \"nombre del ingrediente (ej. Carne de res, Papas fritas)\",\n"
                "      \"cantidad_g\": int,\n"
                "      \"calorias\": float,\n"
                "      \"proteinas\": float,\n"
                "      \"grasas\": float,\n"
                "      \"carbohidratos\": float,\n"
                "      \"es_estimado\": boolean\n"
                "    }\n"
                "  ]\n"
                "}\n"
                "```\n"
                "Si la imagen no contiene alimentos claros o el plato no puede ser desglosado de forma significativa, devuelve el JSON con 'alimentos_detallados' vacío y los totales en 0, y 'nombre_general_comida' como 'No se pudo identificar un plato claro'."
                "Asegúrate de que la salida sea SOLO el objeto JSON y nada más. Si puedes, proporciona los valores nutricionales con hasta 2 decimales."
            )

            headers = {
                "Authorization": f"Bearer {OPENROUTER_API_KEY}",
                "Content-Type": "application/json",
            }

            payload = {
                "model": GEMINI_MODEL_NAME,
                "messages": [
                    {
                        "role": "user",
                        "content": [
                            {"type": "text", "text": prompt},
                            {"type": "image_url", "image_url": {"url": image_url_data}},
                        ],
                    }
                ],
                "temperature": 0.3,  # Baja la temperatura para respuestas más concisas y menos creativas
                "max_tokens": 4000  # Suficientes tokens para un desglose detallado
            }

            response = requests.post(OPENROUTER_URL, headers=headers, json=payload, timeout=90)
            response.raise_for_status()  # Lanza un error para códigos de estado HTTP 4xx/5xx

            response_json = response.json()
            response_text = response_json['choices'][0]['message']['content'].strip()

            print(f"Respuesta cruda de OpenRouter/Gemini:\n{response_text}")  # Para depuración

            # --- MEJORA EN EL PARSEO DEL JSON ---
            # Busca el bloque JSON dentro de ```json ... ``` o intenta parsear directamente
            match = re.search(r"```json\n(\{.*\})\n```", response_text, re.DOTALL)
            if match:
                json_content = match.group(1)
            else:
                # Si no está en un bloque de código, asume que la respuesta directa es el JSON
                json_content = response_text

            gemini_result = json.loads(json_content)

            # --- VALIDACIÓN DE LA ESTRUCTURA ESPERADA ---
            # Asegura que el resultado sea un diccionario y contenga la clave esperada
            if not isinstance(gemini_result, dict) or "alimentos_detallados" not in gemini_result:
                raise ValueError(
                    "La respuesta JSON de Gemini no tiene la estructura esperada: debe ser un objeto con 'alimentos_detallados'.")

            # Preparamos los alimentos detallados para el formato final
            processed_foods = []
            for item in gemini_result.get("alimentos_detallados", []):
                processed_foods.append({
                    "nombre_alimento": item.get("nombre", "Desconocido").strip(),
                    "cantidad_estimada_g": float(item.get("cantidad_g", 0)),
                    # Aquí ya usamos los valores nutricionales 'tal cual' de Gemini,
                    # ya que el prompt le pidió que fueran por la 'cantidad_g' estimada.
                    "nutrientes_estimados": {
                        "calorias": round(item.get("calorias", 0.0), 2),
                        "proteinas": round(item.get("proteinas", 0.0), 2),
                        "grasas": round(item.get("grasas", 0.0), 2),
                        "carbohidratos": round(item.get("carbohidratos", 0.0), 2)
                    },
                    "es_estimado": item.get("es_estimado", True)  # Asumir True si no está presente
                })

            # Preparamos el diccionario final que será devuelto a app.py
            # Las claves de nivel superior se toman directamente del resultado de Gemini
            final_result = {
                "nombre_general_comida": gemini_result.get("nombre_general_comida", "Plato sin nombre").strip(),
                "calorias_totales": round(gemini_result.get("calorias_totales", 0.0), 2),
                "proteinas_totales": round(gemini_result.get("proteinas_totales", 0.0), 2),
                "grasas_totales": round(gemini_result.get("grasas_totales", 0.0), 2),
                "carbohidratos_totales": round(gemini_result.get("carbohidratos_totales", 0.0), 2),
                "alimentos_detallados": processed_foods,  # Ya procesados
                "error": None  # No hay error si llegamos hasta aquí
            }

            return final_result

        except requests.exceptions.RequestException as e:
            print(f"❌ Error de red o HTTP al comunicarse con OpenRouter: {e}")
            return {"nombre_general_comida": "Error de conexión", "calorias_totales": 0, "proteinas_totales": 0,
                    "grasas_totales": 0, "carbohidratos_totales": 0, "alimentos_detallados": [],
                    "error": f"Error de conexión con la API: {e}"}
        except json.JSONDecodeError as e:
            print(f"❌ Error al parsear la respuesta JSON de OpenRouter/Gemini: {e}")
            print(
                f"Respuesta cruda de la API (podría estar truncada o malformada):\n{response_text if 'response_text' in locals() else 'N/A'}")
            return {"nombre_general_comida": "Error de formato de IA", "calorias_totales": 0, "proteinas_totales": 0,
                    "grasas_totales": 0, "carbohidratos_totales": 0, "alimentos_detallados": [],
                    "error": f"Error al procesar la respuesta de la API: {e}"}
        except ValueError as e:
            print(f"❌ Error de validación en la respuesta de Gemini: {e}")
            return {"nombre_general_comida": "Error de validación", "calorias_totales": 0, "proteinas_totales": 0,
                    "grasas_totales": 0, "carbohidratos_totales": 0, "alimentos_detallados": [],
                    "error": f"Error de validación de datos: {e}"}
        except Exception as e:
            print(f"❌ Error general al analizar la imagen: {e}")
            import traceback
            traceback.print_exc()  # Esto imprimirá el stack trace completo del error
            return {"nombre_general_comida": "Error desconocido", "calorias_totales": 0, "proteinas_totales": 0,
                    "grasas_totales": 0, "carbohidratos_totales": 0, "alimentos_detallados": [],
                    "error": f"Error inesperado en el análisis: {e}"}
