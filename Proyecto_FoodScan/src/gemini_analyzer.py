import google.generativeai as genai
from PIL import Image
import io
import os
import json  # ¡Importar el módulo json!
from config import GEMINI_API_KEY, GEMINI_MODEL_NAME  # Importa desde config




# Ya no se llama load_dotenv() ni genai.configure() aquí fuera de la clase
# porque ya se hace en config.py al importar.


class GeminiAnalyzer:
   def __init__(self):
       # La clave API y el modelo ya deberían estar configurados por config.py
       # Solo verificamos que la clave esté disponible (aunque config.py ya lo hace)
       if not GEMINI_API_KEY:
           raise ValueError("GEMINI_API_KEY no está configurado. Asegúrate de que config.py lo cargue correctamente.")

       # genai.configure(api_key=GEMINI_API_KEY) # Esto es redundante si ya se configuró en config.py
       self.model = genai.GenerativeModel(GEMINI_MODEL_NAME)
       print(f"Modelo Gemini '{GEMINI_MODEL_NAME}' inicializado en GeminiAnalyzer.")


   def analyze_image(self, image_path):
       """
       Analiza una imagen utilizando Gemini Vision Pro y extrae información de los alimentos.
       Intenta identificar alimentos y estimar su cantidad en gramos y sus nutrientes.
       Devuelve la respuesta en un formato estructurado (diccionario) listo para ser procesado.
       """
       try:
           # Abrir la imagen con PIL para asegurar el formato y manejar posibles errores
           pil_image = Image.open(image_path)


           # Convertir la imagen a bytes para enviarla a la API
           img_byte_arr = io.BytesIO()
           # Asegura que el formato es JPEG, ya que 'mime_type' se establece en 'image/jpeg'
           pil_image.save(img_byte_arr, format='JPEG')
           image_data = img_byte_arr.getvalue()


           image_part = {
               'mime_type': 'image/jpeg',  # Establecido explícitamente a JPEG
               'data': image_data
           }


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


           # Enviar el prompt y la imagen
           response = self.model.generate_content([prompt, image_part],
                                                  request_options={"timeout": 60})  # Aumentar timeout por si acaso
           response.resolve()  # Asegura que la respuesta esté completa


           response_text = response.text.strip()
           # Limpiar la respuesta de Gemini para asegurar que sea JSON puro
           # Buscar el inicio y fin del bloque JSON
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
               response_text = response_text[json_start: json_end + 1]


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
                   item.get("cantidad_estimada_g", 0))  # Default a 0 si no lo estima o es inválido
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
                   "nutrientes_estimados_por_100g_gemini": nutrientes_por_100g  # Guardamos la estimación de Gemini
               })


           return {"alimentos": processed_foods}


       except json.JSONDecodeError as e:
           print(f"❌ Error al parsear la respuesta JSON de Gemini: {e}")
           print(
               f"Respuesta cruda de Gemini (podría estar truncada o malformada):\n{response.text if 'response' in locals() else 'N/A'}")
           return {"alimentos": [], "resumen_general": "Error al procesar la respuesta de Gemini."}
       except Exception as e:
           print(f"❌ Error general al analizar la imagen con Gemini: {e}")
           return {"alimentos": [], "resumen_general": f"Error en el análisis: {e}"}




# Para probar rápidamente el analyzer en desarrollo
if __name__ == '__main__':
   # Este __main__ es solo para pruebas aisladas del analyzer.
   # Necesitarás tener un archivo .env en la raíz del proyecto para que funcione.
   # Y una imagen de prueba en images/input_images/


   # Asumiendo que config.py ya ha cargado las variables de entorno
   # y configurado genai.configure()


   # Si quieres probar este archivo de forma independiente, DEBES asegurarte
   # de que el .env se cargue aquí.
   from dotenv import load_dotenv


   project_root_test = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
   load_dotenv(dotenv_path=os.path.join(project_root_test, '.env'))


   # Reimportar las claves después de cargar dotenv en este scope
   from config import GEMINI_API_KEY, GEMINI_MODEL_NAME


   if not GEMINI_API_KEY:
       print("La clave GEMINI_API_KEY no está configurada. No se puede ejecutar la prueba.")
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




