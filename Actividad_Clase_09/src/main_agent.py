import time
import os
from src.config import MONITOR_INTERVAL_SECONDS, INPUT_DIR, PROCESSING_DIR, INFRACTIONS_DIR
from src.image_manager import ImageManager
from src.gemini_analyzer import GeminiAnalyzer
from src.data_logger import DataLogger

def start_monitoring():
    image_manager = ImageManager()
    gemini_analyzer = GeminiAnalyzer()
    data_logger = DataLogger()

    print(f"Monitoreando la carpeta de entrada: {INPUT_DIR}")
    print("Presiona Ctrl+C para detener el monitoreo.")

    try:
        while True:
            new_images = image_manager.get_new_images()
            if not new_images:
                time.sleep(MONITOR_INTERVAL_SECONDS)
                continue

            for image_name in new_images:
                image_path_in_processing = None
                infraction_logged_successfully = False  # Bandera para saber si la infracción fue registrada exitosamente

                try:
                    print(f"[{image_name}] Nueva imagen detectada. Moviendo a procesamiento...")
                    image_path_in_processing = image_manager.move_to_processing(image_name)

                    if image_path_in_processing:
                        print(f"[{image_name}] Analizando con Gemini...")
                        results = gemini_analyzer.analyze_image(image_path_in_processing)

                        if results:
                            print(f"[{image_name}] Infracción(es) detectada(s):")
                            # Itera sobre cada infracción detectada
                            for infraction in results:
                                print(
                                    f" - Tipo: {infraction.get('tipo_infraccion')}, Patente: {infraction.get('patente')}, Color: {infraction.get('color_vehiculo')}, Marca: {infraction.get('marca_vehiculo')}, Confianza: {infraction.get('confianza_infraccion'):.2f}"
                                )
                                # Intenta registrar la infracción.
                                # Si log_infraction devuelve True, al menos una infracción fue registrada
                                if data_logger.log_infraction(image_name, infraction):
                                    infraction_logged_successfully = True
                                else:
                                    # Si falla el registro, esto lo mostrará y no moverá a la carpeta de infracciones
                                    print(
                                        f"[{image_name}] ADVERTENCIA: Fallo al registrar la infracción en MongoDB para {infraction.get('tipo_infraccion')}."
                                    )

                            # Después de intentar registrar TODAS las infracciones:
                            if infraction_logged_successfully:
                                # Si al menos una infracción fue registrada, mover a infracciones_detectadas
                                image_manager.move_to_infractions(image_name)
                            else:
                                # Si se detectaron infracciones pero ninguna se pudo registrar, mover a errores
                                print(
                                    f"[{image_name}] ERROR: Se detectaron infracciones, pero ninguna pudo ser registrada en MongoDB. Moviendo a errores."
                                )
                                image_manager.move_to_error(image_name)
                        else:
                            print(f"[{image_name}] No se detectaron infracciones o no cumplen el umbral.")
                            image_manager.move_to_processed(image_name)
                    else:
                        print(f"[{image_name}] ERROR: No se pudo mover la imagen a procesamiento. Saltando.")
                except Exception as e:
                    # Este catch es para errores durante el análisis o movimiento, no de registro en MongoDB
                    print(f"Ocurrió un error inesperado al procesar {image_name}: {e}")
                    if image_path_in_processing and os.path.exists(image_path_in_processing):
                        image_manager.move_to_error(image_name)
                    else:
                        print(
                            f"[{image_name}] ERROR: No se pudo mover a errores, el archivo no existe o ya fue movido."
                        )
                time.sleep(MONITOR_INTERVAL_SECONDS)

    except KeyboardInterrupt:
        print("\nMonitoreo detenido por el usuario.")
    except Exception as e:
        print(f"Ocurrió un error inesperado en el bucle principal general:\n{e}")
        # Intenta mover la imagen actual a la carpeta de errores si es posible
        if 'image_name' in locals() and os.path.exists(os.path.join(PROCESSING_DIR, image_name)):
            image_manager.move_to_error(image_name)
        time.sleep(MONITOR_INTERVAL_SECONDS)
    finally:
        data_logger.close_connection()

if __name__ == "__main__":
    start_monitoring()