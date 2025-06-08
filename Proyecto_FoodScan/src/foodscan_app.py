import time
import os
from image_manager import ImageManager
from gemini_analyzer import GeminiAnalyzer
from data_logger import DataLogger
from config import MONITOR_INTERVAL_SECONDS, FOOD_SECTIONS, INITIAL_SCAN
from pymongo import MongoClient
from config import MONGO_URI, MONGO_DB_NAME, MONGO_COLLECTION_NAME
from datetime import datetime, timedelta
from bson.objectid import ObjectId

# Global para almacenar el usuario actual, para simular perfiles
current_user = None


def mostrar_menu():
    print(f"\n\U0001F371 Bienvenido a FoodScan (Usuario: {current_user if current_user else 'Invitado'})")
    print("1) Agregar comida/alimento")
    print("2) Ver historial de comida y resumen nutricional")
    print("3) Eliminar comida del historial")
    print("4) Configuración y Perfil de Usuario")  # Nueva opción de menú
    print("5) Cerrar programa")


def elegir_opcion_menu():
    while True:
        opcion = input("\nSeleccione una opción (1/2/3/4/5): ").strip()
        if opcion in ["1", "2", "3", "4", "5"]:
            return opcion
        print("X Opción inválida. Intente nuevamente.")


def elegir_seccion():
    print("\n Seleccione la sección de comida:")
    print("Opciones: ", ", ".join(FOOD_SECTIONS))
    while True:
        seccion = input("Ingrese sección (desayuno / almuerzo / once): ").strip().lower()
        if seccion in FOOD_SECTIONS:
            return seccion
        print("X Sección inválida. Intente nuevamente.")


def agregar_comidas(seccion):
    image_manager = ImageManager()
    analyzer = GeminiAnalyzer()
    logger = DataLogger()

    nuevos_alimentos = []

    print(f"\n Procesando imágenes para: {seccion.capitalize()}...")
    print("Coloque las imágenes en la carpeta 'input_images/' y presione Enter para continuar.")
    print("Para cancelar, presione 'c' y luego Enter.")

    while True:
        user_input = input("Presione Enter para escanear nuevas imágenes o 'c' para cancelar: ").strip().lower()
        if user_input == 'c':
            print("Operación de agregar comida cancelada.")
            break

        images = image_manager.get_new_images()
        if not images:
            print("No se encontraron nuevas imágenes en la carpeta 'input_images/'.")
            continue

        for i, image_name in enumerate(images):
            print(f"[{i + 1}/{len(images)}] Procesando {image_name}...")
            path = image_manager.move_to_processing(image_name)

            if not path:
                print(f"X No se pudo mover {image_name} para procesamiento. Saltando...")
                continue

            print(f" Analizando {image_name} con IA...")
            alimentos = analyzer.analyze_image(path)

            if alimentos:
                print(f" Comida detectada en {image_name}: {', '.join([a['alimento'] for a in alimentos])}")
                if logger.log_meal(image_name, seccion, alimentos, current_user):  # Pasa el usuario actual
                    image_manager.move_to_processed(image_name)
                    nuevos_alimentos.extend([a['alimento'] for a in alimentos])
                else:
                    image_manager.move_to_error(image_name)
            else:
                print(f" No se detectaron alimentos o hubo un error en {image_name}. Moviendo a errores.")
                image_manager.move_to_error(image_name)

        if not images:
            print("No se encontraron más imágenes nuevas. Finalizando proceso de agregar comida.")
            break
        else:
            print("Escaneo completado. Buscando más imágenes...")

    logger.close_connection()
    if nuevos_alimentos:
        print(f"\nSe agregaron los siguientes alimentos a {seccion}: {', '.join(nuevos_alimentos)}")
    else:
        print("\nNo se detectaron alimentos en las imágenes proporcionadas o la operación fue cancelada.")
    time.sleep(2)


def ver_historial():
    client = MongoClient(MONGO_URI)
    db = client[MONGO_DB_NAME]
    collection = db[MONGO_COLLECTION_NAME]

    query_filter = {"user": current_user} if current_user else {}  # Filtrar por usuario si hay uno

    while True:
        print(f"\n--- Opciones de Historial (Usuario: {current_user if current_user else 'Invitado'}) ---")
        print("1) Ver historial completo")
        print("2) Filtrar por fecha")
        print("3) Ver resumen diario de calorías y macronutrientes")
        print("4) Volver al menú principal")

        hist_opcion = input("Seleccione una opción: ").strip()

        if hist_opcion == "1":
            _mostrar_historial_detallado(collection, query_filter)
        elif hist_opcion == "2":
            _filtrar_historial_por_fecha(collection, query_filter)
        elif hist_opcion == "3":
            _mostrar_resumen_diario(collection, query_filter)
        elif hist_opcion == "4":
            break
        else:
            print("X Opción inválida. Intente nuevamente.")

    client.close()


def _mostrar_historial_detallado(collection, query_filter):
    print("\n Historial de comidas por sección:")

    total_proteinas_cal = 0
    total_grasas_cal = 0
    total_carbohidratos_cal = 0

    all_records = list(collection.find(query_filter).sort("timestamp", -1))

    if not all_records:
        print("No se ha agregado ningún alimento aún para este usuario.")
        return

    for r in all_records:
        alimentos = r.get("alimentos", [])
        for a in alimentos:
            total_proteinas_cal += a.get('proteinas', 0) * 4
            total_grasas_cal += a.get('grasas', 0) * 9
            total_carbohidratos_cal += a.get('carbohidratos', 0) * 4

    print("\n--- Historial Detallado ---")
    current_date = None
    for r in all_records:
        record_date = r['timestamp'].strftime('%Y-%m-%d')
        if record_date != current_date:
            print(f"\n--- {record_date} ---")
            current_date = record_date

        alimentos = r.get("alimentos", [])
        nombres = [a['alimento'] for a in alimentos]
        print(
            f"- {r['seccion'].capitalize()} ({r['timestamp'].strftime('%H:%M')}): {', '.join(nombres)} [ID: {str(r['_id'])}]")
        for a in alimentos:
            print(
                f"    - {a['alimento']}: {a['calorias']} kcal, {a['proteinas']} g prot, {a['grasas']} g grasa, {a['carbohidratos']} g carb")

    _mostrar_resumen_nutricional_global(total_proteinas_cal, total_grasas_cal, total_carbohidratos_cal)


def _filtrar_historial_por_fecha(collection, query_filter):
    while True:
        fecha_str = input("\nIngrese la fecha a filtrar (YYYY-MM-DD) o 'c' para cancelar: ").strip()
        if fecha_str.lower() == 'c':
            return
        try:
            fecha_obj = datetime.strptime(fecha_str, '%Y-%m-%d')
            start_of_day = fecha_obj
            end_of_day = fecha_obj + timedelta(days=1)

            # Combinar el filtro de usuario con el filtro de fecha
            date_filter = {"timestamp": {"$gte": start_of_day, "$lt": end_of_day}}
            combined_filter = {**query_filter, **date_filter}

            registros_filtrados = list(collection.find(combined_filter).sort("timestamp", 1))

            if not registros_filtrados:
                print(f"No se encontraron registros para la fecha {fecha_str} para este usuario.")
            else:
                print(
                    f"\n--- Historial para el {fecha_str} (Usuario: {current_user if current_user else 'Invitado'}) ---")
                daily_proteinas_cal = 0
                daily_grasas_cal = 0
                daily_carbohidratos_cal = 0

                for r in registros_filtrados:
                    alimentos = r.get("alimentos", [])
                    nombres = [a['alimento'] for a in alimentos]
                    print(
                        f"- {r['seccion'].capitalize()} ({r['timestamp'].strftime('%H:%M')}): {', '.join(nombres)} [ID: {str(r['_id'])}]")
                    for a in alimentos:
                        print(
                            f"    - {a['alimento']}: {a['calorias']} kcal, {a['proteinas']} g prot, {a['grasas']} g grasa, {a['carbohidratos']} g carb")
                        daily_proteinas_cal += a.get('proteinas', 0) * 4
                        daily_grasas_cal += a.get('grasas', 0) * 9
                        daily_carbohidratos_cal += a.get('carbohidratos', 0) * 4

                print(
                    f"\n--- Resumen Nutricional para el {fecha_str} (Usuario: {current_user if current_user else 'Invitado'}) ---")
                _mostrar_resumen_nutricional_global(daily_proteinas_cal, daily_grasas_cal, daily_carbohidratos_cal)
            break
        except ValueError:
            print("Formato de fecha inválido. Por favor, use YYYY-MM-DD.")


def _mostrar_resumen_diario(collection, query_filter):
    print("\n--- Resumen Diario de Calorías y Macronutrientes ---")
    registros = list(collection.find(query_filter).sort("timestamp", 1))

    if not registros:
        print("No hay registros para generar un resumen diario para este usuario.")
        return

    daily_data = {}

    for r in registros:
        record_date = r['timestamp'].strftime('%Y-%m-%d')
        if record_date not in daily_data:
            daily_data[record_date] = {'proteinas_cal': 0, 'grasas_cal': 0, 'carbohidratos_cal': 0}

        alimentos = r.get("alimentos", [])
        for a in alimentos:
            daily_data[record_date]['proteinas_cal'] += a.get('proteinas', 0) * 4
            daily_data[record_date]['grasas_cal'] += a.get('grasas', 0) * 9
            daily_data[record_date]['carbohidratos_cal'] += a.get('carbohidratos', 0) * 4

    for date, data in daily_data.items():
        print(f"\n--- Resumen para el {date} (Usuario: {current_user if current_user else 'Invitado'}) ---")
        _mostrar_resumen_nutricional_global(data['proteinas_cal'], data['grasas_cal'], data['carbohidratos_cal'])


def _mostrar_resumen_nutricional_global(total_proteinas_cal, total_grasas_cal, total_carbohidratos_cal):
    total_calorias_macronutrientes = total_proteinas_cal + total_grasas_cal + total_carbohidratos_cal

    if total_calorias_macronutrientes > 0:
        prot_perc = (total_proteinas_cal / total_calorias_macronutrientes) * 100
        gras_perc = (total_grasas_cal / total_calorias_macronutrientes) * 100
        carb_perc = (total_carbohidratos_cal / total_calorias_macronutrientes) * 100

        print(f"Total Calorías: {int(total_calorias_macronutrientes)} kcal")
        print(f"Proteínas:   {int(total_proteinas_cal)} kcal ({prot_perc:.1f}%)")
        print(f"Grasas:      {int(total_grasas_cal)} kcal ({gras_perc:.1f}%)")
        print(f"Carbs:       {int(total_carbohidratos_cal)} kcal ({carb_perc:.1f}%)")

        print("\nRepresentación Gráfica (Basada en Carga Calórica):")
        bar_length = 50
        prot_bar = int(bar_length * (prot_perc / 100))
        gras_bar = int(bar_length * (gras_perc / 100))
        carb_bar = int(bar_length * (carb_perc / 100))

        remaining = bar_length - (prot_bar + gras_bar + carb_bar)
        if remaining > 0:
            if prot_bar >= gras_bar and prot_bar >= carb_bar:
                prot_bar += remaining
            elif gras_bar >= prot_bar and gras_bar >= carb_bar:
                gras_bar += remaining
            else:
                carb_bar += remaining

        print(f"Proteínas:   [{'█' * prot_bar}{' ' * (bar_length - prot_bar)}]")
        print(f"Grasas:      [{'█' * gras_bar}{' ' * (bar_length - gras_bar)}]")
        print(f"Carbs:       [{'█' * carb_bar}{' ' * (bar_length - carb_bar)}]")
    else:
        print("No hay suficientes datos para generar un resumen nutricional.")


def eliminar_comida():
    logger = DataLogger()
    client = MongoClient(MONGO_URI)
    db = client[MONGO_DB_NAME]
    collection = db[MONGO_COLLECTION_NAME]

    print("\n--- Eliminar Comida del Historial ---")
    query_filter = {"user": current_user} if current_user else {}
    registros = list(collection.find(query_filter))
    if not registros:
        print("No hay comidas registradas para eliminar para este usuario.")
        logger.close_connection()
        return

    print("Lista de comidas registradas:")
    for i, r in enumerate(registros):
        alimentos_str = ", ".join([a['alimento'] for a in r.get("alimentos", [])])
        print(
            f"{i + 1}) Fecha: {r['timestamp'].strftime('%Y-%m-%d %H:%M')}, Sección: {r['seccion']}, Alimentos: {alimentos_str} (ID: {str(r['_id'])})")

    while True:
        try:
            opcion = input("Ingrese el número de la comida a eliminar (o '0' para cancelar): ").strip()
            if opcion == '0':
                print("Operación de eliminación cancelada.")
                break

            idx = int(opcion) - 1
            if 0 <= idx < len(registros):
                comida_a_eliminar = registros[idx]
                confirmacion = input(
                    f"¿Está seguro de eliminar '{', '.join([a['alimento'] for a in comida_a_eliminar.get('alimentos', [])])}' de {comida_a_eliminar['seccion']}? (si/no): ").strip().lower()
                if confirmacion == 'si':
                    if logger.delete_meal(comida_a_eliminar['_id']):
                        print("Comida eliminada exitosamente.")
                    else:
                        print("X Error al intentar eliminar la comida.")
                else:
                    print("Eliminación cancelada.")
                break
            else:
                print("Número de opción inválido. Intente de nuevo.")
        except ValueError:
            print("Entrada no válida. Por favor, ingrese un número.")
    logger.close_connection()


def configuracion_y_perfil():
    global current_user
    while True:
        print("\n--- Configuración y Perfil de Usuario ---")
        print(f"Usuario actual: {current_user if current_user else 'Invitado (sin perfil)'}")
        print("1) Cambiar/Crear Perfil de Usuario")
        print("2) Volver al menú principal")

        config_opcion = input("Seleccione una opción: ").strip()

        if config_opcion == "1":
            nuevo_usuario = input("Ingrese el nombre de usuario (dejar vacío para 'Invitado' o cancelar): ").strip()
            if nuevo_usuario:
                current_user = nuevo_usuario
                print(f"Perfil cambiado a: {current_user}")
            else:
                current_user = None
                print("Se ha vuelto al perfil 'Invitado'.")
        elif config_opcion == "2":
            break
        else:
            print("X Opción inválida. Intente nuevamente.")


def run_tutorial():
    print("\n--- ¡Bienvenido a FoodScan! Tutorial Rápido ---")
    print("Este programa te ayuda a registrar tus comidas y ver su información nutricional.")
    print("\n1. ¿Cómo agregar una comida?")
    print("   - Ve a la opción '1) Agregar comida/alimento' en el menú principal.")
    print("   - Coloca la imagen de tu comida en la carpeta 'input_images/' antes de continuar.")
    print("   - El sistema escaneará la carpeta y analizará las imágenes para identificar los alimentos.")
    print("   - La información nutricional se guardará automáticamente.")
    print("\n2. ¿Cómo ver tu historial?")
    print("   - Ve a la opción '2) Ver historial de comida y resumen nutricional'.")
    print("   - Podrás ver todas tus comidas, filtrar por fecha o ver un resumen diario de calorías y macronutrientes.")
    print("\n3. ¿Cómo eliminar una comida?")
    print("   - Si necesitas corregir algo, selecciona la opción '3) Eliminar comida del historial'.")
    print("   - Se te pedirá el número de la comida que deseas eliminar.")
    print("\n4. ¿Perfiles de Usuario?")
    print("   - En la opción '4) Configuración y Perfil de Usuario', puedes crear o cambiar tu perfil.")
    print("   - Esto te permite llevar un registro separado si varias personas usan el mismo programa.")
    print("\n¡Listo! Ahora estás preparado para usar FoodScan. ¡Disfruta!")
    input("\nPresiona Enter para volver al menú principal...")


def main():
    global current_user
    # Determinar si es la primera vez que se ejecuta el programa o si el usuario quiere ver el tutorial
    if not os.path.exists("foodscan_first_run.flag"):
        run_tutorial()
        with open("foodscan_first_run.flag", "w") as f:
            f.write("True")  # Crea un archivo para indicar que el tutorial ya se mostró
    else:
        # Preguntar si quiere ver el tutorial nuevamente
        while True:
            ver_tutorial_again = input("\n¿Quieres ver el tutorial rápido de nuevo? (si/no): ").strip().lower()
            if ver_tutorial_again == 'si':
                run_tutorial()
                break
            elif ver_tutorial_again == 'no':
                break
            else:
                print("Respuesta no válida. Por favor, ingresa 'si' o 'no'.")

    # Selección de usuario al inicio
    while True:
        user_choice = input("\nIngresa tu nombre de usuario (o presiona Enter para 'Invitado'): ").strip()
        if user_choice:
            current_user = user_choice
            print(f"Sesión iniciada como: {current_user}")
        else:
            current_user = None
            print("Sesión iniciada como: Invitado")
        break  # Siempre salir después de la primera elección

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
        elif opcion == "4":  # Nueva opción de configuración y perfil
            configuracion_y_perfil()
        elif opcion == "5":  # Se ajustó el número de cerrar
            print("\nX Cerrando FoodScan. ¡Hasta luego! \U0001F44B")
            break


if __name__ == "__main__":
    main()