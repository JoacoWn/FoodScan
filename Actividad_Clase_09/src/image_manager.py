import os
import shutil
from src.config import INPUT_DIR, PROCESSING_DIR, PROCESSED_DIR, INFRACTIONS_DIR, ERROR_DIR

class ImageManager:
    def __init__(self):
        self._ensure_directories_exist()

    def _ensure_directories_exist(self):
        """Asegura que todos los directorios necesarios existan."""
        for d in [INPUT_DIR, PROCESSING_DIR, PROCESSED_DIR, INFRACTIONS_DIR, ERROR_DIR]:
            os.makedirs(d, exist_ok=True)

    def get_new_images(self):
        """Obtiene una lista de imágenes en el directorio de entrada."""
        return [f for f in os.listdir(INPUT_DIR) if os.path.isfile(os.path.join(INPUT_DIR, f))]

    def move_to_processing(self, image_name):
        """Mueve una imagen del directorio de entrada al de procesamiento."""
        src_path = os.path.join(INPUT_DIR, image_name)
        dest_path = os.path.join(PROCESSING_DIR, image_name)
        try:
            shutil.move(src_path, dest_path)
            print(f"[{image_name}] Movida a procesamiento.")
            return dest_path
        except Exception as e:
            print(f"Error al mover {image_name} a procesamiento: {e}")
            return None

    def move_to_processed(self, image_name):
        """Mueve una imagen del directorio de procesamiento al de procesados."""
        src_path = os.path.join(PROCESSING_DIR, image_name)
        dest_path = os.path.join(PROCESSED_DIR, image_name)
        try:
            shutil.move(src_path, dest_path)
            print(f"[{image_name}] Movida a procesados.")
        except Exception as e:
            print(f"Error al mover {image_name} a procesados: {e}")

    def move_to_infractions(self, image_name):
        """Mueve una imagen del directorio de procesamiento al de infracciones."""
        src_path = os.path.join(PROCESSING_DIR, image_name)
        dest_path = os.path.join(INFRACTIONS_DIR, image_name)
        try:
            shutil.move(src_path, dest_path)
            print(f"[{image_name}] ¡Infracción detectada! Movida a infracciones.")
        except Exception as e:
            print(f"Error al mover {image_name} a infracciones: {e}")

    def move_to_error(self, image_name):
        """Mueve una imagen del directorio de procesamiento al de errores."""
        src_path = os.path.join(PROCESSING_DIR, image_name)
        dest_path = os.path.join(ERROR_DIR, image_name)
        try:
            shutil.move(src_path, dest_path)
            print(f"[{image_name}] Movida a errores (fallo en procesamiento).")
        except Exception as e:
            print(f"Error al mover {image_name} a errores: {e}")

