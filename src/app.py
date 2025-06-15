import os
from flask import Flask, request, jsonify
from flask_cors import CORS
from datetime import datetime
import uuid
import json  # Necesario para pretty-print si usas prints de debug con JSON
import tempfile  # Para crear archivos temporales
from werkzeug.utils import secure_filename  # Para el manejo seguro de nombres de archivo

# Importar las clases y funciones de tus módulos existentes
# Asegúrate de que estas rutas sean correctas para tu estructura 'src'
from src.gemini_analyzer import GeminiAnalyzer
from src.data_logger import DataLogger
from src.image_manager import ImageManager
from src.food_utils import get_food_data_from_db  # Esto busca en tu FOOD_DATABASE local
from src.config import FOOD_SECTIONS  # Esto debería contener las secciones de comida (ej. ["Desayuno", "Almuerzo"])

app = Flask(__name__)
CORS(app)  # Habilita CORS para permitir solicitudes desde tu app Android

# --- Configuración de directorios de imágenes temporales ---
UPLOAD_FOLDER = os.path.join(tempfile.gettempdir(), 'foodscan_uploads')
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg'}

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
os.makedirs(UPLOAD_FOLDER, exist_ok=True)  # Asegura que la carpeta de subida exista

# Inicializa los módulos
gemini_analyzer = GeminiAnalyzer()
data_logger = DataLogger()
image_manager = ImageManager()  # Si usas ImageManager para mover archivos temporales


def allowed_file(filename):
    return '.' in filename and \
        filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


@app.route('/analizar', methods=['POST'])
def analizar_imagen_comida():
    """
    Endpoint para recibir una imagen, analizarla con Gemini, procesar la información
    nutricional (usando la BD local si aplica), registrarla en MongoDB y devolver un resumen.
    """
    if 'image' not in request.files:
        return jsonify({"error": "No se encontró el archivo de imagen en la solicitud."}), 400

    image_file = request.files['image']
    if image_file.filename == '':
        return jsonify({"error": "No se seleccionó ninguna imagen."}), 400

    if not allowed_file(image_file.filename):
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
        return jsonify({"error": "Error al guardar la imagen recibida."}), 500

    meal_type = request.form.get('meal_type', FOOD_SECTIONS[0])  # Asegura que FOOD_SECTIONS es una lista en config.py
    if meal_type not in FOOD_SECTIONS:
        meal_type = FOOD_SECTIONS[0]  # Valor por defecto si no es válido

    print(f"🔎 Iniciando análisis de la imagen {unique_filename} con Gemini...")
    # Llama a GeminiAnalyzer, que ahora devuelve la estructura JSON completa
    gemini_raw_analysis = gemini_analyzer.analyze_image(temp_image_path)

    # --- Manejo de la respuesta de Gemini ---
    if not gemini_raw_analysis or gemini_raw_analysis.get("error"):
        error_msg = gemini_raw_analysis.get("error", "Análisis de Gemini falló o no devolvió resultados válidos.")
        image_manager.move_to_error(unique_filename)
        os.remove(temp_image_path)  # Limpiar archivo temporal
        print(f"❌ Análisis fallido, limpiando {temp_image_path}")
        return jsonify({
            "error": "No se pudieron identificar alimentos en la imagen o el análisis de Gemini falló.",
            "details": error_msg
        }), 400

    # Extraer los datos principales de la respuesta de Gemini
    nombre_general_comida = gemini_raw_analysis.get("nombre_general_comida", "Plato sin nombre")
    alimentos_detallados_gemini = gemini_raw_analysis.get("alimentos_detallados", [])

    # Inicializar totales generales, los acumularemos en el bucle
    total_calorias = 0.0
    total_proteinas = 0.0
    total_grasas = 0.0
    total_carbohidratos = 0.0

    # Lista de alimentos con nutrientes finalizados para la base de datos y la respuesta de la app
    final_processed_foods_for_db = []
    response_foods_for_app = []

    for item_gemini in alimentos_detallados_gemini:
        nombre_alimento_gemini = item_gemini.get("nombre", "Desconocido").strip()
        cantidad_g_gemini = int(item_gemini.get("cantidad_g", 0))  # Asegura que sea int para la cantidad

        # Nutrientes estimados por Gemini para la cantidad_g_gemini
        nutrientes_gemini_para_cantidad = {
            "calorias": float(item_gemini.get("calorias", 0.0)),
            "proteinas": float(item_gemini.get("proteinas", 0.0)),
            "grasas": float(item_gemini.get("grasas", 0.0)),
            "carbohidratos": float(item_gemini.get("carbohidratos", 0.0))
        }
        es_estimado_ia_original = item_gemini.get("es_estimado", True)  # Si Gemini lo marcó como estimado

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
        log_time=datetime.now()
    )

    if not log_success:
        print("❌ Falló el registro en MongoDB.")
        image_manager.move_to_error(unique_filename)
        os.remove(temp_image_path)  # Limpiar archivo temporal incluso si falla DB
        return jsonify({"error": "Error al registrar la entrada en la base de datos."}), 500

    # Mover la imagen a la carpeta de procesados después de un éxito total
    image_manager.move_to_processed(unique_filename)
    os.remove(temp_image_path)  # Limpiar archivo temporal
    print(f"✅ Análisis completado y entrada registrada para {unique_filename}.")

    # --- Construyendo la respuesta final para la aplicación móvil (ResultActivity) ---
    # Esta es la estructura que tu ResultActivity espera del Intent (FoodResult)
    response_data = {
        "nombre": nombre_general_comida,  # Nombre del plato para el resumen
        "calorias": total_calorias,
        "proteinas": total_proteinas,
        "grasas": total_grasas,
        "carbohidratos": total_carbohidratos,
        "alimentos_detallados": response_foods_for_app  # Lista de items para la vista detallada
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
            serialized_entry = entry.copy()  # Crea una copia mutable

            # Convertir ObjectId a string
            if '_id' in serialized_entry:
                serialized_entry['_id'] = str(serialized_entry['_id'])

            # Convertir datetime a ISO 8601 string
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


@app.route('/saludo', methods=['GET'])
def saludo():
    return jsonify({"mensaje": "¡Hola desde FoodScan Backend! La API está funcionando."}), 200


if __name__ == '__main__':
    print("🚀 Iniciando servidor Flask. Accede a http://127.0.0.1:5000/saludo para probar.")
    app.run(host='0.0.0.0', port=5000, debug=True)