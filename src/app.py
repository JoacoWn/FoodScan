import os
from flask import Flask, request, jsonify
from flask_cors import CORS
from datetime import datetime, date  # Importa 'date' también para mayor claridad
import uuid
import json  # Importado para pretty-print en debug logs
import tempfile
from werkzeug.utils import secure_filename

# Importar las clases y funciones de tus módulos existentes
# Asegúrate de que estas rutas de importación sean correctas para tu estructura 'src'
from src.gemini_analyzer import GeminiAnalyzer
from src.data_logger import DataLogger
from src.image_manager import ImageManager
from src.food_utils import get_food_data_from_db  # Esto busca en tu FOOD_DATABASE local
from src.config import FOOD_SECTIONS  # Esto debería contener las secciones de comida (ej. ["Desayuno", "Almuerzo"])

app = Flask(__name__)
CORS(app)  # Habilita CORS para permitir solicitudes desde tu app Android

# --- Configuración de directorios de imágenes temporales ---
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg'}

# Inicializa los módulos
gemini_analyzer = GeminiAnalyzer()
data_logger = DataLogger()
image_manager = ImageManager()  # ImageManager se encargará de crear sus directorios


# --- FUNCIÓN allowed_file CORREGIDA: Ubicada correctamente ---
def allowed_file(filename):
    """Verifica si la extensión del archivo está permitida."""
    return '.' in filename and \
        filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


# --- ENDPOINTS DE LA API ---

@app.route('/analizar', methods=['POST'])
def analizar_imagen_comida():
    """
    Endpoint para recibir una imagen, analizarla con Gemini, procesar la información
    nutricional (usando la BD local si aplica), registrarla en MongoDB y devolver un resumen.
    """
    if 'image' not in request.files:
        print("❌ Error: No se encontró la parte 'image' en la solicitud.")
        return jsonify({"error": "No se encontró el archivo de imagen en la solicitud."}), 400

    image_file = request.files['image']
    if image_file.filename == '':
        print("❌ Error: No se seleccionó ninguna imagen.")
        return jsonify({"error": "No se seleccionó ninguna imagen."}), 400

    if not allowed_file(image_file.filename):
        print(f"❌ Error: Tipo de archivo no permitido: {image_file.filename}")
        return jsonify({"error": "Tipo de archivo no permitido."}), 400

    original_filename = secure_filename(image_file.filename)
    file_extension = os.path.splitext(original_filename)[1]
    unique_filename = f"{uuid.uuid4()}{file_extension}"

    # Guardar imagen en la carpeta de procesamiento temporal para GeminiAnalyzer
    temp_image_path = os.path.join(image_manager.processing_dir, unique_filename)
    try:
        image_file.save(temp_image_path)
        print(f"🖼️ Imagen guardada temporalmente en: {temp_image_path}")
    except Exception as e:
        print(f"❌ Error al guardar la imagen recibida: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({"error": "Error al guardar la imagen recibida."}), 500

    meal_type = request.form.get('meal_type', FOOD_SECTIONS[0])
    if meal_type not in FOOD_SECTIONS:
        meal_type = FOOD_SECTIONS[0]  # Valor por defecto si no es válido

    print(f"🔎 Iniciando análisis de la imagen {unique_filename} con Gemini...")
    # Llama a GeminiAnalyzer, que ahora devuelve la estructura JSON completa
    gemini_raw_analysis = gemini_analyzer.analyze_image(temp_image_path)

    # --- INICIO DE LOS PRINTS DE DEPURACIÓN EN APP.PY (Puedes quitarlos después de verificar) ---
    print(f"\n--- DEBUG APP.PY: ESTADO DESPUÉS DE LA LLAMADA A GEMINI ---")
    print(f"DEBUG: Tipo de 'gemini_raw_analysis': {type(gemini_raw_analysis)}")

    if isinstance(gemini_raw_analysis, dict):
        print(f"DEBUG: 'gemini_raw_analysis' completo (JSON.DUMPS):\n{json.dumps(gemini_raw_analysis, indent=2)}")
        print(
            f"DEBUG: 'nombre_general_comida' (extraído con .get()): {gemini_raw_analysis.get('nombre_general_comida', 'NO_ENCONTRADO_DEFAULT_APP')}")
        print(
            f"DEBUG: 'alimentos_detallados' (extraído con .get()): {gemini_raw_analysis.get('alimentos_detallados', 'NO_ENCONTRADO_DEFAULT_APP')}")
        print(
            f"DEBUG: Longitud de 'alimentos_detallados' (extraída): {len(gemini_raw_analysis.get('alimentos_detallados', []))}")
    else:
        print(f"DEBUG: 'gemini_raw_analysis' no es un diccionario, contenido: {gemini_raw_analysis}")
    print(f"---------------------------------------------------\n")
    # --- FIN DE LOS PRINTS DE DEPURACIÓN EN APP.PY ---

    # --- Manejo de la respuesta de Gemini ---
    if not gemini_raw_analysis or gemini_raw_analysis.get("error"):
        error_msg = gemini_raw_analysis.get("error", "Análisis de Gemini falló o no devolvió resultados válidos.")
        image_manager.move_to_error(unique_filename)
        # Eliminar el archivo temporal del directorio de procesamiento después de moverlo a error
        if os.path.exists(temp_image_path):
            os.remove(temp_image_path)
        print(f"❌ Análisis fallido, moviendo a error y limpiando {temp_image_path}")
        return jsonify({
            "error": "No se pudieron identificar alimentos en la imagen o el análisis de Gemini falló.",
            "details": error_msg
        }), 400

    # Extraer los datos principales de la respuesta de Gemini
    nombre_general_comida = gemini_raw_analysis.get("nombre_general_comida", "Plato sin nombre")
    alimentos_detallados_gemini = gemini_raw_analysis.get("alimentos_detallados", [])

    # --- INICIO DE OTROS PRINTS DE DEPURACIÓN CRÍTICA ANTES DEL BUCLE (Puedes quitarlos después de verificar) ---
    print(f"\n--- DEBUG APP.PY: ANTES DEL BUCLE DE PROCESAMIENTO DE ALIMENTOS ---")
    print(f"DEBUG: Variable 'alimentos_detallados_gemini' que se usará en el bucle: {alimentos_detallados_gemini}")
    print(f"DEBUG: Longitud final de 'alimentos_detallados_gemini' para el bucle: {len(alimentos_detallados_gemini)}")
    print(f"-------------------------------------------------------------------\n")
    # --- FIN DE OTROS PRINTS DE DEPURACIÓN CRÍTICA ---

    # Inicializar totales generales, los acumularemos en el bucle
    total_calorias = 0.0
    total_proteinas = 0.0
    total_grasas = 0.0
    total_carbohidratos = 0.0

    # Lista de alimentos con nutrientes finalizados para la base de datos y la respuesta de la app
    final_processed_foods_for_db = []
    response_foods_for_app = []  # Para la respuesta de la app, solo con nutrientes finales

    for item_gemini in alimentos_detallados_gemini:
        # --- PRINT DENTRO DEL BUCLE (Puedes quitarlos después de verificar) ---
        print(f"DEBUG: Procesando item_gemini dentro del bucle: {item_gemini}")
        # --- FIN PRINT DENTRO DEL BUCLE ---

        # *************************************************************************
        # CAMBIOS CLAVE AQUÍ: Ajuste de claves a la estructura REAL de gemini_analyzer
        # *************************************************************************
        nombre_alimento_gemini = item_gemini.get("nombre_alimento", "Desconocido").strip()

        try:
            # Ahora la clave es 'cantidad_estimada_g' y puede ser float, la convertimos a int
            cantidad_g_gemini = int(item_gemini.get("cantidad_estimada_g", 0.0))
        except ValueError:
            cantidad_g_gemini = 0
            print(
                f"⚠️ Cantidad_g para '{nombre_alimento_gemini}' no es un número válido o no se encontró 'cantidad_estimada_g', se usará 0.")

        # Los nutrientes están anidados bajo la clave 'nutrientes_estimados'
        nutrientes_estimados_dict = item_gemini.get("nutrientes_estimados", {})

        nutrientes_gemini_para_cantidad = {
            "calorias": float(nutrientes_estimados_dict.get("calorias", 0.0)),
            "proteinas": float(nutrientes_estimados_dict.get("proteinas", 0.0)),
            "grasas": float(nutrientes_estimados_dict.get("grasas", 0.0)),
            "carbohidratos": float(nutrientes_estimados_dict.get("carbohidratos", 0.0))
        }
        es_estimado_ia_original = item_gemini.get("es_estimado", True)
        # *************************************************************************
        # FIN CAMBIOS CLAVE
        # *************************************************************************

        # Buscar el alimento en tu base de datos local
        matched_food_data = get_food_data_from_db(nombre_alimento_gemini)

        nutrientes_finales_por_item = {}
        nombre_final_alimento = nombre_alimento_gemini
        usado_bd_local = False
        es_estimado_final = True  # Por defecto es estimado, a menos que usemos la BD local

        if matched_food_data and cantidad_g_gemini > 0:
            # Si se encuentra en la DB local, usa sus valores por 100g y escala a la cantidad_g_gemini
            factor = cantidad_g_gemini / 100.0
            nutrientes_finales_por_item["calorias"] = round(matched_food_data.get("calorias_por_100g", 0.0) * factor, 2)
            nutrientes_finales_por_item["proteinas"] = round(matched_food_data.get("proteinas_por_100g", 0.0) * factor,
                                                             2)
            nutrientes_finales_por_item["grasas"] = round(matched_food_data.get("grasas_por_100g", 0.0) * factor, 2)
            nutrientes_finales_por_item["carbohidratos"] = round(
                matched_food_data.get("carbohidratos_por_100g", 0.0) * factor, 2)

            nombre_final_alimento = matched_food_data.get("nombre", nombre_alimento_gemini).title()
            usado_bd_local = True
            es_estimado_final = False  # Ya no es estimado si usamos nuestra BD
            print(
                f"✅ Alimento '{nombre_alimento_gemini}' (Gemini) → '{nombre_final_alimento}' (BD Local) - Calculado para {cantidad_g_gemini}g.")
        else:
            # Si no se encuentra en la DB local, usa directamente las estimaciones de Gemini
            nutrientes_finales_por_item = {
                "calorias": round(nutrientes_gemini_para_cantidad.get("calorias", 0.0), 2),
                "proteinas": round(nutrientes_gemini_para_cantidad.get("proteinas", 0.0), 2),
                "grasas": round(nutrientes_gemini_para_cantidad.get("grasas", 0.0), 2),
                "carbohidratos": round(nutrientes_gemini_para_cantidad.get("carbohidratos", 0.0), 2)
            }
            nombre_final_alimento = nombre_alimento_gemini.title() + " (Estimado por IA)"  # Etiqueta para identificar
            usado_bd_local = False
            es_estimado_final = True
            print(
                f"⚠️ Alimento '{nombre_alimento_gemini}' no encontrado en la BD local. Usando estimaciones de Gemini para {cantidad_g_gemini}g.")

        # Acumular los totales generales del plato
        total_calorias += nutrientes_finales_por_item["calorias"]
        total_proteinas += nutrientes_finales_por_item["proteinas"]
        total_grasas += nutrientes_finales_por_item["grasas"]
        total_carbohidratos += nutrientes_finales_por_item["carbohidratos"]

        # Formato para guardar en la base de datos (DataLogger)
        final_processed_foods_for_db.append({
            "nombre_alimento": nombre_final_alimento,
            "cantidad_g": cantidad_g_gemini,
            "nutrientes": nutrientes_finales_por_item,  # Nutrientes para esa cantidad
            "es_estimado_ia_original": es_estimado_ia_original,  # Si Gemini lo marcó como estimado
            "usado_bd_local_para_calculo": usado_bd_local  # Indica si se usó la BD local para el cálculo
        })

        # Formato para la respuesta a la aplicación móvil (lo que espera ResultActivity)
        response_foods_for_app.append({
            "nombre": nombre_final_alimento,
            "cantidad_g": cantidad_g_gemini,
            "calorias": nutrientes_finales_por_item["calorias"],
            "proteinas": nutrientes_finales_por_item["proteinas"],
            "grasas": nutrientes_finales_por_item["grasas"],
            "carbohidratos": nutrientes_finales_por_item["carbohidratos"],
            "es_estimado": es_estimado_final  # Si el cálculo final es estimado o de BD
        })

    # Redondear totales generales del plato
    total_calorias = round(total_calorias, 2)
    total_proteinas = round(total_proteinas, 2)
    total_grasas = round(total_grasas, 2)
    total_carbohidratos = round(total_carbohidratos, 2)

    # Preparar el objeto final para guardar en la base de datos (DataLogger)
    full_meal_data_for_db = {
        "nombre_general_comida": nombre_general_comida,  # Nombre general del plato de Gemini
        "calorias_totales": total_calorias,
        "proteinas_totales": total_proteinas,
        "grasas_totales": total_grasas,
        "carbohidratos_totales": total_carbohidratos,
        "alimentos_detallados": final_processed_foods_for_db
    }

    # Llama a DataLogger para registrar la entrada completa
    log_success = data_logger.log_food_entry(
        analysis_result=full_meal_data_for_db,
        image_name=unique_filename,
        meal_type=meal_type,
        log_time=datetime.now()  # Guarda el timestamp actual
    )

    if not log_success:
        print("❌ Falló el registro en MongoDB.")
        image_manager.move_to_error(unique_filename)
        # Eliminar el archivo temporal del directorio de procesamiento
        if os.path.exists(temp_image_path):
            os.remove(temp_image_path)
        return jsonify({"error": "Error al registrar la entrada en la base de datos."}), 500

    # Mover la imagen a la carpeta de procesados después de un éxito total
    image_manager.move_to_processed(unique_filename)
    # Eliminar el archivo temporal del directorio de procesamiento
    if os.path.exists(temp_image_path):
        os.remove(temp_image_path)
    print(f"✅ Análisis completado y entrada registrada para {unique_filename}.")

    # --- Construyendo la respuesta final para la aplicación móvil (ResultActivity) ---
    response_data = {
        "nombre": nombre_general_comida,
        "calorias": total_calorias,
        "proteinas": total_proteinas,
        "grasas": total_grasas,
        "carbohidratos": total_carbohidratos,
        "alimentos_detallados": response_foods_for_app
    }
    return jsonify(response_data), 200


@app.route('/historial', methods=['GET'])
def get_food_history_endpoint():
    """
    Endpoint para obtener el historial de todas las comidas registradas.
    Convierte ObjectId y datetime a string para ser serializable en JSON.
    """
    try:
        entries = data_logger.get_food_entries()

        serialized_entries = []
        for entry in entries:
            serialized_entry = entry.copy()

            # Convertir ObjectId a string
            if '_id' in serialized_entry:
                serialized_entry['_id'] = str(serialized_entry['_id'])

            # Convertir datetime a ISO 8601 string
            # Esto generará 'YYYY-MM-DDTHH:MM:SS.ffffff' (microsegundos, sin 'Z' si es naive)
            if 'timestamp' in serialized_entry and isinstance(serialized_entry['timestamp'], datetime):
                serialized_entry['timestamp'] = serialized_entry['timestamp'].isoformat()

            # Asegurar que los campos numéricos sean floats
            for key in ["calorias_totales", "proteinas_totales", "grasas_totales", "carbohidratos_totales"]:
                if key in serialized_entry and not isinstance(serialized_entry[key], (float, int)):
                    try:
                        serialized_entry[key] = float(serialized_entry[key])
                    except (ValueError, TypeError):
                        serialized_entry[key] = 0.0

            if "alimentos_detallados" in serialized_entry:
                for food_item in serialized_entry["alimentos_detallados"]:
                    if "nutrientes" in food_item:
                        for nutrient_key in ["calorias", "proteinas", "grasas", "carbohidratos"]:
                            if nutrient_key in food_item["nutrientes"] and not isinstance(
                                    food_item["nutrientes"][nutrient_key], (float, int)):
                                try:
                                    food_item["nutrientes"][nutrient_key] = float(food_item["nutrientes"][nutrient_key])
                                except (ValueError, TypeError):
                                    food_item["nutrientes"][nutrient_key] = 0.0

            serialized_entries.append(serialized_entry)

        return jsonify(serialized_entries), 200
    except Exception as e:
        print(f"❌ Error al obtener el historial de comidas: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({"error": "Error interno del servidor al obtener historial."}), 500


@app.route('/historial_por_fecha', methods=['GET'])
def get_food_history_by_date_endpoint():
    """
    Endpoint para obtener el historial de comidas registradas para una fecha específica.
    Recibe la fecha como parámetro de query en formato 'YYYY-MM-DD'.
    """
    date_str = request.args.get('date')  # Obtener la fecha del query parameter
    if not date_str:
        return jsonify({"error": "Parámetro 'date' es requerido en formato YYYY-MM-DD."}), 400

    try:
        # Intentar parsear la fecha del string a un objeto datetime
        start_of_day = datetime.strptime(date_str, "%Y-%m-%d")
        end_of_day = start_of_day.replace(hour=23, minute=59, second=59, microsecond=999999)

        # *** ¡IMPORTANTE! ***
        # Para que este endpoint sea eficiente para grandes volúmenes de datos,
        # tu método `get_food_entries` en `src/data_logger.py` debería ser modificado
        # para aceptar parámetros `start_date` y `end_date` y filtrar directamente en MongoDB.
        # Por ejemplo, en data_logger.py:
        # def get_food_entries(start_date=None, end_date=None):
        #     query = {}
        #     if start_date and end_date:
        #         query["timestamp"] = {"$gte": start_date, "$lte": end_of_day}
        #     return list(self.collection.find(query).sort("timestamp", 1)) # Opcional: ordenar por timestamp
        #
        # Si no modificas `data_logger.py`, esta función seguirá obteniendo *todo* el historial
        # y filtrando en Python, lo cual es menos eficiente pero funcionará.
        # *** FIN IMPORTANTE ***

        # Obtener todas las entradas y luego filtrar por fecha en Python
        # (Idealmente, get_food_entries filtraría esto directamente de la DB)
        all_entries = data_logger.get_food_entries()
        entries_for_date = []
        for entry in all_entries:
            if 'timestamp' in entry and isinstance(entry['timestamp'], datetime):
                # Compara si el timestamp de la entrada está dentro del rango del día
                if start_of_day <= entry['timestamp'] <= end_of_day:
                    entries_for_date.append(entry)

        serialized_entries = []
        for entry in entries_for_date:
            serialized_entry = entry.copy()

            if '_id' in serialized_entry:
                serialized_entry['_id'] = str(serialized_entry['_id'])

            if 'timestamp' in serialized_entry and isinstance(serialized_entry['timestamp'], datetime):
                serialized_entry['timestamp'] = serialized_entry['timestamp'].isoformat()

            # Asegurar que los campos numéricos sean floats
            for key in ["calorias_totales", "proteinas_totales", "grasas_totales", "carbohidratos_totales"]:
                if key in serialized_entry and not isinstance(serialized_entry[key], (float, int)):
                    try:
                        serialized_entry[key] = float(serialized_entry[key])
                    except (ValueError, TypeError):
                        serialized_entry[key] = 0.0

            if "alimentos_detallados" in serialized_entry:
                for food_item in serialized_entry["alimentos_detallados"]:
                    if "nutrientes" in food_item:
                        for nutrient_key in ["calorias", "proteinas", "grasas", "carbohidratos"]:
                            if nutrient_key in food_item["nutrientes"] and not isinstance(
                                    food_item["nutrientes"][nutrient_key], (float, int)):
                                try:
                                    food_item["nutrientes"][nutrient_key] = float(food_item["nutrientes"][nutrient_key])
                                except (ValueError, TypeError):
                                    food_item["nutrientes"][nutrient_key] = 0.0

            serialized_entries.append(serialized_entry)

        # Opcional: Ordenar las entradas por timestamp antes de enviarlas
        # Collections.sort(serialized_entries, key=lambda x: x.get('timestamp', '')) # Esto asume que timestamp es comparable
        # Mejor ordenarlo por el objeto datetime real si se modifica get_food_entries para devolverlos así
        # O si ya están ordenados por la consulta a MongoDB.

        return jsonify(serialized_entries), 200

    except ValueError:
        return jsonify({"error": "Formato de fecha inválido. Use YYYY-MM-DD."}), 400
    except Exception as e:
        print(f"❌ Error al obtener el historial por fecha: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({"error": "Error interno del servidor al obtener historial por fecha."}), 500


@app.route('/saludo', methods=['GET'])
def saludo():
    """Endpoint simple para verificar que la API está funcionando."""
    return jsonify({"mensaje": "¡Hola desde FoodScan Backend! La API está funcionando."}), 200


if __name__ == '__main__':
    print("🚀 Iniciando servidor Flask. Accede a http://127.0.0.1:5000/saludo para probar.")
    app.run(host='0.0.0.0', port=5000, debug=True)