import os
import io
import json
import base64  # Necesario para codificar la imagen en base64
import requests # Nueva librería para hacer peticiones HTTP

from PIL import Image # Ya lo tenías
# Importamos las nuevas variables de configuración
from config import OPENROUTER_API_KEY, OPENROUTER_URL, GEMINI_MODEL_NAME


class GeminiAnalyzer:
    def __init__(self):
        # Ya no necesitamos genai.configure() aquí ni self.model como objeto genai
        # Solo verificamos que la clave esté disponible
        if not OPENROUTER_API_KEY:
            raise ValueError("OPENROUTER_API_KEY no está configurado. Asegúrate de que config.py lo cargue correctamente.")

        print(f"Configurando para OpenRouter con modelo '{GEMINI_MODEL_NAME}' en URL '{OPENROUTER_URL}'.")


    def analyze_image(self, image_path):
        """
        Analiza una imagen utilizando la API de OpenRouter (para Gemini) y extrae información de los alimentos.
        Intenta identificar alimentos y estimar su cantidad en gramos y sus nutrientes.
        Devuelve la respuesta en un formato estructurado (diccionario) listo para ser procesado.
        """
        try:
            # Abrir la imagen con PIL
            pil_image = Image.open(image_path)

            # Convertir la imagen a bytes y luego a Base64 para enviarla en el JSON
            img_byte_arr = io.BytesIO()
            pil_image.save(img_byte_arr, format='JPEG') # Asegura formato JPEG para la API
            image_data = img_byte_arr.getvalue()
            base64_image = base64.b64encode(image_data).decode('utf-8')

            # URL de la imagen en formato Base64 (para la API compatible con OpenAI)
            image_url_data = f"data:image/jpeg;base64,{base64_image}"

            # Hemos ajustado el prompt para que la respuesta sea directamente el JSON.
            # Instrucciones claras para el formato de salida JSON.
            prompt = (
                "Analiza esta imagen y desglosa los alimentos que contiene. Para cada alimento identificado, "
                "proporciona su nombre en español, una estimación de su cantidad en gramos (número entero), "
                "y una estimación de sus valores nutricionales (calorías, proteínas, grasas, carbohidratos) "
                "por la cantidad estimada. No incluyas ningún texto adicional, solo el objeto JSON."
                "Devuelve la respuesta en formato JSON, con una lista de objetos, donde cada objeto representa un alimento. "
                "Ejemplo de formato JSON:\n"
                "```json\n"
                "[\n"
                "  {\n"
                "    \"nombre\": \"Arroz blanco cocido\",\n"
                "    \"cantidad_estimada_g\": 200,\n"
                "    \"nutrientes_estimados\": {\n"
                "      \"calorias\": 260,\n"
                "      \"proteinas\": 5.4,\n"
                "      \"grasas\": 0.6,\n"
                "      \"carbohidratos\": 56.4\n"
                "    }\n"
                "  },\n"
                "  {\n"
                "    \"nombre\": \"Pechuga de pollo cocida\",\n"
                "    \"cantidad_estimada_g\": 150,\n"
                "    \"nutrientes_estimados\": {\n"
                "      \"calorias\": 247.5,\n"
                "      \"proteinas\": 46.5,\n"
                "      \"grasas\": 5.4,\n"
                "      \"carbohidratos\": 0.0\n"
                "    }\n"
                "  }\n"
                "]\n"
                "```"
            )

            # Encabezados para la petición a OpenRouter
            headers = {
                "Authorization": f"Bearer {OPENROUTER_API_KEY}",
                "Content-Type": "application/json",
            }

            # Construir el payload (cuerpo de la petición) en formato OpenAI-compatible
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
                "temperature": 0.7, # Puedes ajustar la creatividad (0.0 a 1.0)
                "max_tokens": 4000 # Un límite razonable para la respuesta
            }

            # Enviar la petición a la API de OpenRouter
            response = requests.post(OPENROUTER_URL, headers=headers, json=payload, timeout=90) # Aumentar timeout
            response.raise_for_status() # Lanza una excepción para errores HTTP (4xx o 5xx)

            response_json = response.json()
            # Extraer el contenido del mensaje del modelo
            response_text = response_json['choices'][0]['message']['content'].strip()


            # Limpiar la respuesta de Gemini para asegurar que sea JSON puro
            json_start = response_text.find('[')
            json_end = response_text.rfind(']')

            if json_start == -1 or json_end == -1:
                # Si no encontramos los corchetes, podría ser un JSON de objeto o texto plano.
                # Intentamos eliminar prefijos/sufijos comunes de bloques de código.
                if response_text.startswith("```json"):
                    response_text = response_text[len("```json"):].strip()
                if response_text.endswith("```"):
                    response_text = response_text[:-len("```")].strip()
            else:
                # Si encontramos corchetes, asumimos que el JSON está entre ellos
                response_text = response_text[json_start : json_end + 1]


            gemini_foods = json.loads(response_text)


            if not isinstance(gemini_foods, list):
                # Si Gemini devuelve un objeto único en lugar de una lista, conviértelo
                if isinstance(gemini_foods, dict):
                    gemini_foods = [gemini_foods]
                else:
                    raise ValueError("La respuesta JSON no es una lista ni un objeto de alimento.")


            # Procesamiento básico para asegurar el formato y la disponibilidad de datos
            processed_foods = []
            for item in gemini_foods:
                nombre = item.get("nombre", "Desconocido").strip()
                cantidad_estimada_g = float(
                    item.get("cantidad_estimada_g", 0))
                nutrientes_estimados = item.get("nutrientes_estimados", {})


                # Calcula nutrientes por 100g si se proporciona una cantidad estimada total
                nutrientes_por_100g = {
                    "calorias": round((nutrientes_estimados.get("calorias", 0) / (
                                cantidad_estimada_g / 100)) if cantidad_estimada_g > 0 else 0, 2),
                    "proteinas": round((nutrientes_estimados.get("proteinas", 0) / (
                                cantidad_estimada_g / 100)) if cantidad_estimada_g > 0 else 0, 2),
                    "grasas": round((nutrientes_estimados.get("grasas", 0) / (
                                cantidad_estimada_g / 100)) if cantidad_estimada_g > 0 else 0, 2),
                    "carbohidratos": round((nutrientes_estimados.get("carbohidratos", 0) / (
                                cantidad_estimada_g / 100)) if cantidad_estimada_g > 0 else 0, 2)
                }


                processed_foods.append({
                    "nombre_alimento": nombre,
                    "cantidad_estimada_g": cantidad_estimada_g,
                    "nutrientes_estimados_por_100g_gemini": nutrientes_por_100g
                })


            return {"alimentos": processed_foods}

        except requests.exceptions.RequestException as e:
            print(f"❌ Error de red o HTTP al comunicarse con OpenRouter: {e}")
            return {"alimentos": [], "resumen_general": f"Error de conexión con la API: {e}"}
        except json.JSONDecodeError as e:
            print(f"❌ Error al parsear la respuesta JSON de OpenRouter/Gemini: {e}")
            print(f"Respuesta cruda de la API (podría estar truncada o malformada):\n{response_text if 'response_text' in locals() else response.text if 'response' in locals() else 'N/A'}")
            return {"alimentos": [], "resumen_general": "Error al procesar la respuesta de la API."}
        except Exception as e:
            print(f"❌ Error general al analizar la imagen: {e}")
            return {"alimentos": [], "resumen_general": f"Error en el análisis: {e}"}


# Para probar rápidamente el analyzer en desarrollo
if __name__ == '__main__':
    # Asegurarse de que el .env se cargue para pruebas aisladas
    from dotenv import load_dotenv

    project_root_test = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    load_dotenv(dotenv_path=os.path.join(project_root_test, '.env'))

    # Reimportar las claves después de cargar dotenv en este scope
    # Ahora importamos las variables de OpenRouter
    from config import OPENROUTER_API_KEY, OPENROUTER_URL, GEMINI_MODEL_NAME


    if not OPENROUTER_API_KEY:
        print("La clave OPENROUTER_API_KEY no está configurada. No se puede ejecutar la prueba.")
    else:
        analyzer = GeminiAnalyzer()
        # Asegúrate de que la ruta de la imagen de prueba sea correcta
        test_image_path = os.path.join(project_root_test, 'images', 'input_images', 'plato_arroz.jpg')


        if os.path.exists(test_image_path):
            print(f"Analizando imagen de prueba: {test_image_path}")
            analysis_result = analyzer.analyze_image(test_image_path)


            if analysis_result and analysis_result.get("alimentos"):
                print("\n--- Resultado del Análisis de Gemini (solo identificación y estimación) ---")
                for item in analysis_result["alimentos"]:
                    print(f"Alimento: {item['nombre_alimento']}")
                    print(f"  Cantidad Estimada: {item['cantidad_estimada_g']}g")
                    print(
                        f"  Nutrientes Estimados (por 100g de Gemini): {item['nutrientes_estimados_por_100g_gemini']}")
            else:
                print("No se pudieron identificar alimentos en la imagen de prueba o hubo un error.")
                print(analysis_result.get("resumen_general", "Error desconocido."))
        else:
            print(f"No se encontró la imagen de prueba en: {test_image_path}")
            print("Asegúrate de que la ruta de la imagen de prueba sea correcta y la imagen exista.")

