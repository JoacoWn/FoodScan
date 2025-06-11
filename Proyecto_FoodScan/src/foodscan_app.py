import time
import os
import shutil
from datetime import datetime, timedelta
from bson.objectid import ObjectId

from image_manager import ImageManager
from gemini_analyzer import GeminiAnalyzer
from data_logger import DataLogger
from config import MONITOR_INTERVAL_SECONDS, FOOD_SECTIONS
from food_database import FOOD_DATABASE  # ¡Importar solo el diccionario!


# --- Funciones para manejar la base de datos de alimentos (ahora aquí en foodscan_app.py) ---
def normalize_food_name(name):
    """Normaliza un nombre de alimento para facilitar la búsqueda."""
    return name.lower().strip()


def get_food_data_from_db(food_name):
    """
    Busca un alimento en FOOD_DATABASE y devuelve sus datos nutricionales.
    Intenta una coincidencia exacta normalizada y luego una parcial.
    """
    normalized_name = normalize_food_name(food_name)

    # Intenta una coincidencia exacta o normalizada primero
    if normalized_name in FOOD_DATABASE:
        return FOOD_DATABASE[normalized_name]

    # Si no hay coincidencia exacta, intenta buscar una coincidencia parcial o por palabras clave
    for db_food_name, db_data in FOOD_DATABASE.items():
        if normalized_name in normalize_food_name(db_food_name) or normalize_food_name(db_food_name) in normalized_name:
            # print(f"DEBUG: Coincidencia parcial: '{food_name}' -> '{db_food_name}'") # Puedes descomentar para depurar
            return db_data
    return None


# --- Fin de las funciones de la base de datos de alimentos ---


def mostrar_menu():
    """Muestra el menú principal de opciones al usuario."""
    print("\n--- FoodScan - Sistema de Registro Nutricional ---")
    print("1) Agregar comida/alimento")
    print("2) Ver historial de comida y resumen nutricional")
    print("3) Eliminar comida del historial")
    print("4) Salir")


def elegir_opcion_menu():
    """Solicita al usuario que elija una opción del menú y valida la entrada."""
    while True:
        opcion = input("Seleccione una opción: ").strip()
        if opcion in ["1", "2", "3", "4"]:
            return opcion
        else:
            print("X Opción inválida. Por favor, seleccione un número del 1 al 4.")


def elegir_seccion():
    """
    Solicita al usuario que elija una sección de comida y normaliza la entrada.
    """
    seccion_map = {
        "desayuno": "desayuno",
        "d": "desayuno",
        "almuerzo": "almuerzo",
        "a": "almuerzo",
        "once": "once",
        "cena": "once",  # 'cena' se mapea a 'once'
        "o": "once",
        "c": "once"
    }

    while True:
        seccion = input(f"Seleccione la sección de la comida ({'/'.join(FOOD_SECTIONS)}): ").strip().lower()
        if seccion in seccion_map:
            return seccion_map[seccion]
        else:
            print("X Sección inválida. Intente de nuevo con 'desayuno', 'almuerzo' o 'once'/'cena'.")


def _recalculate_meal_totals(analysis_result):
    """
    Recalcula los totales nutricionales (calorías, proteínas, grasas, carbohidratos)
    para una comida, basándose en las cantidades ajustadas por el usuario.
    Modifica el diccionario analysis_result en su lugar.
    """
    if not analysis_result.get("alimentos"):
        analysis_result["resumen_general"] = "No hay alimentos en esta comida."
        analysis_result["calorias_totales"] = 0.0
        analysis_result["proteinas_totales"] = 0.0
        analysis_result["grasas_totales"] = 0.0
        analysis_result["carbohidratos_totales"] = 0.0
        return

    total_calorias = 0.0
    total_proteinas = 0.0
    total_grasas = 0.0
    total_carbohidratos = 0.0

    # Recalcular los valores individuales de cada alimento en el análisis
    for item in analysis_result["alimentos"]:
        cantidad_usuario_g = item.get("cantidad_usuario_g", item.get("cantidad_original_g",
                                                                     0))  # Usar cantidad_original_g si no hay cantidad_usuario_g

        # Asegurarse de que nutrientes_por_100g existe y no es nulo
        if not item.get("nutrientes_por_100g"):
            item["nutrientes_por_100g"] = {
                "calorias": 0.0, "proteinas": 0.0, "grasas": 0.0, "carbohidratos": 0.0
            }

        factor_cantidad = cantidad_usuario_g / 100.0 if cantidad_usuario_g > 0 else 0.0

        item["calorias_totales_calculadas"] = round(item["nutrientes_por_100g"].get("calorias", 0.0) * factor_cantidad,
                                                    2)
        item["proteinas_totales_calculadas"] = round(
            item["nutrientes_por_100g"].get("proteinas", 0.0) * factor_cantidad, 2)
        item["grasas_totales_calculadas"] = round(item["nutrientes_por_100g"].get("grasas", 0.0) * factor_cantidad, 2)
        item["carbohidratos_totales_calculadas"] = round(
            item["nutrientes_por_100g"].get("carbohidratos", 0.0) * factor_cantidad, 2)

        total_calorias += item["calorias_totales_calculadas"]
        total_proteinas += item["proteinas_totales_calculadas"]
        total_grasas += item["grasas_totales_calculadas"]
        total_carbohidratos += item["carbohidratos_totales_calculadas"]

    analysis_result["calorias_totales"] = round(total_calorias, 2)
    analysis_result["proteinas_totales"] = round(total_proteinas, 2)
    analysis_result["grasas_totales"] = round(total_grasas, 2)
    analysis_result["carbohidratos_totales"] = round(total_carbohidratos, 2)
    analysis_result["resumen_general"] = (
        f"Calorías: {analysis_result['calorias_totales']} kcal, "
        f"Proteínas: {analysis_result['proteinas_totales']} g, "
        f"Grasas: {analysis_result['grasas_totales']} g, "
        f"Carbohidratos: {analysis_result['carbohidratos_totales']} g"
    )


def agregar_comidas(seccion):
    """
    Permite al usuario agregar comidas escaneando imágenes en 'input_images/'.
    """
    image_manager = ImageManager()
    analyzer = GeminiAnalyzer()  # Inicializa GeminiAnalyzer aquí
    logger = DataLogger()

    print(f"\n--- Agregando comida para: {seccion.capitalize()} ---")
    print("Coloca las imágenes de tu comida en la carpeta 'images/input_images/'.")
    print("Presiona Enter para escanear cuando estés listo, o escribe 'c' para cancelar.")

    while True:
        user_input = input("Esperando imágenes... (Enter para escanear / 'c' para cancelar): ").strip().lower()
        if user_input == 'c':
            print("Operación cancelada.")
            break

        new_images = image_manager.get_new_images()

        if not new_images:
            print(
                f"No se encontraron nuevas imágenes en '{image_manager.input_dir}'. Escaneando de nuevo en {MONITOR_INTERVAL_SECONDS} segundos...")
            time.sleep(MONITOR_INTERVAL_SECONDS)
            continue

        print(f"Se encontraron {len(new_images)} nueva(s) imagen(es). Procesando...")

        for image_name in new_images:
            path_in_processing = os.path.join(image_manager.processing_dir, image_name)

            print(f"\nProcesando imagen: {image_name}")

            if not image_manager.move_to_processing(image_name):
                print(f"Error al mover {image_name} a la carpeta de procesamiento. Saltando esta imagen.")
                continue

            # Llamar al analizador de Gemini
            gemini_raw_analysis = analyzer.analyze_image(path_in_processing)

            if not gemini_raw_analysis or not gemini_raw_analysis.get("alimentos"):
                print(f"No se pudo identificar alimentos en {image_name} o el análisis de Gemini falló.")
                print("Por favor, asegúrate de que la imagen sea clara y contenga alimentos reconocibles.")
                image_manager.move_to_error(image_name)
                print("Imagen movida a 'error_images'.")
                time.sleep(3)
                continue

            # --- LÓGICA DE PROCESAMIENTO DEL ANÁLISIS DE GEMINI Y MATCH CON DB ---
            final_processed_foods = []
            for item in gemini_raw_analysis["alimentos"]:
                nombre_gemini = item.get("nombre_alimento", "Desconocido").strip()
                cantidad_estimada_g = item.get("cantidad_estimada_g", 0)
                nutrientes_estimados_por_100g_gemini = item.get("nutrientes_estimados_por_100g_gemini", {})

                # Intentar buscar en la base de datos local (usando la función ahora local)
                matched_food_data = get_food_data_from_db(nombre_gemini)

                nutrientes_base_por_100g = {}
                nombre_final = nombre_gemini  # Por defecto, usa el nombre de Gemini

                if matched_food_data:
                    # Usar datos de nuestra base de datos local
                    nutrientes_base_por_100g = {
                        "calorias": matched_food_data.get("calorias_por_100g", 0.0),
                        "proteinas": matched_food_data.get("proteinas_por_100g", 0.0),
                        "grasas": matched_food_data.get("grasas_por_100g", 0.0),
                        "carbohidratos": matched_food_data.get("carbohidratos_por_100g", 0.0)
                    }
                    # Podrías actualizar nombre_final a un nombre 'oficial' si tu DB los tiene
                    # nombre_final = matched_food_data.get("nombre_oficial", nombre_gemini)
                else:
                    # Si no hay match en nuestra DB, usar las estimaciones de Gemini
                    print(
                        f"⚠️ No se encontró '{nombre_gemini}' en la base de datos local. Usando estimaciones de Gemini.")
                    nutrientes_base_por_100g = nutrientes_estimados_por_100g_gemini
                    nombre_final = nombre_gemini + " (Estimado)"  # Indica que es una estimación de Gemini

                # Ahora crea el formato que espera _recalculate_meal_totals
                final_processed_foods.append({
                    "nombre_alimento": nombre_final.title(),  # Capitaliza la primera letra para presentación
                    "cantidad_original_g": cantidad_estimada_g,  # Cantidad original estimada por Gemini
                    "cantidad_usuario_g": cantidad_estimada_g,  # Cantidad que el usuario puede ajustar
                    "nutrientes_por_100g": nutrientes_base_por_100g  # Base de 100g, sea de DB o Gemini
                })

            # Crear el diccionario analysis_result en el formato esperado por _recalculate_meal_totals
            analysis_result = {"alimentos": final_processed_foods}
            _recalculate_meal_totals(analysis_result)  # Calcula los totales iniciales

            # Mostrar análisis inicial
            print("\n--- Análisis Inicial de Gemini y Base de Datos ---")
            print(f"Resumen General: {analysis_result.get('resumen_general', 'N/A')}")
            print("Alimentos detectados:")
            if analysis_result.get("alimentos"):
                for i, item in enumerate(analysis_result["alimentos"]):
                    print(
                        f"  {i + 1}. {item.get('nombre_alimento', 'N/A')} (Cant. Est.: {item.get('cantidad_original_g', 'N/A')}g)")
                    # Mostramos los nutrientes por 100g que se usaron como base
                    if item.get("nutrientes_por_100g"):
                        print(
                            f"     Base (por 100g): Cals: {item['nutrientes_por_100g'].get('calorias', 0.0)}, Prot: {item['nutrientes_por_100g'].get('proteinas', 0.0)}, Gras: {item['nutrientes_por_100g'].get('grasas', 0.0)}, Carb: {item['nutrientes_por_100g'].get('carbohidratos', 0.0)}")
                    print(
                        f"     Calculado para {item.get('cantidad_original_g', 'N/A')}g: Cals: {item.get('calorias_totales_calculadas', 0.0)}, Prot: {item.get('proteinas_totales_calculadas', 0.0)}, Gras: {item.get('grasas_totales_calculadas', 0.0)}, Carb: {item.get('carbohidratos_totales_calculadas', 0.0)}")
            else:
                print("   (No se identificaron alimentos detallados)")

            # Permitir al usuario modificar cantidades o alimentos
            while True:
                modificar = input(
                    "\n¿Desea modificar las cantidades de los alimentos o eliminar alguno? (s/n): ").strip().lower()
                if modificar == 's':
                    if not analysis_result.get("alimentos"):
                        print("No hay alimentos para modificar.")
                        break  # Sale del bucle de modificación

                    while True:
                        print("\n--- Alimentos para Modificar ---")
                        for i, item in enumerate(analysis_result["alimentos"]):
                            cantidad_display = item.get("cantidad_usuario_g", item.get("cantidad_original_g", "N/A"))
                            print(
                                f"  {i + 1}. {item.get('nombre_alimento', 'N/A')} (Cantidad actual: {cantidad_display}g)")
                        print("  0. Terminar modificación y recalcular")
                        print("  -1. Eliminar un alimento")

                        try:
                            choice = int(input(
                                "Ingrese el número del alimento a modificar, '0' para terminar, o '-1' para eliminar: "))
                            if choice == 0:
                                _recalculate_meal_totals(analysis_result)
                                break
                            elif choice == -1:
                                if not analysis_result.get("alimentos"):
                                    print("No hay alimentos para eliminar.")
                                    continue
                                try:
                                    idx_eliminar = int(input("Ingrese el número del alimento a eliminar: ")) - 1
                                    if 0 <= idx_eliminar < len(analysis_result["alimentos"]):
                                        nombre_eliminado = analysis_result["alimentos"][idx_eliminar].get(
                                            "nombre_alimento", "Alimento")
                                        del analysis_result["alimentos"][idx_eliminar]
                                        _recalculate_meal_totals(analysis_result)
                                        print(f"'{nombre_eliminado}' eliminado. Totales recalculados.")
                                    else:
                                        print("Número de alimento inválido.")
                                except ValueError:
                                    print("Entrada inválida. Por favor, ingrese un número.")
                                continue  # Volver a mostrar las opciones de modificación/eliminación
                            elif 1 <= choice <= len(analysis_result["alimentos"]):
                                food_item = analysis_result["alimentos"][choice - 1]
                                try:
                                    new_quantity_input = input(
                                        f"Ingrese la nueva cantidad en gramos para '{food_item.get('nombre_alimento', 'N/A')}' (actual: {food_item.get('cantidad_usuario_g', food_item.get('cantidad_original_g', 'N/A'))}g) o 's' para omitir: ").strip().lower()
                                    if new_quantity_input == 's':
                                        print("Cantidad omitida.")
                                    else:
                                        new_quantity = float(new_quantity_input)
                                        if new_quantity > 0:
                                            food_item["cantidad_usuario_g"] = new_quantity
                                            print(
                                                f"Cantidad de '{food_item.get('nombre_alimento', 'N/A')}' actualizada a {new_quantity}g.")
                                            _recalculate_meal_totals(
                                                analysis_result)  # Recalcular después de cada cambio
                                        else:
                                            print("La cantidad debe ser un número positivo.")
                                except ValueError:
                                    print("Entrada inválida. Por favor, ingrese un número o 's'.")
                            else:
                                print("Número de alimento inválido.")
                        except ValueError:
                            print("Entrada inválida. Por favor, ingrese un número.")

                    # Después de terminar la modificación o si se eliminan todos los alimentos
                    if not analysis_result.get("alimentos"):
                        print("\nAdvertencia: No quedan alimentos en esta entrada después de las modificaciones.")
                        confirm_empty = input("¿Desea registrar esta entrada sin alimentos? (s/n): ").strip().lower()
                        if confirm_empty != 's':
                            print("Entrada descartada.")
                            image_manager.move_to_error(image_name)
                            break  # Sale del bucle de modificación de la comida actual

                    print("\n--- Análisis Final Actualizado ---")
                    print(f"Resumen General: {analysis_result.get('resumen_general', 'N/A')}")
                    print("Alimentos detallados:")
                    for i, item in enumerate(analysis_result["alimentos"]):
                        print(
                            f"  {i + 1}. {item.get('nombre_alimento', 'N/A')} (Cantidad ajustada: {item.get('cantidad_usuario_g', 'N/A')}g)")
                        print(
                            f"     Calculado: Cals: {item.get('calorias_totales_calculadas', 0.0)}, Prot: {item.get('proteinas_totales_calculadas', 0.0)}, Gras: {item.get('grasas_totales_calculadas', 0.0)}, Carb: {item.get('carbohidratos_totales_calculadas', 0.0)}")
                    break  # Sale del bucle de modificación
                elif modificar == 'n':
                    _recalculate_meal_totals(
                        analysis_result)  # Asegurarse de que los totales estén calculados incluso si no se modificó nada
                    if not analysis_result.get("alimentos"):
                        print("\nAdvertencia: La entrada no contiene alimentos identificados.")
                        confirm_empty = input("¿Desea registrar esta entrada sin alimentos? (s/n): ").strip().lower()
                        if confirm_empty != 's':
                            print("Entrada descartada.")
                            image_manager.move_to_error(image_name)
                            break  # Sale del bucle de modificación de la comida actual
                    print("\n--- Análisis Final Confirmado ---")
                    print(f"Resumen General: {analysis_result.get('resumen_general', 'N/A')}")
                    print("Alimentos detallados:")
                    for i, item in enumerate(analysis_result["alimentos"]):
                        print(
                            f"  {i + 1}. {item.get('nombre_alimento', 'N/A')} (Cantidad estimada: {item.get('cantidad_original_g', 'N/A')}g)")
                        print(
                            f"     Calculado: Cals: {item.get('calorias_totales_calculadas', 0.0)}, Prot: {item.get('proteinas_totales_calculadas', 0.0)}, Gras: {item.get('grasas_totales_calculadas', 0.0)}, Carb: {item.get('carbohidratos_totales_calculadas', 0.0)}")
                    break  # Sale del bucle de modificación
                else:
                    print("X Opción inválida. Por favor, ingrese 's' o 'n'.")

            # Preguntar si desea confirmar y registrar
            if analysis_result.get("alimentos") or input(
                    "\n¿Confirmar y registrar esta entrada vacía? (s/n): ").strip().lower() == 's':
                if logger.log_food_entry(analysis_result, image_name, seccion):
                    image_manager.move_to_processed(image_name)
                    print("Entrada de comida registrada y imagen movida a 'processed_images'.")
                else:
                    image_manager.move_to_error(image_name)
                    print("Error al registrar la entrada. Imagen movida a 'error_images'.")
            else:
                print("Registro cancelado por el usuario.")
                image_manager.move_to_error(image_name)
                print("Imagen movida a 'error_images'.")

            time.sleep(3)  # Pausa para que el usuario pueda leer los mensajes

        # Después de procesar todas las imágenes encontradas, preguntar si quiere seguir escaneando
        if not new_images:
            user_continue = input("No hay más imágenes nuevas. ¿Desea seguir escaneando? (s/n): ").strip().lower()
            if user_continue == 'n':
                break
            else:
                print(f"Continuando el escaneo en {MONITOR_INTERVAL_SECONDS} segundos...")
                time.sleep(MONITOR_INTERVAL_SECONDS)
        else:
            print("\nProcesamiento de imágenes completado.")
            break  # Salir después de procesar el lote actual de imágenes


def ver_historial():
    """
    Permite al usuario ver el historial de comidas y resúmenes nutricionales.
    """
    logger = DataLogger()

    while True:
        print("\n--- Historial de Comida y Resumen Nutricional ---")
        print("1) Ver historial completo")
        print("2) Filtrar historial por fecha y tipo de comida")
        print("3) Ver resumen nutricional diario")
        print("4) Volver al menú principal")

        historial_opcion = input("Seleccione una opción: ").strip()

        if historial_opcion == "1":
            _mostrar_historial_detallado(logger)
        elif historial_opcion == "2":
            _filtrar_historial_por_fecha(logger)
        elif historial_opcion == "3":
            _mostrar_resumen_diario(logger)
        elif historial_opcion == "4":
            logger.close_connection()
            break
        else:
            print("X Opción inválida. Intente nuevamente.")


def _mostrar_historial_detallado(logger):
    """
    Muestra todas las entradas de comida registradas en detalle.
    """
    entries = logger.get_food_entries()
    if not entries:
        print("\nNo hay entradas de comida en el historial.")
        return

    print("\n--- Historial de Comida Detallado ---")
    current_date = None
    for entry in entries:
        entry_date = entry["timestamp"].date()
        if entry_date != current_date:
            print(f"\n--- Fecha: {entry_date.strftime('%Y-%m-%d')} ---")
            current_date = entry_date

        print(f"\n  ID de Entrada: {entry['_id']}")
        print(f"  Sección: {entry.get('meal_type', 'N/A').capitalize()}")
        print(f"  Hora: {entry['timestamp'].strftime('%H:%M:%S')}")
        print(f"  Imagen: {entry.get('image_name', 'N/A')}")

        print("  Alimentos:")
        if entry.get("alimentos"):
            for i, food_item in enumerate(entry["alimentos"]):
                print(f"    {i + 1}. {food_item.get('nombre_alimento', 'N/A')}")
                cantidad_display = food_item.get("cantidad_usuario_g", food_item.get("cantidad_original_g", "N/A"))
                print(f"       Cantidad: {cantidad_display}g")

                # Mostrar nutrientes calculados individuales si están disponibles
                if "calorias_totales_calculadas" in food_item:
                    print(
                        f"       Nutrientes (calculados): Cals: {food_item.get('calorias_totales_calculadas', 0.0)}, Prot: {food_item.get('proteinas_totales_calculadas', 0.0)}, Gras: {food_item.get('grasas_totales_calculadas', 0.0)}, Carb: {food_item.get('carbohidratos_totales_calculadas', 0.0)}")
                elif food_item.get("nutrientes_por_100g"):
                    # Fallback si no están los calculados directamente
                    print(
                        f"       Nutrientes (por 100g): Cals: {food_item['nutrientes_por_100g'].get('calorias', 0.0)}, Prot: {food_item['nutrientes_por_100g'].get('proteinas', 0.0)}, Gras: {food_item['nutrientes_por_100g'].get('grasas', 0.0)}, Carb: {food_item['nutrientes_por_100g'].get('carbohidratos', 0.0)}")
        else:
            print("    (No se detallaron alimentos para esta entrada)")

        # Mostrar resumen nutricional total de la comida
        print(f"  --- Resumen Nutricional de la Comida ---")
        print(f"  Calorías Totales: {entry.get('calorias_totales_comida', 0.0)} kcal")
        print(f"  Proteínas Totales: {entry.get('proteinas_totales_comida', 0.0)} g")
        print(f"  Grasas Totales: {entry.get('grasas_totales_comida', 0.0)} g")
        print(f"  Carbohidratos Totales: {entry.get('carbohidratos_totales_comida', 0.0)} g")
        print("-" * 40)


def _filtrar_historial_por_fecha(logger):
    """
    Permite al usuario filtrar el historial por fecha y tipo de comida.
    """
    while True:
        try:
            fecha_str = input(
                "Ingrese la fecha (YYYY-MM-DD) para filtrar (deje en blanco para no filtrar por fecha): ").strip()
            start_date = None
            end_date = None
            if fecha_str:
                start_date = datetime.strptime(fecha_str, "%Y-%m-%d")
                end_date = start_date + timedelta(days=1) - timedelta(microseconds=1)  # Fin del día
            break
        except ValueError:
            print("X Formato de fecha inválido. Use YYYY-MM-DD.")
            print("Por favor, ingrese una fecha válida en formato YYYY-MM-DD.")

    while True:
        meal_type_input = input(
            f"Ingrese la sección de comida ({'/'.join(FOOD_SECTIONS)}, deje en blanco para todas): ").strip().lower()
        meal_type = None
        if meal_type_input:
            seccion_map = {
                "desayuno": "desayuno",
                "d": "desayuno",
                "almuerzo": "almuerzo",
                "a": "almuerzo",
                "once": "once",
                "cena": "once",
                "o": "once",
                "c": "once"
            }
            if meal_type_input in seccion_map:
                meal_type = seccion_map[meal_type_input]
            else:
                print("X Sección de comida inválida. Intente de nuevo.")
                continue
        break

    entries = logger.get_food_entries(start_date=start_date, end_date=end_date, meal_type=meal_type)
    if not entries:
        print("\nNo se encontraron entradas para los filtros seleccionados.")
        return

    print("\n--- Historial Filtrado ---")
    current_date = None
    for entry in entries:
        entry_date = entry["timestamp"].date()
        if entry_date != current_date:
            print(f"\n--- Fecha: {entry_date.strftime('%Y-%m-%d')} ---")
            current_date = entry_date

        print(f"\n  ID de Entrada: {entry['_id']}")
        print(f"  Sección: {entry.get('meal_type', 'N/A').capitalize()}")
        print(f"  Hora: {entry['timestamp'].strftime('%H:%M:%S')}")
        print(f"  Imagen: {entry.get('image_name', 'N/A')}")
        print("  Alimentos:")
        if entry.get("alimentos"):
            for i, food_item in enumerate(entry["alimentos"]):
                print(
                    f"    {i + 1}. {food_item.get('nombre_alimento', 'N/A')} (Cantidad: {food_item.get('cantidad_usuario_g', food_item.get('cantidad_original_g', 'N/A'))}g)")
        else:
            print("    (No se detallaron alimentos para esta entrada)")

        print(f"  Calorías Totales: {entry.get('calorias_totales_comida', 0.0)} kcal")
        print(f"  Proteínas Totales: {entry.get('proteinas_totales_comida', 0.0)} g")
        print(f"  Grasas Totales: {entry.get('grasas_totales_comida', 0.0)} g")
        print(f"  Carbohidratos Totales: {entry.get('carbohidratos_totales_comida', 0.0)} g")
        print("-" * 40)


def _mostrar_resumen_diario(logger):
    """
    Muestra un resumen nutricional diario.
    """
    while True:
        try:
            fecha_str = input("Ingrese la fecha (YYYY-MM-DD) para el resumen (deje en blanco para hoy): ").strip()
            if fecha_str:
                target_date = datetime.strptime(fecha_str, "%Y-%m-%d")
            else:
                target_date = datetime.now()
            break
        except ValueError:
            print("X Formato de fecha inválido. Use YYYY-MM-DD.")
            print("Por favor, ingrese una fecha válida en formato YYYY-MM-DD.")

    summary = logger.get_summary_by_date(target_date)

    if summary:
        print(f"\n--- Resumen Nutricional para {summary['date']} ---")
        print(f"Calorías Totales: {summary['total_calorias']} kcal")
        print(f"Proteínas Totales: {summary['total_proteinas']} g")
        print(f"Grasas Totales: {summary['total_grasas']} g")
        print(f"Carbohidratos Totales: {summary['total_carbohidratos']} g")
    else:
        print(f"No hay datos nutricionales para la fecha {target_date.strftime('%Y-%m-%d')}.")


def eliminar_comida():
    """
    Permite al usuario eliminar una entrada de comida del historial por su ID.
    """
    logger = DataLogger()
    print("\n--- Eliminar Comida del Historial ---")
    print("Para eliminar una comida, necesitarás su ID de Entrada.")
    print("Puedes encontrar los IDs viendo el 'Historial de Comida Detallado'.")

    entry_id_str = input("Ingrese el ID de la entrada a eliminar: ").strip()

    try:
        # Intentar convertir a ObjectId, aunque el DataLogger ya lo maneja
        entry_id = ObjectId(entry_id_str)
        if logger.delete_food_entry(entry_id):
            print("Comida eliminada exitosamente.")
        else:
            print("No se pudo eliminar la comida. Asegúrate de que el ID sea correcto.")
    except Exception as e:
        print(f"Error: ID inválido o problema al eliminar. {e}")
    finally:
        logger.close_connection()


def main():
    """Función principal de la aplicación FoodScan."""
    while True:
        mostrar_menu()
        opcion = elegir_opcion_menu()

        if opcion == "1":
            seccion = elegir_seccion()
            agregar_comidas(seccion)
        elif opcion == "2":
            ver_historial()
        elif opcion == "3":
            eliminar_comida()
        elif opcion == "4":  # Cambiado a 4 para Salir
            print("Saliendo de FoodScan. ¡Hasta pronto!")
            break


if __name__ == "__main__":
    main()