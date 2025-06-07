import time
from image_manager import ImageManager
from gemini_analyzer import GeminiAnalyzer
from data_logger import DataLogger
from config import MONITOR_INTERVAL_SECONDS, FOOD_SECTIONS
from pymongo import MongoClient
from config import MONGO_URI, MONGO_DB_NAME, MONGO_COLLECTION_NAME


def mostrar_menu():
    print("\n\U0001F371 Bienvenido a FoodScan")
    print("1) Agregar comida/alimento")
    print("2) Ver historial de comida")
    print("3) Cerrar programa")

def elegir_opcion_menu():
    while True:
        opcion = input("\nSeleccione una opción (1/2/3): ").strip()
        if opcion in ["1", "2", "3"]:
            return opcion
        print("❌ Opcion invalida. Intente nuevamente.")

def elegir_seccion():
    print("\n⏰ Seleccione la sección de comida:")
    print("Opciones: " + ", ".join(FOOD_SECTIONS))
    while True:
        seccion = input("Ingrese sección (desayuno / almuerzo / once): ").strip().lower()
        if seccion in FOOD_SECTIONS:
            return seccion
        print("❌ Sección inválida. Intente nuevamente.")

def agregar_comidas(seccion):
    image_manager = ImageManager()
    analyzer = GeminiAnalyzer()
    logger = DataLogger()

    nuevos_alimentos = []

    print(f"\n🍒 Procesando imágenes para: {seccion.capitalize()}...")

    while True:
        images = image_manager.get_new_images()

        if not images:
            break

        for image_name in images:
            path = image_manager.move_to_processing(image_name)
            if not path:
                continue

            alimentos = analyzer.analyze_image(path)
            if alimentos:
                logger.log_meal(image_name, seccion, alimentos)
                image_manager.move_to_processed(image_name)
                nuevos_alimentos.extend([a['alimento'] for a in alimentos])
            else:
                image_manager.move_to_error(image_name)

    logger.close_connection()

    print("\n✅ Se agregaron los alimentos exitosamente.")
    if nuevos_alimentos:
        print(f"Alimentos agregados a {seccion}: " + ", ".join(nuevos_alimentos))
    else:
        print("No se detectaron alimentos en las imágenes proporcionadas.")

    time.sleep(5)


def ver_historial():
    client = MongoClient(MONGO_URI)
    db = client[MONGO_DB_NAME]
    collection = db[MONGO_COLLECTION_NAME]

    print("\n📓 Historial de comidas por sección:")

    for seccion in FOOD_SECTIONS:
        registros = list(collection.find({"seccion": seccion}))
        if not registros:
            print(f"\n{seccion.capitalize()}: No se ha agregado ningún alimento.")
        else:
            print(f"\n{seccion.capitalize()}:")
            for r in registros:
                alimentos = r.get("alimentos", [])
                nombres = [a['alimento'] for a in alimentos]
                print(" - " + ", ".join(nombres))
                for a in alimentos:
                    print(f"    • {a['alimento']}: {a['calorias']} kcal, {a['proteinas']}g prot, {a['grasas']}g grasa, {a['carbohidratos']}g carb")

    while True:
        volver = input("\n⟳ ¿Desea volver al menú? (si / no): ").strip().lower()
        if volver == "si":
            return
        elif volver == "no":
            print("Por favor, escriba 'si' para volver al menú.")
        else:
            print("Entrada no válida. Intente con 'si' o 'no'.")

def main():
    while True:
        mostrar_menu()
        opcion = elegir_opcion_menu()

        if opcion == "1":
            seccion = elegir_seccion()
            agregar_comidas(seccion)
        elif opcion == "2":
            ver_historial()
        elif opcion == "3":
            print("\n❌ Cerrando FoodScan. Hasta luego! \U0001F44B")
            break

if __name__ == "__main__":
    main()
