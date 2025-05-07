from image_manager import ImageManager
from gemini_analyzer import GeminiAnalyzer
from data_logger import DataLogger
from config import MONITOR_INTERVAL_SECONDS, FOOD_SECTIONS
import time


def ask_section():
    print("🕐 ¿Qué sección estás registrando ahora?")
    print("Opciones válidas:", ", ".join(FOOD_SECTIONS))

    while True:
        section = input("👉 Ingrese la sección (desayuno / almuerzo / once): ").strip().lower()
        if section in FOOD_SECTIONS:
            return section
        print("❌ Sección inválida. Intente de nuevo.")


def start_monitoring(section):
    image_manager = ImageManager()
    gemini_analyzer = GeminiAnalyzer()
    data_logger = DataLogger()

    print(f"\n📂 Monitoreando carpeta: {image_manager.input_dir}")
    print(f"🍽️ Registrando sección de comida: {section}")
    print("🟢 Esperando nuevas imágenes... Ctrl+C para detener.\n")

    try:
        while True:
            images = image_manager.get_new_images()

            if not images:
                time.sleep(MONITOR_INTERVAL_SECONDS)
                continue

            for image_name in images:
                path = image_manager.move_to_processing(image_name)
                if not path:
                    continue

                print(f"🔎 Analizando {image_name}...")
                food_items = gemini_analyzer.analyze_image(path)

                if food_items:
                    success = data_logger.log_meal(image_name, section, food_items)
                    if success:
                        image_manager.move_to_processed(image_name)
                    else:
                        image_manager.move_to_error(image_name)
                else:
                    print(f"[{image_name}] ⚠️ No se detectaron alimentos o hubo error.")
                    image_manager.move_to_error(image_name)

    except KeyboardInterrupt:
        print("\n🛑 Monitoreo detenido por el usuario.")
    finally:
        data_logger.close_connection()


if __name__ == "__main__":
    selected_section = ask_section()
    start_monitoring(selected_section)
